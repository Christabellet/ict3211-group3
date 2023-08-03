# Deep-Packet




## Prerequisites

1. Ensure Python 3.x is installed.
2. Ensure JAVA_HOME is set and added to system PATH.
3. If using Windows, ensure Hadoop is installed and HADOOP_HOME is set and added to system PATH, with %HADOOP_HOME%\bin containing the [winutils.exe](https://github.com/kontext-tech/winutils) file for the appropriate Hadoop version.

## NVIDIA CUDA

NVIDIA CUDA is used to speed up the performance of applications by harnessing the power of GPUs. Check if your GPU supports CUDA [here](https://developer.nvidia.com/cuda-gpus).

Download link for the latest CUDA version is available [here](https://developer.nvidia.com/cuda-downloads).

## pytorch

This code uses pytorch, which can be accelerated using CUDA. Depending on whether you hava CUDA or not, you can install pytorch using this [link](https://pytorch.org/get-started/locally/).

## Python requirements

Install the other Python requirements from the requirements.txt file, not inclusive of the pytorch requirements in the earlier section.

    pip install -r requirements.txt


# Dataset Preparation

This section contains the steps for training the model.

## Pre-processing dataset

    python preprocessing.py -s /path/to/CompletePcap/ -t processed_data

## Creating train and test datasets

    python create_train_test_set.py -s processed_data -t train_test_data

## Training Model
### Application Model
    python train_cnn.py -d train_test_data/application_classification/train.parquet -m model/application_classification.cnn.model -t app
### Traffic Model

    python train_cnn.py -d train_test_data/traffic_classification/train.parquet -m model/traffic_classification.cnn.model -t traffic

### Pretrained Models
The pretrained models can be downloaded [here](https://drive.google.com/drive/folders/1nHn3JUho04FJdeX8eVcfSmyE42qXXzTV).

## Evalutating Model
Change the model and test data directory accordingly in the .ipynb file. 

# Prediction

    python prediction.py -s /path/to/CompletePcap/ -t output

