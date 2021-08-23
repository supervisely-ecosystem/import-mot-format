

<div align="center" markdown>
<img src="https://i.imgur.com/L0I3dCO.png"/>


# Import MOT

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Input-Data-Format">Input Data Format</a> •
  <a href="#How-To-Use">How To Use</a> •
  <a href="#Results">Results</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/import-mot-format)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-mot-format)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-mot-format&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-mot-format&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-mot-format&counter=runs&label=runs&123)](https://supervise.ly)

</div>

# Overview

App converts data in [MOTChallenge](https://motchallenge.net/) format to [Supervisely](https://docs.supervise.ly/data-organization/00_ann_format_navi) format. You can import MOT datasets or your custom prepared archives located in `Team Files`.

<!-- **Current version of application supports only `gt` file annotations.** -->

<!-- New Supervisely project could contain any number of classes: e.g. `MOT{15,16,17,20}` datasets will contain only `pedestrian` class with shape `Rectangle`(due to the fact that only objects of the pedestrian class are labelled in source datasets). Also new project will contain `None` type tag with name `ignore_conf`. Tag indicates that you do not need to take into account this figure in the current frame for evaluating. More about MOT format and `conf` value you can read [here](https://motchallenge.net/instructions/). -->


Application key points:  
- Created project will be in your Workspace
- Created project will contain `None` type tag with name `ignore_conf` (tag indicates that you do not need to take into account this figure in the current frame for evaluating)([about conf](https://motchallenge.net/instructions/))
- Supports only `gt` file annotations
- Backward compatible with [`Export to MOT`](https://github.com/supervisely-ecosystem/export-to-mot-format)


# Input Data Format

Currently supported datasets from [MOTChallenge](https://motchallenge.net/):  
`MOT15`, `MOT16`, `MOT17` and `MOT20`.

**1. Public Dataset structure**
```
.
└── MOT#.tar
    └── MOT#
        ├── test
        │   └── video_name
        |       ├── det
        |       │   └── det.txt
        │       ├── img1
        │       │   ├── 000001.jpg
        │       │   ├── 000002.jpg
        │       │   └── ...
        │       └── seqinfo.ini
        └── train
            └── video_name
                ├── det
                │   └── det.txt
                ├── gt
                │   └── gt.txt
                ├── img1
                │   ├── 000001.jpg
                │   ├── 000002.jpg
                │   └── ...
                └── seqinfo.ini
```

**2. Custom Dataset structure**
```
.
└── CUSTOM_MOT.tar
    └── dataset_name
        ├── test
        │   └── video_name
        │       ├── img1
        │       │   ├── 000001.jpg
        │       │   ├── 000002.jpg
        │       │   └── ...
        │       └── seqinfo.ini
        └── train
            └── video_name
                ├── gt
                │   └── gt.txt # gt_class_name.txt e.g. gt_car.txt for custom class
                ├── img1
                │   ├── 000001.jpg
                │   ├── 000002.jpg
                │   └── ...
                └── seqinfo.ini
```

The meaning of the individual elements is:

- `dataset_name` name of dataset in created project.
- `video_name` name of video in created dataset.
- `gt` folder with text-files (format: `gt.txt` or `gt_{classname}.txt` for custom data), containing one object instance per line. Each line contain 10 values. More about MOT format values you can read [here](https://motchallenge.net/instructions/).
- `img1` folder with images for video.
- `seqinfo.ini` file with images and video information.

You can download example of MOT15 dataset [here](https://motchallenge.net/data/MOT15/).

# How to Use
1. Add [Import MOT](https://ecosystem.supervise.ly/apps/import-mot-format) to your team from Ecosystem.

<img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/import-mot-format" src="https://imgur.com/QQTBz0C.png" width="350px" style='padding-bottom: 20px'/>  

2. Run app from the `Plugins & Apps` chapter:

<img src="https://imgur.com/6nPIM21.png"/>

3. Select import mode:

- Your can download selected datasets from [MOTChallenge](https://motchallenge.net/).  
- Use your custom dataset in MOT format by path to your archive in `Team Files`.

<img src="https://imgur.com/8lzZUPc.png" width="600px"/>

4. After pressing the `Run` button you will be redirected to the `Tasks` page.

# Results

Result project will be saved in your current `Workspace` with name `mot_video`.

<img src="https://i.imgur.com/tA0lrEN.png"/>

# Watch Demo
<a data-key="sly-embeded-video-link" href="https://youtu.be/i1hugMhGSY8" data-video-code="i1hugMhGSY8">
    <img src="https://i.imgur.com/5cj5ilu.png" alt="SLY_EMBEDED_VIDEO_LINK"  style="max-width:100%;">
</a>
