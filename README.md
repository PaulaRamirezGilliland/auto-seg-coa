
Auto-Seg-CoA
-------------

Automatic segmentation strategy used for deriving a Coarctation of the Aorta risk score from 3D T2w fetal CMR. See Fig. below for segmentation protocol.  

<img src="https://media.springernature.com/full/springer-static/image/chp%3A10.1007%2F978-3-031-45544-5_5/MediaObjects/555468_1_En_5_Fig1_HTML.png?as=webp" alt="AUTOCOA_FETAL_CARDIAC" height="100" align ="centre" />


> "Ramirez, P., Hermida, U., Uus, A., van Poppel, M.P., Grigorescu, I., Steinweg, J.K., Lloyd, D.F., Pushparajah, K., de Vecchi, A., King, A. and Lamata, P., 2023, October. Towards Automatic Risk Prediction of Coarctation of the Aorta from Fetal CMR Using Atlas-Based Segmentation and Statistical Shape Modelling. In International Workshop on Preterm, Perinatal and Paediatric Image Analysis (pp. 53-63). Cham: Springer Nature Switzerland. (doi: 10.1007/978-3-031-45544-5_5)

To run it: 
1.	Pull the docker image:
```bash
docker pull paularg/auto-seg-coa:latest
```
2.	Run the docker mounted to the folder with .nii.gz or .dcm files for processing (CPU version is operational on MAC OS, Linux and Windows):
```bash
docker run -it --rm --mount type=bind,source=location_on_your_machine,target=/home/data paularg/auto-seg-coa:latest /bin/bash
```
3. run aortic arch segmentation: 
```bash
bash /home/auto-seg-coa/scripts/auto-coa.sh /home/data/ your_folder_with_brain_svr_t2_files /home/data/output_folder_for_segmentations
```

MASC: Multi-task vessel Segmentation and diagnosis Classification for aortic arch anomalies (fetal cardiac MRI): 
-------------


MASC is a Pytorch and MONAI (https://monai.io/) based multi-task framework for multi-class segmentation and classification in fetal cardiac aortic arch anomalies. The default architectures are Attention U-Net for segmentation and DenseNet121 for classification.


<img src="https://user-images.githubusercontent.com/93882352/231525071-c67e6777-2417-4abd-8f1b-6574e98ec0f5.png
" alt="MASC_FETAL_CARDIAC" height="200" align ="centre" />


Our networks are trained on 3D T2w reconstructions of fetal cardiac MRI, cropped to the fetal thorax. It is only trained on the following anomalies:  suspected Coarctation of the Aorta (CoA), Right Aortic Arch (RAA) with Aberrant left subclavian artery, and Double Aortic Arch (DAA). The predicted diagnosis class is one of CoA, RAA or DAA. 

To run it: 

Follow steps 1. and 2 described above (Auto-CoA) 


3.	Run 3D fetal cardiac vessel segmentation and classification: 
```bash
bash /home/auto-seg-heart/scripts/auto-masc.sh /home/data/ your_folder_with_brain_svr_t2_files /home/data/output_folder_for_segmentations
```


License:
--------

The SVRTK dockers are distributed under the terms of the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html). This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation. This software is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.


Citation and acknowledgements:
-------------



> "Ramirez, P., Hermida, U., Uus, A., van Poppel, M.P., Grigorescu, I., Steinweg, J.K., Lloyd, D.F., Pushparajah, K., de Vecchi, A., King, A. and Lamata, P., 2023, October. Towards Automatic Risk Prediction of Coarctation of the Aorta from Fetal CMR Using Atlas-Based Segmentation and Statistical Shape Modelling. In International Workshop on Preterm, Perinatal and Paediatric Image Analysis (pp. 53-63). Cham: Springer Nature Switzerland.

> "Hermida, U., van Poppel, M.P., Lloyd, D.F., Steinweg, J.K., Vigneswaran, T.V., Simpson, J.M., Razavi, R., De Vecchi, A., Pushparajah, K. and Lamata, P., 2023. Learning the hidden signature of fetal arch anatomy: a three-dimensional shape analysis in suspected coarctation of the aorta. Journal of cardiovascular translational research, 16(3), pp.738-747.

> "Ramirez Gilliland, P., Uus, A., van Poppel, M.P., Grigorescu, I., Steinweg, J.K., Lloyd, D.F., Pushparajah, K., King, A.P. and Deprez, M., 2022, September. Automated Multi-class Fetal Cardiac Vessel Segmentation in Aortic Arch Anomalies Using T2-Weighted 3D Fetal MRI. In International Workshop on Preterm, Perinatal and Paediatric Image Analysis (pp. 82-93). Cham: Springer Nature Switzerland.

> "Ramirez, P., Uus, A., van Poppel, M.P., Grigorescu, I., Steinweg, J.K., Lloyd, D.F., Pushparajah, K., King, A.P. and Deprez, M., 2023. Multi-task learning for joint weakly-supervised segmentation and aortic arch anomaly classification in fetal cardiac MRI. Machine Learning for Biomedical Imaging, 2(PIPPI 2022 special issue), pp.406-446.



