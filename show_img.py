from Tkinter import PhotoImage, Label, Tk, Canvas, NW

class Settings(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height


class App(object):

    def __init__(self, canvas, settings):
        self.canvas = canvas
        self.photo = None
        self.image = self.canvas.create_image(
            0,
            0,
            anchor=NW,
            image=self.photo)

        self.actual_image = 0
        self.images = ['one.gif', 'two.gif', 'three.gif']
        self.settings = settings

    def next_image(self):
        self.actual_image += 1
        self.actual_image %= len(self.images)

    def prev_image(self):
        self.actual_image -= 1
        self.actual_image %= len(self.images)

    def get_region(self, event):
        if event.x < self.settings.width / 3:
            return "left"
        elif event.x > 2 * self.settings.width /3:
            return "right"
        return "center"

    def update_image(self):
        self.photo = PhotoImage(file=self.images[self.actual_image])
        w = self.photo.width()
        h = self.photo.height()

        self.canvas.itemconfigure(self.image, image=self.photo)
        x = (self.settings.width - w ) / 2
        y = (self.settings.height - h ) / 2
        self.canvas.coords(self.image, x, y)

    def clicked(self, event):
        region = self.get_region(event)
        if region == "left":
            self.prev_image()
        elif region == "right":
            self.next_image()
        else:
            print "menu"

        self.update_image()


def start_app():
    root = Tk()
    settings = Settings(480, 320)
    canvas = Canvas(root, width=settings.width, height=settings.height)
    app = App(canvas, settings)
    canvas.bind("<Button-1>", app.clicked)
    canvas.place(x=0, y=0)
    root.mainloop()

if __name__ == "__main__":
    start_app()
