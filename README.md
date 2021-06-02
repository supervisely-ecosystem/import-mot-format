

<div align="center" markdown>
<img src="https://i.imgur.com/DLlZIes.png"/>


# Import MOTChallenge

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>
  

[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-mot-format)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-mot-format&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-mot-format&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-mot-format&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview

App downloads [MOTChallenge](https://motchallenge.net/) or your prepared archives(which should be located in `Team Files`) with video sequences. After extraction data is converted to [Supervisely](https://app.supervise.ly) format. Currently suppored datasets from [MOTChallenge](https://motchallenge.net/): `MOT15`, `MOT16`, `MOT17` and `MOT20`.

Folder structure of the MOT dataset is as follows:

```python
{root}/{dataset_name}/{train}/{video_name}/{gt + img1 + seqinfo.ini}   
```

The meaning of the individual elements is:

- `dataset_name` name of dataset in created project.
- `video_name` name of video in created dataset.
- `gt` folder with CSV text-file (gt.txt), containing one object instance per line. Each line contain 10 values. More about MOT format value you can read  [here](https://motchallenge.net/instructions/).
- `img1` folder with images the video consists of.
- `seqinfo.ini` file with images and video information.

You can download example of MOT15 dataset [here](https://motchallenge.net/data/MOT15/).

Current version of application supports only `gt` file annotations.

After application execution, `mot_video` project will be created in your workspace. New Supervisely project will contain only one class: `pedestrian` with shape `Rectangle`. Also new project will contain `None` type tag with name `ignore_conf`. Tag indicates that you do not need to take into account this figure in the current frame for evaluating. More about MOT format and `conf` value you can read [here](https://motchallenge.net/instructions/).



## How To Run 
**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/import-mot-format) if it is not there.

**Step 2**: Open `Plugins & Apps` -> `import-mot-format` -> `Run` 

<img src="https://i.imgur.com/FVrbqSn.png"/>

**Step 3**: Select datasets import mode.

Your can choose and download datasets from [MOTChallenge](https://motchallenge.net/).

<img src="https://i.imgur.com/NdgxSJ7.png" width="600px"/>

Or your dataset in MOT format by path to your archive in `Team Files`.

<img src="https://i.imgur.com/5VvVkOu.png" width="600px"/>



## How to use

Result project will be saved in your current `Workspace` with name `mot_video`.

<img src="https://i.imgur.com/b0hafY5.png"/>
