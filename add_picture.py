"""Read lines from standard input. Each line is a picture file, it is uploaded
to the repository, exif data extracted, thumbnail created, added"""

import argparse
from filestore import repository
import fs
import sys
import utils


def get_args():
    parser = argparse.ArgumentParser(
        description="Load a picture to the filestore")
    parser.add_argument('fname', help='Filename to use')
    parser.add_argument('filestore', help='Filestore repository to use')
    parser.add_argument('thumbsize', help='Size of the thumb')
    return parser.parse_args()


def main(args):
    repo = repository.Repository(fs.Directory(args.filestore))

    fname = args.fname
    thumbsize = args.thumbsize

    with open(fname, 'rb') as stream:
        obj = repo.save(stream)

        stream.seek(0)
        metadata = (
            obj.metadata and eval(obj.metadata)) or dict()

        metadata['type'] = 'picture'
        metadata['exif'] = utils.to_structured_info(
            utils.get_raw_exif_info(stream))

        stream.seek(0)
        thumb = utils.save_thumb(stream, repo, thumbsize)

        metadata['thumbs'] = metadata.get('thumbs', dict())
        metadata['thumbs'][thumbsize] = thumb.checksum
        obj.metadata = repr(metadata)

if __name__ == "__main__":
    main(get_args())
