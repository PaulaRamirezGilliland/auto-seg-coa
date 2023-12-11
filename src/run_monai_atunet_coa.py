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



# Define segmenter
segmenter = AttentionUnet(
    spatial_dims=3,
    in_channels=1,
    out_channels=cl_num + 1,
    channels=(32, 64, 128, 256, 512),
    strides=(2, 2, 2, 2),
    kernel_size=3,
    up_kernel_size=3,
    dropout=0.2
)

torch.backends.cudnn.benchmark = True

#############################################################################################################
#############################################################################################################

ckpt_seg = torch.load(os.path.join(check_path, 'segmenter_coa.pth'), map_location=map_location)
segmenter.load_state_dict(ckpt_seg, strict=True)
segmenter.eval()

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
        run_outputs = segmenter(run_inputs)

        # Save the segmentation
        out_name = results_path + "/cnn-lab-pred-" + case_name
        print("OUT NAME", out_name)

        out_label = torch.argmax(run_outputs, dim=1).detach().cpu()[0, ...]
        out_lab_nii = nib.Nifti1Image(out_label, img_tmp_info.affine, img_tmp_info.header)
        d = {'stack': case_name}
        nib.save(out_lab_nii, out_name)

#############################################################################################################
#############################################################################################################
