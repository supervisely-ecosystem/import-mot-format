import os
import zipfile, tarfile, shutil
import cv2
import supervisely_lib as sly
from collections import defaultdict
from supervisely_lib.annotation.tag_meta import TagValueType
from supervisely_lib.io.fs import download, file_exists, get_file_name, remove_dir
from supervisely_lib.video_annotation.video_tag import VideoTag
from supervisely_lib.video_annotation.video_tag_collection import VideoTagCollection

my_app = sly.AppService()
TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])

obj_class_name = 'pedestrian'
conf_tag_name = 'ignore_conf'
project_name = 'mot_video'
video_ext = '.mp4'
mot_bbox_file_name = 'gt.txt'
seqinfo_file_name = 'seqinfo.ini'
frame_rate_default = 25
image_name_length = 6
logger = sly.logger
link_path = 'https://motchallenge.net/data/'
input_archive_ext = '.zip'

mot_dataset = os.environ['modal.state.motDataset']

if mot_dataset == 'custom':
   ds_path = os.environ['modal.state.dsPath']
   ARH_NAMES = [os.path.basename(ds_path)]
   LINKS = [None]
else:
    mot_ds_names_str = os.environ['modal.state.currDatasets']
    mot_ds_names = mot_ds_names_str.replace('\'', '')
    mot_ds_names = mot_ds_names.replace(' ', '')
    mot_ds_names = mot_ds_names[1:-1].split(',')
    ARH_NAMES = [ds_name + input_archive_ext for ds_name in mot_ds_names]
    LINKS = [link_path + arch_name for arch_name in ARH_NAMES]


def check_mot_format(input_dir):

    possible_images_extentions = set(['jpg', 'jpeg', 'mpo', 'bmp', 'png', 'webp'])
    mot_datasets = 0
    for r, d, f in os.walk(input_dir):
        logger.warn('ALEX_TEST: {}_{}_{}'.format(r, d, f))
        if 'img1' in d and 'gt' in d:
            if seqinfo_file_name not in f:
                logger.warning(
                    'Folder {} should contain seqinfo.ini file, will be used frame_rate by default'.format(r))
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
                raise ValueError(
                    'Image name should have length {} like: 000001.jpg, 000002.jpg'.format(image_name_length))
            over_files = files_exts - possible_images_extentions
            if len(over_files) > 0:
                raise ValueError(
                    'Folder {} should contain only images, not files with {} extentions'.format(r + '/img1',
                                                                                                over_files))
            mot_datasets += 1
    if mot_datasets == 0:
        raise ValueError(
            'Input format of data does not match the required MOT dataset structure: mot_folder:gt_dir, img1_dir')


