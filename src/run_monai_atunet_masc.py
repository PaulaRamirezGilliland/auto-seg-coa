#!/usr/bin/python 
from __future__ import print_function 
import sys 
import os 
import tempfile 
import nibabel as nib 
from monai.transforms import (AddChanneld, Compose, LoadImaged, ScaleIntensityd, ToTensord,)
from monai.networks.nets import AttentionUnet, DenseNet121 
from monai.data import (DataLoader, CacheDataset, load_decathlon_datalist,)
import torch
from statistics import mode
import warnings
warnings.filterwarnings("ignore") 
warnings.simplefilter("ignore")

############################################################################################################# 
############################################################################################################# 

files_path = sys.argv[1] 
check_path = sys.argv[2] 
json_file = sys.argv[3] 
results_path = sys.argv[4] 
cl_num = int(sys.argv[5])


#############################################################################################################
#############################################################################################################

directory = os.environ.get("MONAI_DATA_DIRECTORY")
root_dir = tempfile.mkdtemp() if directory is None else directory

root_dir = files_path
os.chdir(root_dir)

run_transforms = Compose(
    [
        LoadImaged(keys=["image"]),
        AddChanneld(keys=["image"]),
        ScaleIntensityd(
            keys=["image"], minv=0.0, maxv=1.0
        ),
        ToTensord(keys=["image"]),
    ]
)

#############################################################################################################
#############################################################################################################


datasets = files_path + json_file
run_datalist = load_decathlon_datalist(datasets, True, "running")
run_ds = CacheDataset(
    data=run_datalist, transform=run_transforms,
    cache_num=100, cache_rate=1.0, num_workers=4,
)

run_loader = DataLoader(
    run_ds, batch_size=1, shuffle=False, num_workers=4, pin_memory=True
)

#############################################################################################################
#############################################################################################################

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"

device = torch.device('cpu')
map_location = torch.device('cpu')


def convert_num_to_cond(x):
    """
    Converts numbered 0, 1, 2 to labelled CoA, RAA and DAA
    Args:
        x: input label to be converted (int)
    Returns:
        Anomaly label (str)
    """
    if x == 0.0:
        z = "CoA"
    elif x == 1.0:
        z = "RAA"
    elif x == 2.0:
        z = "DAA"
    else:
        raise Exception("Not a valid label, should be an int between 0 and 2")
    return z

# Define three segmenters (ensemble)
segmenter0 = AttentionUnet(
    spatial_dims=3,
    in_channels=1,
    out_channels=cl_num + 1,
    channels=(32, 64, 128, 256, 512),
    strides=(2, 2, 2, 2),
    kernel_size=3,
    up_kernel_size=3,
    dropout=0.2
)

segmenter1 = AttentionUnet(
    spatial_dims=3,
    in_channels=1,
    out_channels=cl_num + 1,
    channels=(32, 64, 128, 256, 512),
    strides=(2, 2, 2, 2),
    kernel_size=3,
    up_kernel_size=3,
    dropout=0.2
)

segmenter2 = AttentionUnet(
    spatial_dims=3,
    in_channels=1,
    out_channels=cl_num + 1,
    channels=(32, 64, 128, 256, 512),
    strides=(2, 2, 2, 2),
    kernel_size=3,
    up_kernel_size=3,
    dropout=0.2
)

# Define three classifiers (first two using image + seg, last just seg as input)
classifier0 = DenseNet121(
    spatial_dims=3,
    in_channels=cl_num + 2,
    out_channels=3,
    dropout_prob=0.2,
    norm='INSTANCE')

classifier1 = DenseNet121(
    spatial_dims=3,
    in_channels=cl_num + 2,
    out_channels=3,
    dropout_prob=0.2,
    norm='INSTANCE')

classifier2 = DenseNet121(
    spatial_dims=3,
    in_channels=cl_num + 1,
    out_channels=3,
    dropout_prob=0.2,
    norm='INSTANCE')

torch.backends.cudnn.benchmark = True

#############################################################################################################
#############################################################################################################
# Ensemble models dictionaries
classifiers = {'classifier0': classifier0, 'classifier1': classifier1, 'classifier2': classifier2}
segmenters = {'segmenter0': segmenter0, 'segmenter1': segmenter1, 'segmenter2': segmenter2}

for model_ind in range(3):
    classifier_name = 'classifier' + str(model_ind)
    segmenter_name = 'segmenter' + str(model_ind)

    ckpt_class = torch.load(os.path.join(check_path, classifier_name + '.pth'), map_location=map_location)
    classifiers[classifier_name].load_state_dict(ckpt_class, strict=True)
    classifiers[classifier_name].eval()

    ckpt_seg = torch.load(os.path.join(check_path, segmenter_name + '.pth'), map_location=map_location)
    segmenters[segmenter_name].load_state_dict(ckpt_seg, strict=True)
    segmenters[segmenter_name].eval()

for x in range(len(run_datalist)):
    case_num = x
    img_name = run_datalist[case_num]["image"]
    case_name = os.path.split(run_ds[case_num]["image_meta_dict"]["filename_or_obj"])[1]

    print(case_num)
    img_tmp_info = nib.load(img_name)

    with torch.no_grad():
        img_name = os.path.split(run_ds[case_num]["image_meta_dict"]["filename_or_obj"])[1]
        img = run_ds[case_num]["image"]
        run_inputs = torch.unsqueeze(img, 1)

        seg_soft_all, class_all = [], []
        # Pass through three segmenters
        for model_ind in range(3):
            run_outputs = segmenters['segmenter' + str(model_ind)](run_inputs)
            softmax_out = torch.softmax(run_outputs, dim=1)
            if model_ind==2:
                class_in = softmax_out
            else:
                class_in = torch.cat((softmax_out, run_inputs), dim=1)

            logits_class = classifiers['classifier' + str(model_ind)](class_in)
            class_out = convert_num_to_cond(logits_class.argmax(dim=1).item())

            seg_soft_all.append(softmax_out)
            class_all.append(class_out)

        # Ensemble models (average for seg, max voting for class)
        predicted_seg_avg = torch.mean(torch.stack(seg_soft_all), dim=0)
        class_out_mode = mode(class_all)

        print('The predicted condition is = {}'.format(class_out_mode))

        # Save the segmentation, with predicted class in filename
        out_name = results_path + "/cnn-lab-pred-" + case_name[:-7] + "-" + class_out_mode + ".nii.gz"
        print("OUT NAME", out_name)

        out_label = torch.argmax(predicted_seg_avg, dim=1).detach().cpu()[0, ...]
        out_lab_nii = nib.Nifti1Image(out_label, img_tmp_info.affine, img_tmp_info.header)
        d = {'stack': case_name, 'prediction': class_out_mode}
        nib.save(out_lab_nii, out_name)

#############################################################################################################
#############################################################################################################
