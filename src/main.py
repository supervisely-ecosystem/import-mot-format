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

obj_class_name = 'pedestrain'
logger = sly.logger


def check_mot_format(input_dir):
    possible_images_extentions = set(['jpg', 'jpeg', 'mpo', 'bmp', 'png', 'webp'])
    mot_datasets = 0
    for r, d, f in os.walk(input_dir):
        if 'img1' in d and 'det' in d:
            check_det = os.listdir(r + '/det')
            if 'det.txt' not in check_det:
                raise ValueError('Folder {} should contain det.txt file'.format(r + '/det'))
            check_imgs = os.listdir(r + '/img1')
            files_exts = set([file.split('.')[1] for file in check_imgs])
            img_names_length = set([len(file.split('.')[0]) for file in check_imgs])
            img_exts = list(files_exts & possible_images_extentions)
            if len(img_exts) == 0:
                raise ValueError('Where is no images in {} directory'.format(r + '/img1'))
            if 6 not in img_names_length or len(img_names_length) > 1:
                raise ValueError('Image name should have length 6 like: 000001.jpg, 000002.jpg')
            over_files = files_exts - possible_images_extentions
            if len(over_files) > 0:
                raise ValueError('Folder {} should contain only images, not files with {} extentions'.format(r + '/img1', over_files))
            mot_datasets += 1
    if mot_datasets == 0:
        raise ValueError('Input format of data does not match the required MOT dataset structure: mot_folder:det_dir, img1_dir')


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
            if len(line) == 0:
                continue
            line = list(map(lambda x: round(float(x)), line))
            line = list(map(int, line))
            frame_to_objects[line[0]].extend([line[2:6]])
    return frame_to_objects


#def img_size_from_seqini(txt_path):
#    with open(txt_path, "r") as file:
#        all_lines = file.readlines()
#        img_width = int(all_lines[5].split('\n')[0].split('=')[1])
#        img_height = int(all_lines[6].split('\n')[0].split('=')[1])
#    return (img_width, img_height)


@my_app.callback("import_mot_format")
@sly.timeit
def import_mot_format(api: sly.Api, task_id, context, state, app_logger):
    storage_dir = my_app.data_dir

    if INPUT_FOLDER:
        cur_files_path = INPUT_FOLDER + ARH_NAME
        archive_path = os.path.join(storage_dir, ARH_NAME)
    else:
        raise ValueError('Input folder not exist')

    logger.info('Download archive')
    #api.file.download(TEAM_ID, cur_files_path, archive_path)
    #if zipfile.is_zipfile(archive_path):
    #    logger.info('Extract archive')
    #    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
    #        zip_ref.extractall(storage_dir)
    #else:
    #    raise Exception("No such file".format(ARH_NAME))

    logger.info('Check input mot format')
    check_mot_format(storage_dir)
    new_project = api.project.create(WORKSPACE_ID, 'mot', change_name_if_conflict=True)
    obj_class = sly.ObjClass(obj_class_name, sly.Rectangle)
    meta = sly.ProjectMeta(sly.ObjClassCollection([obj_class]))
    api.project.update_meta(new_project.id, meta.to_json())
    for r, d, f in os.walk(storage_dir):
        if 'det.txt' in f:
            new_dataset_name = r.split('/')[-2]
            logger.info('Dataset with name {} in processing'.format(new_dataset_name))
            imgs_path = r[:-3] + 'img1'
            img_to_find_shape = os.listdir(imgs_path)[0]
            img = sly.imaging.image.read(os.path.join(imgs_path, img_to_find_shape))
            img_shape = (img.shape[0], img.shape[1])
            #seqinfo_path = r[:-3] + 'seqinfo.ini'
            #img_size = img_size_from_seqini(seqinfo_path)
            new_dataset = api.dataset.create(new_project.id, new_dataset_name, change_name_if_conflict=True)
            frames_with_objects = get_frames_with_objects_det(os.path.join(r, 'det.txt'))
            images = os.listdir(imgs_path)
            #to_debag = 0 # TODO del comment to test project fast
            for batch in sly.batched(images):
                #if to_debag == 1: # TODO del comment to test project fast
                    #break
                res_anns = []
                full_images_paths = []
                for img_name in batch:
                    full_images_paths.append(os.path.join(imgs_path, img_name))
                    frame = int(img_name.split('.')[0])
                    labels = []
                    coords = frames_with_objects[frame]
                    if len(coords) == 0:
                        logger.warning('Where is no data for image {} in det.txt'.format(img_name))
                        ann = sly.Annotation(img_shape)
                    else:
                        for curr_coord in coords:
                            geom = sly.Rectangle(curr_coord[1], curr_coord[0], curr_coord[1] + curr_coord[3], curr_coord[0] + curr_coord[2])
                            label = sly.Label(geom, obj_class)
                            labels.append(label)
                        ann = sly.Annotation(img_shape, labels)
                    res_anns.append(ann)
                new_image_infos = api.image.upload_paths(new_dataset.id, batch, full_images_paths)
                image_ids = [img_info.id for img_info in new_image_infos]
                api.annotation.upload_anns(image_ids, res_anns)
                #to_debag += 1 # TODO del comment to test project fast
            logger.info('Dataset with name {} upload with {} images'.format(new_dataset_name, len(images)))

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


