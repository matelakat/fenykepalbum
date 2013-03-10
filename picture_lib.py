def _is_picture(metadata):
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
        if _is_picture(metadata):
            yield obj



