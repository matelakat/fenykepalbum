from Tkinter import PhotoImage, Label, Tk, Canvas, NW
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

    def __init__(self, canvas, settings, image_provider, stream):
        self.canvas = canvas
        self.stream = stream
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

        self.update_image()

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

    def update_image(self):
        self.photo = PhotoImage(file=self.image_provider.filename)
        w = self.photo.width()
        h = self.photo.height()

        self.canvas.itemconfigure(self.image, image=self.photo)
        x = (self.settings.width - w ) / 2
        y = (self.settings.height - h ) / 2
        self.canvas.coords(self.image, x, y)

    def clicked(self, event):
        region = self.get_region(event)
        self.stream.write(self.image_provider.identifier)
        if region == "left":
            self.image_provider.prev()
        elif region == "right":
            self.image_provider.next()
        else:
            self.stream.write(" " + region)

        self.stream.write("\n")

        self.update_image()


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


class RepoImageProvider(object):
    def __init__(self, source, start_at):
        from filestore import repository
        import fs

        repo = repository.Repository(fs.Directory(source))
        self.objects = sorted(list(repo.objects()), key=lambda x:x.checksum)
        self.obj_idx = 0

        if start_at:
            for obj in self.objects:
                if obj.checksum == start_at:
                    break
                else:
                    self.obj_idx += 1

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


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='Sort thumbnails')
    parser.add_argument('source', help='Source filestore')
    parser.add_argument('categories', help='File to record categories')
    return parser.parse_args()


def start_app(source, categories):
    root = Tk()
    settings = Settings(480, 320)
    canvas = Canvas(root, width=settings.width, height=settings.height)

    last = None
    try:
        with open(categories, "rb") as f:
            for line in f:
                pass

        last = line.strip().split()[0]
    except:
        pass

    print last

    with open(categories, "a") as f:
        app = App(canvas, settings, RepoImageProvider(source, last), f)
        canvas.bind("<Button-1>", app.clicked)
        canvas.place(x=0, y=0)
        root.mainloop()

if __name__ == "__main__":
    args = parse_args()
    start_app(args.source, args.categories)
