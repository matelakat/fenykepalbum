import subprocess
import StringIO


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


def save_thumb(stream, repo, size):
    size_option = "%sx%s" % (size, size)
    cmd = "convert -resize %s -auto-orient - gif:-" % size_option
    proc = subprocess.Popen(cmd.split(), stdin=stream, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    return repo.save(StringIO.StringIO(out))
