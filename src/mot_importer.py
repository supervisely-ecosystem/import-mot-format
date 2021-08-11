import os
import cv2
import globals as g
import supervisely_lib as sly
from collections import defaultdict
from supervisely_lib.io.fs import get_file_name, dir_exists
from supervisely_lib.video_annotation.video_tag import VideoTag
from supervisely_lib.video_annotation.video_tag_collection import VideoTagCollection


def check_mot_format(input_dir):
    gt_not_exist = True
    possible_images_extentions = set(['jpg', 'jpeg', 'mpo', 'bmp', 'png', 'webp'])
    mot_datasets = 0
    for r, d, f in os.walk(input_dir):
        if 'img1' in d and 'gt' in d:
            if g.seqinfo_file_name not in f:
                g.logger.warning(
                    'Folder {} should contain seqinfo.ini file, frame_rate will be set to default'.format(r))
            check_gt = os.listdir(r + '/gt')
            for curr_gt in check_gt:
                if curr_gt.split('_')[0] == g.mot_bbox_filename or curr_gt == 'gt.txt':
                    gt_not_exist = False
                    break
            if gt_not_exist:
                raise ValueError('Folder {} should contain gt annotation file'.format(r + '/gt'))
            check_imgs = os.listdir(r + '/img1')
            files_exts = set([file.split('.')[1] for file in check_imgs])
            img_names_length = set([len(file.split('.')[0]) for file in check_imgs])
            img_exts = list(files_exts & possible_images_extentions)
            if len(img_exts) == 0:
                raise ValueError('There are no images in {} directory'.format(r + '/img1'))
            if g.image_name_length not in img_names_length or len(img_names_length) > 1:
                raise ValueError(
                    'Image name should have length {} like: 000001.jpg, 000002.jpg'.format(g.image_name_length))
            over_files = files_exts - possible_images_extentions
            if len(over_files) > 0:
                raise ValueError(
                    'Folder {} should contain only images, not files with {} extentions'.format(r + '/img1',
                                                                                                over_files))
            mot_datasets += 1
    if mot_datasets == 0:
        raise ValueError(
            'Input format of data does does not match the required MOT dataset structure: mot_folder:gt_dir, img1_dir')


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


def import_test_dataset(new_project, ds_name, test_dir, app_logger):
    if dir_exists(test_dir):
        test_dataset = g.api.dataset.create(new_project.id, ds_name, change_name_if_conflict=True)
        test_subdirs = os.listdir(test_dir)
        for test_subdir in test_subdirs:
            video_name = test_subdir + g.video_ext
            video_path = os.path.join(test_dir, video_name)
            imgs_path = os.path.join(test_dir, test_subdir, 'img1')
            images = os.listdir(imgs_path)
            progress = sly.Progress(f'Importing "{video_name}" to "{ds_name}" dataset', len(images), app_logger)
            images_ext = images[0].split('.')[1]
            seqinfo_path = os.path.join(test_dir, test_subdir, g.seqinfo_file_name)
            if os.path.isfile(seqinfo_path):
                img_size, frame_rate = img_size_from_seqini(seqinfo_path)
            else:
                img = sly.image.read(os.path.join(imgs_path, images[0]))
                img_size = (img.shape[1], img.shape[0])
                frame_rate = g.frame_rate_default
            video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'MP4V'), frame_rate, img_size)
            for image_id in range(1, len(images) + 1):
                image_name = str(image_id).zfill(g.image_name_length) + '.' + images_ext
                video.write(cv2.imread(os.path.join(imgs_path, image_name)))
                progress.iter_done_report()
            video.release()
            file_info = g.api.video.upload_paths(test_dataset.id, [video_name], [video_path])


