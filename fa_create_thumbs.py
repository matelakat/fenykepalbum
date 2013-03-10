import argparse
from filestore import repository
import fs
import subprocess
import StringIO
import picture_lib

import logging
logging.basicConfig(level=logging.DEBUG)


def save_thumb(stream, repo):
    cmd = "convert -resize 100x100 -auto-orient - gif:-"
    proc = subprocess.Popen(cmd.split(), stdin=stream, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    return repo.save(StringIO.StringIO(out))


def to_stream(obj):
    import os
    fname = os.path.join(obj.directory.root, obj.checksum)
    return open(fname, "rb")


def create_thumbs(source, dest):
    src = repository.Repository(fs.Directory(source))
    dst = repository.Repository(fs.Directory(dest))

    for picture in picture_lib.picture_objects(src):
        with to_stream(picture) as picture_stream:
            logging.info("saving thumb for %s", picture.checksum)
            thumb = save_thumb(picture_stream, dst)

            if thumb.metadata:
                logging.info("potential duplicate thumb")
                metadata = eval(thumb.metadata)
            else:
                metadata = dict(thumbnail=dict())

            metadata['thumbnail'][picture.checksum] = eval(picture.metadata)
            metadata['thumbnail']['size'] = 100
            metadata['thumbnail']['format'] = 'gif'

            thumb.metadata = repr(metadata)


def parse_args():
    parser = argparse.ArgumentParser(description='Create thumbnails')
    parser.add_argument('source', help='Source filestore')
    parser.add_argument('dest', help='Destination filestore')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    create_thumbs(args.source, args.dest)
