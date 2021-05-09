<img src="https://i.imgur.com/DLlZIes.png"/>


# Import MOTChallenge


<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Preparation">Preparation</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/export-only-labeled-items)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/export-only-labeled-items&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/export-only-labeled-items&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/export-only-labeled-items&counter=runs&label=runs&123).](https://supervise.ly)

</div>

## Overview

App download archives with video sequences in unconstrained environments from [MOTChallenge](https://motchallenge.net/). All sequences have been annotated with high accuracy, strictly following a well-defined protocol. Then the archives are extracted and converted to the [Supervisely](https://app.supervise.ly). We use for convertation `MOT15`, `MOT16`, `MOT17` and `MOT20` datasets. You do not need to download, unpack or perform any actions with the original data. All actions are performed automatically by pressing one button. After execution application, a project named `mot_video` will be created in your workspace, containing 4 datasets. New Supervisely project will contain only one class: `pedestrian` with shape `Rectangle`. Also new project will contain `None` type tag with name `ignore_conf`. This tag indicates that you do not need to take the figure in the current frame for evaluating. More about MOT format and `conf` value you can read [here](https://motchallenge.net/instructions/).



## How To Run 
**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/import-mot-format) if it is not there.

**Step 2**: Open `Plugins & Apps` -> `import-mot-format` -> `Run` 

<img src="https://i.imgur.com/FVrbqSn.png"/>


## How to use
Result project is saved your current `Workspace` with name `mot_video`.

<img src="https://i.imgur.com/b0hafY5.png"/>