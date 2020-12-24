import os
import tarfile
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



def get_frames_with_objects(txt_path):
    frame_to_objects = defaultdict(lambda: defaultdict(list))
    with open(txt_path, "r") as file:
        all_lines = file.readlines()
        for line in all_lines:
            line = line.split('\n')[0].split(',')[:-3]
            line = list(map(int, line))
            frame_to_objects[line[0]][line[1]].extend(line[2:6])
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

    api.file.download(TEAM_ID, cur_files_path, archive_path)

    if tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path) as archive:
            archive.extractall(storage_dir)
    else:
        raise Exception("No such file".format(ARH_NAME))


    #new_project = api.project.create(WORKSPACE_ID, 'mot', change_name_if_conflict=True)
    txt_path = '/home/andrew/alex_work/app/import-mot-format/MOT20Labels/train/MOT20-01/gt/gt.txt'
    test_path = '/home/andrew/alex_work/app/import-mot-format/MOT20Labels'
    img_size = (1000, 1000)
    for r, d, f in os.walk(test_path):
        if f == ['gt.txt']:
            new_dataset_name = r.split('/')[-2]
            #new_dataset = api.dataset.create(new_project.id, new_dataset_name, change_name_if_conflict=True)
            res_anns = []
            frames_with_objects = get_frames_with_objects(os.path.join(r, f[0]))
            for frame in frames_with_objects:
                labels = []
                for curr_obj in frames_with_objects[frame]:
                    coords = frames_with_objects[frame][curr_obj]
                    geom = sly.Rectangle(coords[1], coords[0], coords[1] + coords[3], coords[0] + coords[2])
                    obj_class = sly.ObjClass('pedestrain', sly.Rectangle)
                    label = sly.Label(geom, obj_class)
                    labels.append(label)
                ann = sly.Annotation(img_size, labels)
                res_anns.append(ann)

            new_image_infos = api.image.upload_nps(new_dataset.id, res_images_names, res_images)
            image_ids = [img_info.id for img_info in new_image_infos]
            api.annotation.upload_anns(image_ids, res_anns)


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


