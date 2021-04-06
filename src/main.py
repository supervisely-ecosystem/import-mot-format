import os
import zipfile
import cv2
import supervisely_lib as sly
from supervisely_lib.annotation.tag_meta import TagValueType
from collections import defaultdict
from supervisely_lib.io.fs import download, file_exists, get_file_name, remove_dir


my_app = sly.AppService()
TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
#INPUT_FOLDER = "mot_format"

ARH_NAMES = ['MOT15.zip', 'MOT16.zip', 'MOT17.zip', 'MOT20.zip']
LINKS = ['https://motchallenge.net/data/MOT15.zip', 'https://motchallenge.net/data/MOT16.zip', 'https://motchallenge.net/data/MOT17.zip', 'https://motchallenge.net/data/MOT20.zip']

obj_class_name = 'pedestrian'
project_name = 'mot_video'
video_ext = '.mp4'
mot_bbox_file_name = 'gt.txt'
seqinfo_file_name = 'seqinfo.ini'
frame_rate_default = 25
image_name_length = 6
logger = sly.logger


def check_mot_format(input_dir):
    possible_images_extentions = set(['jpg', 'jpeg', 'mpo', 'bmp', 'png', 'webp'])
    mot_datasets = 0
    for r, d, f in os.walk(input_dir):
        if 'img1' in d and 'gt' in d:
            if seqinfo_file_name not in f:
                logger.warning('Folder {} should contain seqinfo.ini file, will be used frame_rate by default'.format(r))
            check_det = os.listdir(r + '/gt')
            if mot_bbox_file_name not in check_det:
                raise ValueError('Folder {} should contain gt.txt file'.format(r + '/gt'))
            check_imgs = os.listdir(r + '/img1')
            files_exts = set([file.split('.')[1] for file in check_imgs])
            img_names_length = set([len(file.split('.')[0]) for file in check_imgs])
            img_exts = list(files_exts & possible_images_extentions)
            if len(img_exts) == 0:
                raise ValueError('Where is no images in {} directory'.format(r + '/img1'))
            if image_name_length not in img_names_length or len(img_names_length) > 1:
                raise ValueError('Image name should have length {} like: 000001.jpg, 000002.jpg'.format(image_name_length))
            over_files = files_exts - possible_images_extentions
            if len(over_files) > 0:
                raise ValueError('Folder {} should contain only images, not files with {} extentions'.format(r + '/img1', over_files))
            mot_datasets += 1
    if mot_datasets == 0:
        raise ValueError('Input format of data does not match the required MOT dataset structure: mot_folder:gt_dir, img1_dir')


def get_frames_with_objects_gt(txt_path):
    frame_to_objects = defaultdict(lambda: defaultdict(list))
    with open(txt_path, "r") as file:
        all_lines = file.readlines()
        for line in all_lines:
            line = line.split('\n')[0].split(',')[:-3]
            if len(line) == 0:
                continue
            line = list(map(lambda x: round(float(x)), line))
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


def img_size_from_seqini(txt_path):
    with open(txt_path, "r") as file:
        all_lines = file.readlines()
        img_width = int(all_lines[5].split('\n')[0].split('=')[1])
        img_height = int(all_lines[6].split('\n')[0].split('=')[1])
        frame_rate = int(all_lines[3].split('\n')[0].split('=')[1])
    return (img_width, img_height), frame_rate


