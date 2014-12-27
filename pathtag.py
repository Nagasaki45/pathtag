import os
import argparse
import logging

import taglib

logger = logging.getLogger(__name__)


class PathError(Exception):
    pass


def path_to_tags(path):
    path_as_list = path.split('/')
    if len(path_as_list) > 2 or path == '':
        raise PathError()
    artist = path_as_list.pop(0)
    album = path_as_list.pop() if path_as_list else 'Unknown'
    return {'ARTIST': artist, 'ALBUM': album}


def update_tags(filepath, new_tags):
    try:
        tagfile = taglib.File(filepath)
    except OSError as e:
        logger.info('asd')
        return
    tagfile.tags.update(new_tags)
    tagfile.save()


def fix_files_metadata(basedir):
    for path, dirs, filenames in os.walk(basedir):
        relpath = os.path.relpath(path, basedir)
        try:
            new_tags = path_to_tags(relpath)
        except PathError:
            continue
        for filename in filenames:
            update_tags(os.path.join(path, filename), new_tags)


def get_cmd_args():
    desc = 'Fix music metadata according to directory structure'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('basedir', help='path to the base directory')
    return parser.parse_args()


def main():
    args = get_cmd_args()
    fix_files_metadata(args.basedir)


if __name__ == '__main__':
    main()