def import_dataset(new_project, ds_name, curr_mot_dir, meta, conf_tag_meta, app_logger):
    obj_classes = []
    obj_class_names = []
    new_dataset = g.api.dataset.create(new_project.id, ds_name, change_name_if_conflict=True)

    for r, d, f in os.walk(curr_mot_dir):
        if r.split('/')[-1] == g.mot_bbox_filename:
            video_name = r.split('/')[-2] + g.video_ext
            video_path = os.path.join(curr_mot_dir, video_name)
            imgs_path = r[:-2] + 'img1'
            images = os.listdir(imgs_path)
            progress = sly.Progress(f'Importing "{video_name}" to "{ds_name}" dataset', len(images), app_logger)
            images_ext = images[0].split('.')[1]
            seqinfo_path = r[:-2] + g.seqinfo_file_name
            if os.path.isfile(seqinfo_path):
                img_size, frame_rate = img_size_from_seqini(seqinfo_path)
            else:
                img = sly.image.read(os.path.join(imgs_path, images[0]))
                img_size = (img.shape[1], img.shape[0])
                frame_rate = g.frame_rate_default
            video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'MP4V'), frame_rate, img_size)

            gt_files = os.listdir(r)
            obj_classes_data = []

            for curr_gt_file in gt_files:
                if curr_gt_file == 'gt.txt':
                    obj_class_name = g.obj_class_pedestrian
                else:
                    obj_class_name = sly.fs.get_file_name(curr_gt_file).split('_')[1]

                if obj_class_name not in obj_class_names:
                    obj_class_names.append(obj_class_name)
                    obj_class = sly.ObjClass(obj_class_name, sly.Rectangle)
                    obj_classes.append(obj_class)
                frames_with_objects, frames_without_objs_conf = get_frames_with_objects_gt(os.path.join(r, curr_gt_file))
                obj_classes_data.append((frames_with_objects, frames_without_objs_conf, obj_class, {}))

            im_names = []
            im_paths = []
            new_frames = []

            for image_id in range(1, len(images) + 1):
                new_figures = []
                image_name = str(image_id).zfill(g.image_name_length) + '.' + images_ext
                im_names.append(image_name)
                im_paths.append(os.path.join(imgs_path, image_name))
                video.write(cv2.imread(os.path.join(imgs_path, image_name)))

                for curr_obj_class_data in obj_classes_data:
                    frames_with_objects = curr_obj_class_data[0]
                    frames_without_objs_conf = curr_obj_class_data[1]

                    frame_object_coords = frames_with_objects[image_id]
                    for idx, coords in frame_object_coords.items():
                        if len(coords) != 4:
                            continue
                        if idx not in curr_obj_class_data[3].keys():
                            curr_frame_ranges = frames_without_objs_conf[idx]
                            if len(curr_frame_ranges) == 0:
                                curr_obj_class_data[3][idx] = sly.VideoObject(curr_obj_class_data[2])
                            else:
                                conf_tags = [VideoTag(conf_tag_meta,
                                                      frame_range=[curr_frame_range[0] - 1, curr_frame_range[1] - 1])
                                             for curr_frame_range in curr_frame_ranges]
                                curr_obj_class_data[3][idx] = sly.VideoObject(curr_obj_class_data[2],
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
                        figure = sly.VideoFigure(curr_obj_class_data[3][idx], geom, image_id - 1)
                        new_figures.append(figure)

                new_frame = sly.Frame(image_id - 1, new_figures)
                new_frames.append(new_frame)
                progress.iter_done_report()

            video.release()

            video_objects = []
            for obj_class_data in obj_classes_data:
                video_objects.extend(list(obj_class_data[3].values()))

            ann_progress = sly.Progress(f'Creating annotation for "{video_name}"', 1, app_logger)
            new_meta = sly.ProjectMeta(sly.ObjClassCollection(obj_classes))
            meta = meta.merge(new_meta)
            g.api.project.update_meta(new_project.id, meta.to_json())
            file_info = g.api.video.upload_paths(new_dataset.id, [video_name], [video_path])
            new_frames_collection = sly.FrameCollection(new_frames)
            new_objects = sly.VideoObjectCollection(video_objects)
            ann = sly.VideoAnnotation((img_size[1], img_size[0]), len(new_frames), objects=new_objects,
                                      frames=new_frames_collection)
            g.api.video.annotation.append(file_info[0].id, ann)
            ann_progress.iter_done_report()
    return meta


def start(archive_name, new_project, meta, conf_tag_meta, app_logger):
    if g.mot_dataset != g.custom_ds:
        if get_file_name(archive_name) in ['MOT16']:
            curr_mot_dir = os.path.join(g.storage_dir, g.train)
            curr_test_mot_dir = os.path.join(g.storage_dir, g.test)
        else:
            curr_mot_dir = os.path.join(g.storage_dir, get_file_name(archive_name))
            curr_test_mot_dir = os.path.join(curr_mot_dir, g.test)
        g.logger.info('Checking input MOT format')
        check_mot_format(curr_mot_dir)
        dataset_name = get_file_name(archive_name)
        import_dataset(new_project, dataset_name, curr_mot_dir, meta, conf_tag_meta, app_logger)
        if g.download_test_data:
            test_dataset_name = dataset_name + g.test_suffix
            import_test_dataset(new_project, test_dataset_name, curr_test_mot_dir, app_logger)
    else:
        mot_dirs = os.listdir(g.storage_dir)
        mot_dirs.remove(archive_name)
        for curr_dir in mot_dirs:
            curr_mot_dir = os.path.join(g.storage_dir, curr_dir)
            g.logger.info('Checking input MOT format')
            if len(os.listdir(curr_mot_dir)) > 1 or g.test not in os.listdir(curr_mot_dir):
                check_mot_format(curr_mot_dir)
            dataset_name = curr_dir
            import_dataset(new_project, dataset_name, curr_mot_dir, meta, conf_tag_meta, app_logger)
            if g.test in os.listdir(curr_mot_dir):
                test_dataset_name = dataset_name + g.test_suffix
                curr_test_mot_dir = os.path.join(curr_mot_dir, g.test)
                import_test_dataset(new_project, test_dataset_name, curr_test_mot_dir, app_logger)
