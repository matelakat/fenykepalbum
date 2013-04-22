import argparse
from list_images import list_files, to_url, load_metadata
import logging
import pickle

logging.basicConfig(level=logging.DEBUG)


def main(args):
    metadatas = dict()
    for fname in list_files(args.httpbase):
        if fname.endswith('.metadata'):
            url = to_url(args.httpbase, fname)

            hashname = fname[:-len('.metadata')]
            metadatas[hashname] = dict(
                data=load_metadata(url),
                url=url)

            logging.debug('%s loaded as %s', url, hashname)

    logging.info('Saving metadatas to %s', args.output)

    with open(args.output, 'wb') as output:
        pickle.dump(metadatas, output)


def get_args():
    parser = argparse.ArgumentParser(
        description="Given an URL, load all metadata, and pickle it to a given file")
    parser.add_argument('httpbase', help='Base of webserver serving repository')
    parser.add_argument('output', help='Output file for the pickled metadata')
    return parser.parse_args()


if __name__ == "__main__":
    main(get_args())
