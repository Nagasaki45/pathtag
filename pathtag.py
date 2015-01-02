import os
import argparse
import logging

from mutagen.easyid3 import EasyID3

logger = logging.getLogger(__name__)


class PathError(Exception):
    pass


def path_to_tags(path):
    path_as_list = path.split('/')
    if len(path_as_list) > 2 or path == '':
        raise PathError()
    artist = path_as_list.pop(0)
    album = path_as_list.pop() if path_as_list else 'Unknown'
    return {'artist': artist, 'album': album}


def update_tags(filepath, new_tags):
    try:
        tagfile = EasyID3(filepath)
    except OSError as e:
        logger.info("mutagen failed to load '{}'".format(filepath))
        return
    for key, val in new_tags.items():
        tagfile[key] = [val]
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
