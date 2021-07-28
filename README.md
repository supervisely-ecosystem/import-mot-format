

<div align="center" markdown>
<img src="https://i.imgur.com/L0I3dCO.png"/>


# Import MOT

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>
  
[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/import-mot-format)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-mot-format)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-mot-format&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-mot-format&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-mot-format&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview

App converts data in [MOTChallenge](https://motchallenge.net/) format to [Supervisely](https://docs.supervise.ly/data-organization/00_ann_format_navi) format. You can import MOT datasets or your custom prepared archives located in `Team Files`. Backward compatible with [`Export to MOT`](https://github.com/supervisely-ecosystem/export-to-mot-format) app.

Currently supported datasets from [MOTChallenge](https://motchallenge.net/): `MOT15`, `MOT16`, `MOT17` and `MOT20`.

**1. Public Dataset structure**
```
└── MOT.tar
    └── dataset_name
        └── train
            └── video_name
                 ├── gt
                 |   └── gt.txt
                 ├── img1
                 └── seqinfo.ini
```

**2. Custom Dataset structure**
```
└── custom_data.tar
    └── dataset_name
        └── train
            └── video_name
                 ├── gt
                 |   └── gt_class_name.txt # e.g. gt_car.txt
                 ├── img1
                 └── seqinfo.ini
```

The meaning of the individual elements is:

- `dataset_name` name of dataset in created project.
- `video_name` name of video in created dataset.
- `gt` folder with text-files (format: `gt.txt` or `gt_{classname}.txt` for custom data), containing one object instance per line. Each line contain 10 values. More about MOT format values you can read [here](https://motchallenge.net/instructions/).
- `img1` folder with images for video.
- `seqinfo.ini` file with images and video information.

You can download example of MOT15 dataset [here](https://motchallenge.net/data/MOT15/).

Current version of application supports only `gt` file annotations.

After application execution, you will be redirected to `Tasks` page and `mot_video` project will be created in your workspace. New Supervisely project could contain any number of classes: e.g. `MOT{15,16,17,20}` datasets will contain only `pedestrian` class with shape `Rectangle`(due to the fact that only objects of the pedestrian class are labelled in source datasets). Also new project will contain `None` type tag with name `ignore_conf`. Tag indicates that you do not need to take into account this figure in the current frame for evaluating. More about MOT format and `conf` value you can read [here](https://motchallenge.net/instructions/).

## How To Run 
**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/import-mot-format) if it is not there.

**Step 2**: Open `Plugins & Apps` -> `import-mot-format` -> `Run` 

<img src="https://i.imgur.com/o8Hoyig.png"/>

**Step 3**: Select import mode.

Your can download selected datasets from [MOTChallenge](https://motchallenge.net/).

<img src="https://i.imgur.com/Ifz2KwX.png" width="600px"/>

Or your custom dataset in MOT format by path to your archive in `Team Files`.

<img src="https://i.imgur.com/agKDn2A.png" width="600px"/>

After pressing the `Run` button you will be redirected to the `Tasks` page.

## How to use

Result project will be saved in your current `Workspace` with name `mot_video`.

<img src="https://i.imgur.com/tA0lrEN.png"/>
