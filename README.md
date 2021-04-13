#TODO picture here


# From MOTChallenge to Supervisely format


<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Preparation">Preparation</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a>
</p>
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/export-to-cityscapes)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-mot-format(https://github.com/supervisely-ecosystem/import-mot-format)&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-mot-format&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-mot-format&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview

App download archives with video sequences in unconstrained environments from [MOTChallenge](https://motchallenge.net/). All sequences have been annotated with high accuracy, strictly following a well-defined protocol. Then the archives are extracted and converted to the Supervisely ([link to format](https://docs.supervise.ly/data-organization/00_ann_format_navi)). We use for convertation MOT15, MOT16, MOT17 and MOT20 datasets. You do not need to download, unpack or perform any actions with the original data. All actions are performed automatically by pressing one button. After execution application, a project named `mot_video` will be created in your workspace, containing 4 datasets. New Supervisely project will contain only one class: `pedestrian` with shape `Rectangle`. Also new project will contain None type tag `ignore_conf`. This tag indicates that you do not need to take the figure in the current frame for evaluating. More about MOT format and `conf` value you can read [here](https://motchallenge.net/instructions/).



## How To Run 
**Step 1**: Add app to your team from [Ecosystem](https://ecosystem.supervise.ly/apps/convert-supervisely-to-cityscapes-format) if it is not there.

**Step 2**: Open context menu of project -> `Download as` -> `Convert Supervisely to Cityscapes format` 

<img src="https://i.imgur.com/XKDjlu3.png" width="600px"/>


## How to use
After running the application, you will be redirected to the Tasks page. Once application processing has finished, your link for downloading will become available. Click on the file name to download it

<img src="https://i.imgur.com/4AB2hgH.png"/>

**Note** You can also find your images metadata in Team Files->cityscapes_format->app_id->`projectId_projectName.tar`

<img src="https://i.imgur.com/VxbXPJj.png"/>