@my_app.callback("import_mot_format")
@sly.timeit
def import_mot_format(api: sly.Api, task_id, context, state, app_logger):
    storage_dir = my_app.data_dir
    new_project = api.project.create(WORKSPACE_ID, project_name, type=sly.ProjectType.VIDEOS, change_name_if_conflict=True)
    obj_class = sly.ObjClass(obj_class_name, sly.Rectangle)
    meta = sly.ProjectMeta(sly.ObjClassCollection([obj_class]))
    api.project.update_meta(new_project.id, meta.to_json())

    for ARH_NAME, LINK in zip(ARH_NAMES, LINKS):

        archive_path = os.path.join(storage_dir, ARH_NAME)

        if not file_exists(archive_path):
            logger.info('Download archive {}'.format(ARH_NAME))
            download(LINK, archive_path)
        #api.file.download(TEAM_ID, cur_files_path, archive_path)
        if zipfile.is_zipfile(archive_path):
            logger.info('Extract archive {}'.format(ARH_NAME))
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(storage_dir)
        else:
            raise Exception("No such file {}".format(ARH_NAME))

        logger.info('Check input mot format')
        if get_file_name(ARH_NAME) in ['MOT16']:
            remove_dir(os.path.join(storage_dir, 'test'))
            curr_mot_dir = os.path.join(storage_dir, 'train')
        else:
            curr_mot_dir = os.path.join(storage_dir, get_file_name(ARH_NAME))
        check_mot_format(curr_mot_dir)

        dataset_name = get_file_name(ARH_NAME)
        new_dataset = api.dataset.create(new_project.id, dataset_name, change_name_if_conflict=True)
        for r, d, f in os.walk(curr_mot_dir):
            if mot_bbox_file_name in f:
                video_name = r.split('/')[-2] + video_ext
                logger.info('Video {} being processed'.format(video_name))
                video_path = os.path.join(curr_mot_dir, video_name)
                imgs_path = r[:-2] + 'img1'
                images = os.listdir(imgs_path)
                images_ext = images[0].split('.')[1]
                seqinfo_path = r[:-2] + seqinfo_file_name
                frames_with_objects = get_frames_with_objects_gt(os.path.join(r, mot_bbox_file_name))
                if os.path.isfile(seqinfo_path):
                    img_size, frame_rate = img_size_from_seqini(seqinfo_path)
                else:
                    img = sly.image.read(os.path.join(imgs_path, images[0]))
                    img_size = (img.shape[1], img.shape[0])
                    frame_rate = frame_rate_default
                video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'MP4V'), frame_rate, img_size)
                im_names = []
                im_paths = []
                ids_to_video_object = {}
                new_frames = []
                for image_id in range(1, len(images) + 1):
                    new_figures = []
                    image_name = str(image_id).zfill(image_name_length) + '.' + images_ext
                    im_names.append(image_name)
                    im_paths.append(os.path.join(imgs_path, image_name))
                    video.write(cv2.imread(os.path.join(imgs_path, image_name)))
                    frame_object_coords = frames_with_objects[image_id]
                    for idx, coords in frame_object_coords.items():
                        if idx not in ids_to_video_object.keys():
                            ids_to_video_object[idx] = sly.VideoObject(obj_class)
                        left, top, w, h = coords
                        bottom = top + h
                        if round(bottom) >= img_size[1] - 1:
                            bottom = img_size[1] - 2
                        right = left + w
                        if round(right) >= img_size[0] - 1:
                            right = img_size[0] - 2
                        if left < 0:
                            left = 0
                        if top < 0:
                            top = 0
                        if right <= 0 or bottom <= 0 or left >= img_size[0] or top >= img_size[1]:
                            continue

                        geom = sly.Rectangle(top, left, bottom, right)
                        figure = sly.VideoFigure(ids_to_video_object[idx], geom, image_id - 1)
                        new_figures.append(figure)
                    new_frame = sly.Frame(image_id - 1, new_figures)
                    new_frames.append(new_frame)

                video.release()
                file_info = api.video.upload_paths(new_dataset.id, [video_name], [video_path])
                new_frames_collection = sly.FrameCollection(new_frames)
                new_objects = sly.VideoObjectCollection(ids_to_video_object.values())
                ann = sly.VideoAnnotation((img_size[1], img_size[0]), len(new_frames), objects=new_objects, frames=new_frames_collection)
                api.video.annotation.append(file_info[0].id, ann)
        remove_dir(curr_mot_dir)
        #clean_dir(storage_dir)
    my_app.stop()



def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID
    })

    # Run application service
    my_app.run(initial_events=[{"command": "import_mot_format"}])



if __name__ == '__main__':
        sly.main_wrapper("main", main)


