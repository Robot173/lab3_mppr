from tkinter import *
import numpy


WIDTH = 28 # размер изображения 28 на 28
HEIGHT = 28

SIZE = 25 #размер создаваемого квадратного окна

K = 0.7 #толщина линии нарисованной цифры

class MatrixInput(object):
    def __init__(self, classifier):
        self.callback = classifier

        self.root = Tk()
        self.root.resizable(0, 0)
        self.canvas = Canvas(self.root, bg="blue", width=WIDTH * SIZE, height=HEIGHT * SIZE)
        self.canvas.configure(cursor="crosshair")
        self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>", self.press)
        self.canvas.bind("<B1-Motion>", self.motion)
        self.canvas.bind("<ButtonRelease-1>", self.release)
        self.root.bind("<space>", self.clear)

        self.matrix = numpy.zeros((WIDTH, HEIGHT), dtype="float32")
        self.pressed = False
        self.last_x = 0
        self.last_y = 0

        self.root.mainloop()

    def press(self, event):
        self.pressed = True
        self.last_x = event.x
        self.last_y = event.y

    def release(self, event):
        self.pressed = False
        matrix = numpy.array([list(map(lambda x: x * 0.8, self.matrix))])
        matrix = self.matrix.reshape(28, 28)
        prediction = self.callback(matrix.reshape(1, -1))
        a = str(prediction.pop(10))
        self.root.title('(' + a + ')  ' + '  '.join(
            map(lambda p: "%d: %02d" % (p[1], int(100 * p[0])), zip(prediction, range(10)))))

    def redraw(self):
        self.canvas.delete("all")
        for x in range(WIDTH):
            for y in range(HEIGHT):
                v = int(self.matrix[y][x] * 255)
                self.canvas.create_rectangle(
                    x * SIZE,
                    y * SIZE,
                    (x + 1) * SIZE +1,
                    (y + 1) * SIZE+1,
                    fill="#%02x%02x%02x" % (255 - v, 255 - v, 255 - v,)
                )

    # pixel coords
    def add_pixel(self, x, y, value):
        if value <= 0: return
        self.matrix[x][y] += value
        if self.matrix[x][y] > 1:
            self.matrix[x][y] = 1

    # pixel coords # тень около черных пикселей
    def add_circle(self, x, y):
        for i in range(-2, 3):
            for j in range(-2, 3):
                X = x + i
                Y = y + j
                if X < 0 or X >= WIDTH or Y < 0 or Y >= HEIGHT:
                    continue
                self.add_pixel(Y, X, 1 - K * (i * i + j * j) ** 0.5)

    # raw coords
    def drawline(self, x1, y1, x2, y2):
        x1 = int(x1 / SIZE)
        y1 = int(y1 / SIZE)
        x2 = int(x2 / SIZE)
        y2 = int(y2 / SIZE)

        dx = x2 - x1
        dy = y2 - y1

        if abs(dy) > abs(dx) and abs(dy) > 0:
            if y1 > y2:
                x1, x2 = x2, x1
                y1, y2 = y2, y1
            s = dx / dy
            x = x1
            for y in range(y1, y2):
                self.add_circle(int(x), int(y))
                x += s

        elif abs(dy) <= abs(dx) and abs(dx) > 0:
            if x1 > x2:
                x1, x2 = x2, x1
                y1, y2 = y2, y1
            s = dy / dx
            y = y1
            for x in range(x1, x2):
                self.add_circle(int(x), int(y))
                y += s

    def motion(self, event):
        if not self.pressed: return

        self.drawline(self.last_x, self.last_y, event.x, event.y)
        self.last_x = event.x
        self.last_y = event.y
        self.redraw()

    def clear(self, event):
        self.matrix = numpy.zeros((WIDTH, HEIGHT), dtype="float32")
        self.redraw()
