import picture_lib
import argparse
from filestore import repository
import fs
import subprocess

import logging
logging.basicConfig(level=logging.DEBUG)


def to_structured_info(raw_info):
    def kvgen():
        for line in raw_info.split('\n'):
            key, _, value = line.partition('=')
            yield key, value

    return dict(kvgen())


def get_raw_exif_info(stream):
    cmd = """identify -format %[EXIF:*] -"""
    proc = subprocess.Popen(cmd.split(), stdin=stream, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    return out


class ThumbFinder(object):
    def __init__(self, repo):
        self.thumb_by_picture = dict()
        self.repo = repo

    def rebuild_index(self):
        self.thumb_by_picture = dict()
        for thumb in self.repo.objects():
            metadata = eval(thumb.metadata)

            for picture in metadata['thumbnail']:
                if picture in ['size', 'format']:
                    continue
                self.thumb_by_picture[picture] = thumb.checksum

    def find_thumb(self, picture):
        return self.repo.get(self.thumb_by_picture[picture])


def update_exif_info(source, thumbs):
    src_repo = repository.Repository(fs.Directory(source))
    thumbs_repo = repository.Repository(fs.Directory(thumbs))

    finder = ThumbFinder(thumbs_repo)
    logging.info('building index')
    finder.rebuild_index()

    for picture in picture_lib.picture_objects(src_repo):
        thumb = finder.find_thumb(picture.checksum)
        metadata = eval(thumb.metadata)

        if not metadata['thumbnail'][picture.checksum].get('exif'):
            raw_info = get_raw_exif_info(picture.stream())
            exif_info = to_structured_info(raw_info)
            logging.info('%s update metadata', picture.checksum)
            metadata['thumbnail'][picture.checksum]['exif'] = exif_info
            thumb.metadata = repr(metadata)


def parse_args():
    parser = argparse.ArgumentParser(description='Add EXIF info to thumbnails')
    parser.add_argument('source', help='Source filestore')
    parser.add_argument('thumbs', help='Thumbs filestore')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    update_exif_info(args.source, args.thumbs)
