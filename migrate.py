import argparse
from filestore import repository
import fs
import subprocess
import StringIO

import logging
logging.basicConfig(level=logging.DEBUG)


def migrate(source):
    src = repository.Repository(fs.Directory(source))
    for obj in src.objects():
        try:
            metadata = eval(obj.metadata)
        except:
            logging.info('%s: bad metadata: %s', obj.checksum, obj.metadata)
            continue

        if metadata.get('thumbnail'):
            logging.info('%s: already at version 1', obj.checksum)
            continue

        thumb_for = metadata['thumb_for']
        del metadata['thumb_for']

        new_metadata = dict(thumbnail={ thumb_for : metadata })
        obj.metadata = repr(new_metadata)


def parse_args():
    parser = argparse.ArgumentParser(description='Migrate metadata')
    parser.add_argument('source', help='Filestore')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    migrate(args.source)
