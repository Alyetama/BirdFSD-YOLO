# BirdFSD-YOLO

Build and train a custom model to identify birds visiting bird feeders.

📖 **[Documentation](https://birdfsd-yolov5.readthedocs.io/en/latest/)**

[![Docker Build](https://github.com/bird-feeder/BirdFSD-YOLOv5/actions/workflows/docker-build.yml/badge.svg)](https://github.com/bird-feeder/BirdFSD-YOLO/actions/workflows/docker-build.yml) [![Documentation Status](https://readthedocs.org/projects/birdfsd-yolov5/badge/?version=latest)](https://birdfsd-yolov5.readthedocs.io/en/latest/?badge=latest) [![Supported Python versions](https://img.shields.io/badge/Python-%3E=3.8-blue.svg)](https://www.python.org/downloads/) [![PEP8](https://img.shields.io/badge/Code%20style-PEP%208-orange.svg)](https://www.python.org/dev/peps/pep-0008/) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/8810d995e593497d9bd04afcfdc366ce)](https://www.codacy.com/gh/bird-feeder/BirdFSD-YOLO/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bird-feeder/BirdFSD-YOLO&amp;utm_campaign=Badge_Grade) [![GitHub latest release](https://badgen.net/github/release/bird-feeder/BirdFSD-YOLO)](https://github.com/bird-feeder/BirdFSD-YOLO/releases) [![Docker Hub](https://badgen.net/badge/icon/Docker%20Hub?icon=docker&label)](https://hub.docker.com/r/alyetama/birdfsd-yolo) [![GitHub License](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/bird-feeder/BirdFSD-YOLO/blob/main/LICENSE)

## Requirements
- 🐍 [python>=3.8](https://www.python.org/downloads/)

## 🚀 Getting started

### Fork and clone this repository

- First, [fork the repository](https://github.com/bird-feeder/BirdFSD-YOLO/fork).
- Enable workflows in your fork:
<img src="https://i.imgur.com/aF5U6J0.png"  width="720"> 

- Then, click on and enable all the workflows that are highlighted wuth a red square in the image below:
<img src="https://i.imgur.com/pj0Fe9e.png"  width="720"> 

- Clone the repository:
```shell
git clone https://github.com/bird-feeder/BirdFSD-YOLO.git
cd BirdFSD-YOLO
git clone https://github.com/ultralytics/yolo.git
```

### Install dependencies

- If you're on an Apple silicon device (Apple M1), follow the instructions [here](<#instructions-for-apple-m1-users> "Instructions for Apple M1 users"). Otherwise, run:

```sh
pip install -r requirements.txt
```


#### Instructions for Apple M1 users

<details>
  <summary>Click here</summary>

```sh
# Skip this if you're not on an Apple silicon device!

# If you don't have conda, install it:
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh"
bash "Miniforge3-MacOSX-arm64.sh" -b
rm "Miniforge3-MacOSX-arm64.sh"
conda init zsh
source ~/.zshrc
conda activate

# Then, run:
yes | pip uninstall grpcio
conda install grpcio --yes
pip install -r requirements.txt
```

</details>


### Build the package

```sh
poetry build
pip install .
```


## 🌱 Environment Variables

- rename `.env.example` to `.env`, then edit the values based on the table below.

```sh
mv .env.example .env
nano .env  # or with any other editor
# See the table for details about the environment variables.
```

| Name                 | Value                                                                                                                   |
|----------------------|-------------------------------------------------------------------------------------------------------------------------|
| TOKEN                | Label-Studio `Access Token`.                                                                                            |
| LS_HOST              | The URL of the label-studio app (e.g., https://label-studio.example.com) – make sure you include `https://` in the URL. |
| DB_CONNECTION_STRING | MongoDB connection string (e.g., `mongodb://mongodb0.example.com:27017`). See [this article](https://www.mongodb.com/docs/manual/reference/connection-string/) for details.                                                                                                |
| DB_NAME              | Name of the main MongoDB database (default: `label_studio`).                                                            |
| S3_ACCESS_KEY        | (Optional) The S3 bucket's `Access Key ID`.                                                                             |
| S3_SECRET_KEY        | (Optional) The S3 bucket's `Secret Key`.                                                                                |
| S3_REGION            | (Optional) The S3 bucket's region (default: `us-east-1`).                                                               |
| S3_ENDPOINT          | (Optional) The S3 bucket's endpoint/URL server.                                                                         |
| EXCLUDE_LABELS       | (Optional) Comma-separated list of labels to exclude from processing (e.g., label a,label b).                           |

- When you're done editing the `.env` file, run:

```sh
python birdfsd_yolo/model_utils/check_env_file.py --env-file .env
```

## 🗃️ Setup

- To use the GitHub Actions workflows (recommended!), you will need to add every environment variable and its value from `.env` to the `Secrets` of your fork (you can find `Secrets` under `Settings`).

<img src="https://i.imgur.com/xlVfoxX.png"  width="720"> 

<details>
  <summary>Click here to show an example of a new secret</summary>

  <img src="https://i.imgur.com/fOKMgHy.png"  width="720"> 

</details>

## 🔧 Dataset preparation

- **Option 1:** Run the `JSON to YOLO (data preprocessing)` workflow under github `Actions`.

- **Option 2:** Run it locally with:

  ```shell
  python birdfsd_yolo/preprocessing/json2yolov5.py
  mv dataset-YOLO/dataset_config.yml .
  python birdfsd_yolo/model_utils/relative_to_abs.py
  ```

## ⚡ Training[^1]

Use the *Colab* notebook: 

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/bird-feeder/BirdFSD-YOLO/blob/main/notebooks/BirdFSD_YOLOv5_train.ipynb)

## 📝 Prediction

- **Option 1:** Run the `Predict` workflow under github `Actions`.
- **Option 2:** Use the *Colab* notebook:

  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/bird-feeder/BirdFSD-YOLO/blob/main/notebooks/BirdFSDV1_YOLOv5_LS_Predict.ipynb)
  
  
## 🐳 Using Docker
```sh
docker pull alyetama/birdfsd-yolov5:latest
```

### Example Usage
```sh
docker run -it --env-file .env alyetama/birdfsd-yolo python birdfsd_yolov5/preprocessing/json2yolov5.py
```


## 🔖 Related

- [BirdFSD-YOLO-APP](https://github.com/bird-feeder/BirdFSD-YOLO-App)


[^1]: [yolo/wiki/Train-Custom-Data](https://github.com/ultralytics/yolov5/wiki/Train-Custom-Data)
