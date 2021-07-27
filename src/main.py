import os
import shutil
import dl_progress
import requests
import globals as g
import supervisely_lib as sly
from supervisely_lib.annotation.tag_meta import TagValueType
from supervisely_lib.io.fs import download, file_exists

import mot_importer


@g.my_app.callback("import_mot_format")
@sly.timeit
def import_mot_format(api: sly.Api, task_id, context, state, app_logger):
    new_project = api.project.create(g.WORKSPACE_ID, g.project_name, type=sly.ProjectType.VIDEOS,
                                     change_name_if_conflict=True)

    conf_tag_meta = sly.TagMeta(g.conf_tag_name, TagValueType.NONE)
    meta = sly.ProjectMeta(tag_metas=sly.TagMetaCollection([conf_tag_meta]))
    api.project.update_meta(new_project.id, meta.to_json())

    for ARH_NAME, LINK in zip(g.ARH_NAMES, g.LINKS):
        archive_path = os.path.join(g.storage_dir, ARH_NAME)
        if g.LINKS[0]:
            if not file_exists(archive_path):
                response = requests.head(LINK, allow_redirects=True)
                sizeb = int(response.headers.get('content-length', 0))
                progress_cb = dl_progress.get_progress_cb(g.api, task_id, f"Download archive {ARH_NAME}", sizeb, is_size=True)
                download(LINK, archive_path, g.my_app.cache, progress=progress_cb)
        else:
            file_size = api.file.get_info_by_path(g.team_id, g.ds_path).sizeb
            progress_download_cb = dl_progress.get_progress_cb(g.api,
                                                                  g.task_id,
                                                                  f'Download "{os.path.basename(os.path.normpath(g.ds_path))}"',
                                                                  total=file_size,
                                                                  is_size=True)
            api.file.download(g.TEAM_ID, g.ds_path, archive_path, progress_cb=progress_download_cb)
        try:
            shutil.unpack_archive(archive_path, g.storage_dir)
        except Exception('Unknown archive format {}'.format(ARH_NAME)):
            g.my_app.stop()

        mot_importer.start(ARH_NAME, new_project, meta, conf_tag_meta, app_logger)
    g.my_app.stop()


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": g.TEAM_ID,
        "WORKSPACE_ID": g.WORKSPACE_ID
    })
    g.my_app.run(initial_events=[{"command": "import_mot_format"}])


if __name__ == '__main__':
    sly.main_wrapper("main", main)
