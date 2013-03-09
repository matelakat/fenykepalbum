import argparse
from filestore import repository
import fs
import subprocess
import StringIO

import logging
logging.basicConfig(level=logging.DEBUG)


def save_thumb(stream, repo):
    cmd = "convert -resize 100x100 -auto-orient - gif:-"
    proc = subprocess.Popen(cmd.split(), stdin=stream, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    return repo.save(StringIO.StringIO(out))


def is_picture(metadata):
    try:
        md = eval(metadata)
        for source in md['sources']:
            if source['fname'].lower().endswith(".jpg"):
                return True
    except:
        pass

    return False


def picture_objects(repository):
    for obj in repository.objects():
        metadata = obj.metadata
        if is_picture(metadata):
            yield obj


def to_stream(obj):
    import os
    fname = os.path.join(obj.directory.root, obj.checksum)
    return open(fname, "rb")


def create_thumbs(source, dest):
    src = repository.Repository(fs.Directory(source))
    dst = repository.Repository(fs.Directory(dest))

    for picture in picture_objects(src):
        with to_stream(picture) as picture_stream:
            logging.info("processing %s", picture.checksum)
            thumb = save_thumb(picture_stream, dst)
            thumb.metadata = repr(dict(eval(picture.metadata), thumb_for=picture.checksum))


def parse_args():
    parser = argparse.ArgumentParser(description='Create thumbnails')
    parser.add_argument('source', help='Source filestore')
    parser.add_argument('dest', help='Destination filestore')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    create_thumbs(args.source, args.dest)