def get_frames_with_objects_gt(txt_path):
    frames_without_objs_conf = defaultdict(list)
    frame_to_objects = defaultdict(lambda: defaultdict(list))
    with open(txt_path, "r") as file:
        all_lines = file.readlines()
        for line in all_lines:
            line = line.split('\n')[0].split(',')[:8]
            if len(line) == 0:
                continue
            line = list(map(lambda x: round(float(x)), line))
            line = list(map(int, line))
            frame_to_objects[line[0]][line[1]].extend(line[2:6])
            if line[6] == 0:
                if len(frames_without_objs_conf[line[1]]) == 0:
                    frames_without_objs_conf[line[1]].append([line[0], line[0]])
                elif frames_without_objs_conf[line[1]][-1][1] + 1 == line[0]:
                    frames_without_objs_conf[line[1]][-1][1] = line[0]
                else:
                    frames_without_objs_conf[line[1]].append([line[0], line[0]])

    return frame_to_objects, frames_without_objs_conf


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
    new_project = api.project.create(WORKSPACE_ID, project_name, type=sly.ProjectType.VIDEOS,
                                     change_name_if_conflict=True)
    obj_class = sly.ObjClass(obj_class_name, sly.Rectangle)
    conf_tag_meta = sly.TagMeta(conf_tag_name, TagValueType.NONE)
    meta = sly.ProjectMeta(sly.ObjClassCollection([obj_class]), sly.TagMetaCollection([conf_tag_meta]))
    api.project.update_meta(new_project.id, meta.to_json())

    for ARH_NAME, LINK in zip(ARH_NAMES, LINKS):
        archive_path = os.path.join(storage_dir, ARH_NAME)
        if LINKS[0]:
            if not file_exists(archive_path):
                logger.info('Download archive {}'.format(ARH_NAME))
                download(LINK, archive_path)
        else:
            api.file.download(TEAM_ID, ds_path, archive_path)

        try:
            shutil.unpack_archive(archive_path, storage_dir)
        except Exception('Unknown archive format {}'.format(ARH_NAME)):
            my_app.stop()

        logger.info('Check input mot format')
        if get_file_name(ARH_NAME) in ['MOT16']:
            remove_dir(os.path.join(storage_dir, 'test'))
            curr_mot_dir = os.path.join(storage_dir, 'train')
        else:
            if mot_dataset != 'custom':
                curr_mot_dir = os.path.join(storage_dir, get_file_name(ARH_NAME))
                check_mot_format(curr_mot_dir)
            else:
                curr_mot_dirs = os.listdir(storage_dir)
                curr_mot_dirs.remove(ARH_NAME)
                logger.warn('ALEX_TEST curr_mot_dirs: {}'.format(curr_mot_dirs))
                for curr_mot_dir in curr_mot_dirs:
                    check_mot_format(curr_mot_dir)

        logger.warn('ALEX_TEST storage_dir: {}'.format(os.listdir(storage_dir)))
        a = 5 / 0
        #check_mot_format(curr_mot_dir)

        dataset_name = get_file_name(ARH_NAME)
        new_dataset = api.dataset.create(new_project.id, dataset_name, change_name_if_conflict=True)
        for r, d, f in os.walk(curr_mot_dir):
            if mot_bbox_file_name in f:
                video_name = r.split('/')[-2] + video_ext
                logger.info('Video {} being processed'.format(video_name))
                video_path = os.path.join(curr_mot_dir, video_name)
                imgs_path = r[:-2] + 'img1'
                images = os.listdir(imgs_path)
                progress = sly.Progress('Create video and figures for frame', len(images), app_logger)
                images_ext = images[0].split('.')[1]
                seqinfo_path = r[:-2] + seqinfo_file_name
                frames_with_objects, frames_without_objs_conf = get_frames_with_objects_gt(
                    os.path.join(r, mot_bbox_file_name))
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
                            curr_frame_ranges = frames_without_objs_conf[idx]
                            if len(curr_frame_ranges) == 0:
                                ids_to_video_object[idx] = sly.VideoObject(obj_class)
                            else:
                                conf_tags = [VideoTag(conf_tag_meta,
                                                      frame_range=[curr_frame_range[0] - 1, curr_frame_range[1] - 1])
                                             for curr_frame_range in curr_frame_ranges]
                                ids_to_video_object[idx] = sly.VideoObject(obj_class,
                                                                           tags=VideoTagCollection(conf_tags))
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
                    progress.iter_done_report()

                video.release()
                file_info = api.video.upload_paths(new_dataset.id, [video_name], [video_path])
                new_frames_collection = sly.FrameCollection(new_frames)
                new_objects = sly.VideoObjectCollection(ids_to_video_object.values())
                ann = sly.VideoAnnotation((img_size[1], img_size[0]), len(new_frames), objects=new_objects,
                                          frames=new_frames_collection)
                logger.info('Create annotation for video {}'.format(video_name))
                api.video.annotation.append(file_info[0].id, ann)
        # remove_dir(curr_mot_dir)
    my_app.stop()


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID
    })
    my_app.run(initial_events=[{"command": "import_mot_format"}])


if __name__ == '__main__':
    sly.main_wrapper("main", main)
