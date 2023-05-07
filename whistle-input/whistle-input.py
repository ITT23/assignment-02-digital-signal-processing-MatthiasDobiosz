import pyaudio
import numpy as np
import pyglet
from pyglet import clock, shapes
from pynput.keyboard import Controller
from AudioSetup import CHUNK_SIZE, FORMAT, CHANNELS, RATE, prompt_device

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400

# setup pyaudio and pyglet window
p = pyaudio.PyAudio()
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

keyboard = Controller()

# Get input device per prompt
input_device = prompt_device(p)

# open audio input stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=False,
                input=True,
                frames_per_buffer=CHUNK_SIZE,
                input_device_index=input_device)


# Main Controller for the Rectangle Stack
class StackController:

    def __init__(self):
        self.lastPeak = None
        self.peakCounter = 0
        self.direction = None
        self.peaks = []

    def update(self, delta_time):
        peak = get_main_frequency(100000)
        if peak is not None and peak > 1:
            self.peaks.append(peak)
        else:
            if len(self.peaks) > 10:
                self.eval_peaks()
            self.peaks = []

    # If the start and end of the list are the same it should not be counted
    # as ascending or descending in case of all inputs being the same number
    def is_same(self, peaks):
        if peaks[0] == peaks[len(peaks) - 1]:
            return True
        return False

    # check if input is ascending or descending
    def eval_peaks(self):
        if not self.is_same(self.peaks):
            if isAscending(self.peaks):
                go_up()
            elif isDescending(self.peaks):
                go_down()


# Check if List is Ascending/Descending
# https://stackoverflow.com/questions/19916143/how-do-you-know-if-your-list-is-ascending-in-python

def isAscending(list):
    # Allow 1 Wrong Input to make the detection easier
    missed = 0
    previous = list[0]
    for number in list:
        if number < previous:
            if missed == 0:
                missed += 1
            else:
                return False
        previous = number
    return True


def isDescending(list):
    # Allow 1 Wrong Input to make the detection easier
    missed = 0
    previous = list[0]
    for number in list:
        if number > previous:
            if missed == 0:
                missed += 1
            else:
                return False
        previous = number
    return True


class Rectangle:
    rectangles = []

    def __init__(self, count, idx, width):
        self.width = width
        self.count = count
        self.gap = (WINDOW_HEIGHT / count) / 5
        self.id = idx
        self.x = WINDOW_WIDTH / 2 - self.width / 2
        self.y = (WINDOW_HEIGHT / count) * self.id
        self.height = WINDOW_HEIGHT / count - self.gap
        self.active = True if count / 2 == self.id else False
        self.color = (175, 175, 175) if self.active else (255, 255, 255)
        self.shape = shapes.Rectangle(x=self.x, y=self.y, width=self.width,
                                      height=self.height, color=self.color)

    # Change color if rectangle is active
    def setActive(self, active):
        self.active = active
        if active:
            self.color = (175, 175, 175)
        else:
            self.color = (255, 255, 255)

        self.shape = shapes.Rectangle(x=self.x, y=self.y, width=self.width,
                                      height=self.height, color=self.color)

    def draw(self):
        self.shape.draw()


def create_Rectangles(delta_time):
    for x in range(0, 10):
        Rectangle.rectangles.append(Rectangle(10, x, 50))


def draw_Rectangles():
    for rectangle in Rectangle.rectangles:
        rectangle.draw()

# change active rectangle and trigger key input upwards
def go_up():
    keyboard.press('w')
    active_id = None
    for x in range(0, len(Rectangle.rectangles)):
        currRectangle = Rectangle.rectangles[x]
        if currRectangle.active and (x != len(Rectangle.rectangles) - 1):
            active_id = currRectangle.id
            currRectangle.setActive(False)
        elif active_id is not None:
            if x - active_id == 1:
                currRectangle.setActive(True)


# change active rectangle and trigger key input downwards
def go_down():
    keyboard.press('s')
    active_id = None
    for x in range(len(Rectangle.rectangles) - 1, -1, -1):
        currRectangle = Rectangle.rectangles[x]
        if currRectangle.active and x != 0:
            active_id = currRectangle.id
            currRectangle.setActive(False)
        elif active_id is not None:
            if active_id - x == 1:
                currRectangle.setActive(True)


# Method to read the data stream and return the main frequency
# threshold = threshold value for sound volume to cut out hissing
def get_main_frequency(threshold):
    # Read audio data from stream
    data = stream.read(CHUNK_SIZE)

    # Convert audio data to numpy array
    data = np.frombuffer(data, dtype=np.int16)

    sp = np.abs(np.fft.fft(data))

    freqs = np.fft.fftfreq(len(data), d=1 / RATE)

    mask = freqs >= 0

    maxsp = np.argmax(sp[mask])

    # only return value if a sound is above the threshold
    if np.max(sp[mask]) > threshold:
        return freqs[maxsp]
    else:
        return None


@window.event
def on_draw():
    window.clear()
    draw_Rectangles()


stackController = StackController()

clock.schedule_once(create_Rectangles, 0)
clock.schedule_interval(stackController.update, 0.01)

pyglet.app.run()
