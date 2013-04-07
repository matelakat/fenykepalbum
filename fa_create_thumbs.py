import argparse
from filestore import repository
import fs
import subprocess
import picture_lib
import utils

import logging
logging.basicConfig(level=logging.DEBUG)


def to_stream(obj):
    import os
    fname = os.path.join(obj.directory.root, obj.checksum)
    return open(fname, "rb")


def create_thumbs(source, dest, size):
    size = int(size)
    src = repository.Repository(fs.Directory(source))
    dst = repository.Repository(fs.Directory(dest))

    for picture in picture_lib.picture_objects(src):
        with to_stream(picture) as picture_stream:
            logging.info("saving thumb for %s", picture.checksum)
            thumb = utils.save_thumb(picture_stream, dst, size)

            if thumb.metadata:
                logging.info("potential duplicate thumb")
                metadata = eval(thumb.metadata)
            else:
                metadata = dict(thumbnail=dict())

            metadata['thumbnail'][picture.checksum] = eval(picture.metadata)
            metadata['thumbnail']['size'] = size
            metadata['thumbnail']['format'] = 'gif'

            thumb.metadata = repr(metadata)


def parse_args():
    parser = argparse.ArgumentParser(description='Create thumbnails')
    parser.add_argument('source', help='Source filestore')
    parser.add_argument('dest', help='Destination filestore')
    parser.add_argument('--size', help='maximal size of thumb', default='100')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    create_thumbs(args.source, args.dest, args.size)
