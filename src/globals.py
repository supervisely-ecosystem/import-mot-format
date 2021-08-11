import os, json
import supervisely_lib as sly


my_app = sly.AppService()
api: sly.Api = my_app.public_api

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])

storage_dir = my_app.data_dir

obj_class_pedestrian = 'pedestrian'
conf_tag_name = 'ignore_conf'
project_name = 'mot_video'
video_ext = '.mp4'
mot_bbox_filename = 'gt'
seqinfo_file_name = 'seqinfo.ini'
frame_rate_default = 25
image_name_length = 6
logger = sly.logger
link_path = 'https://motchallenge.net/data/'
input_archive_ext = '.zip'
custom_ds = 'custom'
train = 'train'
test = 'test'
train_suffix = '_train'
test_suffix = '_test'

mot_dataset = os.environ['modal.state.motDataset']

if mot_dataset == custom_ds:
   ds_path = os.environ['modal.state.dsPath']
   ARH_NAMES = [os.path.basename(ds_path)]
   LINKS = [None]
else:
    mot_ds_names_str = os.environ['modal.state.currDatasets']
    if mot_ds_names_str == []:
        my_app.show_modal_window("No datasets selected for import")
        my_app.stop()
    mot_ds_names = mot_ds_names_str.replace('\'', '')
    mot_ds_names = mot_ds_names.replace(' ', '')
    mot_ds_names = mot_ds_names[1:-1].split(',')
    ARH_NAMES = [ds_name + input_archive_ext for ds_name in mot_ds_names]
    LINKS = [link_path + arch_name for arch_name in ARH_NAMES]

    download_test_data = bool(os.environ.get("modal.state.testData", False))
