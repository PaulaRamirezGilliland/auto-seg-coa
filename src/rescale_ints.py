#!/usr/bin/python 
from __future__ import print_function

import sys
import warnings

import nibabel as nib
import numpy as np
from monai.transforms import (ScaleIntensity)

warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")

filename = sys.argv[1]
out_name = sys.argv[2]

img = nib.load(filename)
img_arr = img.get_fdata()
img_arr = np.expand_dims(img_arr, 0)

if np.min(img_arr)<0:

    img_arr[img_arr == 0.0] = np.min(img_arr) - 1

tf = ScaleIntensity(0, 1000)
img_save = tf(img_arr)

out_label = img_save[0, ...]
out_lab_nii = nib.Nifti1Image(out_label, img.affine, img.header)
nib.save(out_lab_nii, out_name)

