import contextlib
from Tkinter import PhotoImage, Label, Tk, Canvas, NW, NE

import sys
import os


class Settings(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def first_third(self):
        return self.width / 3

    @property
    def second_third(self):
        return 2 * self.width / 3

    @property
    def v_first_third(self):
        return self.height / 3

    @property
    def v_second_third(self):
        return 2 * self.height / 3


class App(object):

    def __init__(self, canvas, settings, image_provider, catalog):
        self.canvas = canvas
        self.catalog = catalog
        self.photo = None
        self.image_provider = image_provider
        self.image = self.canvas.create_image(
            0,
            0,
            anchor=NW,
            image=self.photo)

        self.actual_image = 0
        self.settings = settings

        def vline(x):
            canvas.create_line(x, 0, x, settings.height)

        vline(settings.first_third)
        vline(settings.second_third)

        def hline(y):
            canvas.create_line(settings.first_third, y, settings.second_third, y)

        hline(settings.height / 3)
        hline(2 * settings.height / 3)

        self.caption = canvas.create_text(settings.width, 0, anchor=NE, font="Courier 10")

        self.category_mark = canvas.create_rectangle(
            0, 0, 0, 0, fill="red")

        self.update()

    def get_region(self, event):
        if event.x < self.settings.first_third:
            return "left"
        elif event.x > self.settings.second_third:
            return "right"
        else:
            if event.y <  self.settings.v_first_third:
                return "0"
            elif event.y >  self.settings.v_second_third:
                return "2"
            return "1"

    def update(self, update_photo=True, update_category=True):
        if update_photo:
            self.update_photo()
        if update_category:
            self.update_category()

    @contextlib.contextmanager
    def monitor_changes(self):
        photo_before = self.image_provider.identifier
        category_before = self.catalog.get_category_for(photo_before)
        result = dict()
        yield result

        if self.image_provider.identifier == photo_before:
            result['update_photo'] = False
        if category_before == self.catalog.get_category_for(self.image_provider.identifier):
            result['update_category'] = False

    def update_photo(self):
        self.photo = PhotoImage(file=self.image_provider.filename)
        w = self.photo.width()
        h = self.photo.height()

        self.canvas.itemconfigure(self.image, image=self.photo)
        x = (self.settings.width - w ) / 2
        y = (self.settings.height - h ) / 2
        self.canvas.coords(self.image, x, y)
        caption = "%s / %s [%s]" % (
            self.image_provider.index, self.image_provider.length,
            self.image_provider.identifier)
        self.canvas.itemconfigure(
            self.caption, text=caption)

    def update_category(self):
        category = self.catalog.get_category_for(self.image_provider.identifier)
        settings = self.settings
        offset = settings.height / 3
        coord_mapping = {
            '0': (settings.width / 18, settings.height / 9, settings.width / 9, 2 * settings.height / 9),
            '1': (settings.width / 18, offset + settings.height / 9, settings.width / 9, offset + 2 * settings.height / 9),
            '2': (settings.width / 18, 2 * offset + settings.height / 9, settings.width / 9, 2 * offset + 2 * settings.height / 9),
        }

        coords = coord_mapping.get(category, (0, 0, 0, 0))
        self.canvas.coords(self.category_mark, *coords)

    def clicked(self, event):
        with self.monitor_changes() as update_actions:
            region = self.get_region(event)
            category = None
            if region == "left":
                self.image_provider.prev()
            elif region == "right":
                self.image_provider.next()
            else:
                category = region

            self.catalog.set_category_for(self.image_provider.identifier, category)

        self.update(**update_actions)


class StaticImageProvider(object):
    def __init__(self):
        self.images = ['one.gif', 'two.gif', 'three.gif']
        self.actual_image = 0

    def next(self):
        self.actual_image += 1
        self.actual_image %= len(self.images)

    def prev(self):
        self.actual_image -= 1
        self.actual_image %= len(self.images)

    @property
    def filename(self):
        return self.images[self.actual_image]

    @property
    def index(self):
        return self.actual_image

    @property
    def length(self):
        return len(self.images)


class RepoImageProvider(object):
    def __init__(self, source, start_at, checksum_list=None):
        from filestore import repository
        import fs

        repo = repository.Repository(fs.Directory(source))
        if checksum_list:
            object_by_key = dict((x.checksum, x) for x in repo.objects())
            self.objects = [object_by_key[checksum] for checksum in checksum_list]
        else:
            self.objects = sorted(list(repo.objects()), key=lambda x:x.checksum)
        self.obj_idx = 0

        if start_at:
            for obj in self.objects:
                if obj.checksum == start_at:
                    break
                else:
                    self.obj_idx += 1

    @property
    def index(self):
        return self.obj_idx

    @property
    def length(self):
        return len(self.objects)

    def next(self):
        self.obj_idx += 1
        self.obj_idx %= len(self.objects)

    def prev(self):
        self.obj_idx -= 1
        self.obj_idx %= len(self.objects)

    @property
    def obj(self):
        return self.objects[self.obj_idx]

    @property
    def identifier(self):
        return self.obj.checksum

    @property
    def filename(self):
        import os
        return os.path.join(self.obj.directory.root, self.obj.checksum)


class InMemoryCatalog(object):
    def __init__(self, categories):
        self.categories = categories

    def get_category_for(self, identifier):
        return self.categories.get(identifier)

    def set_category_for(self, identifier, value):
        if value:
            self.categories[identifier] = value


class CategoryLog(object):

    def __init__(self, filename):
        self.filename = filename

    def wrap_catalog(self, catalog):

        class WrappedCatalog(object):
            def get_category_for(_self, identifier):
                return catalog.get_category_for(identifier)

            def set_category_for(_self, identifier, value):
                with open(self.filename, "a") as logfile:
                    if value:
                        logfile.write("%s %s\n" % (identifier, value))
                    else:
                        logfile.write("%s\n" % identifier)

                catalog.set_category_for(identifier, value)

        return WrappedCatalog()

    @property
    def entries(self):
        with open(self.filename, "rb") as f:
            for line in f:
                data = line.strip().split()
                identifier = data[0]
                if len(data) == 2:
                    category = data[1]
                else:
                    category = None

                yield identifier, category



def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Sort thumbnails')
    parser.add_argument('source', help='Source filestore')
    parser.add_argument('categories', help='File to record categories')
    parser.add_argument(
        '--checksum_list_file', help='File containing list of checksums to show',
        default=None)
    return parser.parse_args()


def load_checksums(checksum_list_file):
    checksums = []

    if checksum_list_file:
        with open(checksum_list_file, 'rb') as f:
            for line in f:
                checksums.append(line.strip())

    return checksums


def start_app(source, categories_file, checksum_list_file):
    root = Tk()
    settings = Settings(480, 320)
    canvas = Canvas(root, width=settings.width, height=settings.height)

    category_log = CategoryLog(categories_file)
    categories = dict()
    last_identifier = None

    for identifier, category in category_log.entries:
        last_identifier = identifier
        if category:
            categories[identifier] = category

    catalog = InMemoryCatalog(categories)

    logging_catalog = category_log.wrap_catalog(catalog)

    app = App(
        canvas, settings,
        RepoImageProvider(source, last_identifier, load_checksums(checksum_list_file)),
        logging_catalog)

    canvas.bind("<Button-1>", app.clicked)
    canvas.place(x=0, y=0)
    root.mainloop()

if __name__ == "__main__":
    args = parse_args()
    start_app(args.source, args.categories, args.checksum_list_file)
