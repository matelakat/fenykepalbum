# Example:
#
# python list_images.py http://192.168.0.3/repo/ > new_image_types.list


import argparse
import urllib2
import re
import datetime


def get_args():
    parser = argparse.ArgumentParser(
        description="Generate an ordered list of new-type pictures")
    parser.add_argument('httpbase', help='Base of webserver serving repository')
    return parser.parse_args()


def list_files(httpbase):
    prog = re.compile('^.*href="(?P<fname>[^"]*)".*$')
    f = urllib2.urlopen(httpbase)
    for line in f:
        match = prog.match(line.strip())
        if match:
            yield match.group('fname')
    f.close()


def load_metadata(url):
    f = urllib2.urlopen(url)
    contents = f.read()
    f.close()

    return eval(contents)


def print_metadata(url):
    metadata = load_metadata(url)

    if metadata.get('type') == 'picture':
        exif = metadata['exif']
        date_field = exif['exif:DateTimeOriginal']
        date = datetime.datetime.strptime(date_field, "%Y:%m:%d %H:%M:%S")
        print date.strftime('%Y-%m-%d_%H:%M:%S'), metadata['thumbs']['320'], url
        assert len(metadata.keys()) == 3


def to_url(base, fname):
    return (base if base.endswith('/') else base + '/') + fname


def main(args):
    for fname in list_files(args.httpbase):
        if fname.endswith('.metadata'):
            print_metadata(to_url(args.httpbase, fname))


if __name__ == "__main__":
    main(get_args())
