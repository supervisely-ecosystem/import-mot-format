import os
import zipfile
import cv2
from numpy import random
import supervisely_lib as sly
from supervisely_lib.annotation.tag_meta import TagValueType
import numpy as np
from collections import defaultdict


my_app = sly.AppService()
TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
PROJECT_ID = int(os.environ['modal.state.slyProjectId'])
IMAGE_ID = int(os.environ['modal.state.slyImageId'])
INPUT_FOLDER = os.environ.get("modal.state.slyFolder")
INPUT_FILE = os.environ.get("modal.state.slyFile")
ARH_NAME = os.environ.get("modal.state.slyArh")



def get_frames_with_objects_gt(txt_path):
    frame_to_objects = defaultdict(lambda: defaultdict(list))
    with open(txt_path, "r") as file:
        all_lines = file.readlines()
        for line in all_lines:
            line = line.split('\n')[0].split(',')[:-3]
            line = list(map(int, line))
            frame_to_objects[line[0]][line[1]].extend(line[2:6])
    return frame_to_objects


def get_frames_with_objects_det(txt_path):
    frame_to_objects = defaultdict(list)
    with open(txt_path, "r") as file:
        all_lines = file.readlines()
        for line in all_lines:
            line = line.split('\n')[0].split(',')[:-4]
            line = list(map(int, line))
            frame_to_objects[line[0]].extend([line[2:6]])
    return frame_to_objects



@my_app.callback("import_mot_format")
@sly.timeit
def import_mot_format(api: sly.Api, task_id, context, state, app_logger):
    storage_dir = my_app.data_dir

    if INPUT_FOLDER:
        cur_files_path = INPUT_FOLDER + ARH_NAME
        archive_path = os.path.join(storage_dir, ARH_NAME)
    else:
        cur_files_path = INPUT_FILE
        archive_path = storage_dir + cur_files_path

    #api.file.download(TEAM_ID, cur_files_path, archive_path)
    #if zipfile.is_zipfile(archive_path):
        #with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            #zip_ref.extractall(storage_dir)
    #else:
        #raise Exception("No such file".format(ARH_NAME))

    #new_project = api.project.create(WORKSPACE_ID, 'mot', change_name_if_conflict=True)

    #test_gt = '/home/andrew/alex_work/app_data/data/MOT20/train/MOT20-05/gt/gt.txt'
    #test_det = '/home/andrew/alex_work/app_data/data/MOT20/train/MOT20-05/det/det.txt'
    #gt = get_frames_with_objects_gt(test_gt)
    #det = get_frames_with_objects_det(test_det)

    test_path = '/home/andrew/alex_work/app_data/data/MOT20'
    img_size = (1000, 1000)
    for r, d, f in os.walk(test_path):
        if f == ['det.txt']:
            new_dataset_name = r.split('/')[-2]
            imgs_path = r[:-3] + 'img1'
            #new_dataset = api.dataset.create(new_project.id, new_dataset_name, change_name_if_conflict=True)
            res_anns = []
            frames_with_objects = get_frames_with_objects_det(os.path.join(r, f[0]))
            for frame in frames_with_objects:
                img_name = str(frame).zfill(6) + '.jpg'
                img_path = os.path.join(imgs_path, img_name)
                labels = []
                coords = frames_with_objects[frame]
                for curr_coord in coords:
                    geom = sly.Rectangle(curr_coord[1], curr_coord[0], curr_coord[1] + curr_coord[3], curr_coord[0] + curr_coord[2])
                    obj_class = sly.ObjClass('pedestrain', sly.Rectangle)
                    label = sly.Label(geom, obj_class)
                    labels.append(label)
                ann = sly.Annotation(img_size, labels)
                res_anns.append(ann)

            #new_image_infos = api.image.upload_nps(new_dataset.id, res_images_names, res_images)
            #image_ids = [img_info.id for img_info in new_image_infos]
            #api.annotation.upload_anns(image_ids, res_anns)


    #progress = sly.Progress('Start detecting...', 1)
    #progress.iter_done_report()
    my_app.stop()



def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID,
        "PROJECT_ID": PROJECT_ID,
        "IMAGE_ID": IMAGE_ID
    })

    # Run application service
    my_app.run(initial_events=[{"command": "import_mot_format"}])



if __name__ == '__main__':
        sly.main_wrapper("main", main)


