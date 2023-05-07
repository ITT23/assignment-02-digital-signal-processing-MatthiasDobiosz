import sys
import pyaudio
import numpy as np
import pyglet
from pyglet import clock, shapes
from LevelBuilder import LevelBuilder
from AudioSetup import CHUNK_SIZE, FORMAT, CHANNELS, RATE, prompt_device
import os

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800

backgroundImagePath = os.path.normpath("Images/Pixel_Background.jpg")
backgroundImage = pyglet.image.load(backgroundImagePath)

# setup pyaudio and pyglet window
p = pyaudio.PyAudio()
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

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


class Game:

    def __init__(self):
        self.radius = 20

        # min and max frequency that maps to coordinate boundaries
        self.minFreq = 80
        self.maxFreq = 240

        # Store last frequency
        self.frequency = None
        # MovementSpeed in Y-Axis
        self.movementRate = 5
        self.levelBuilder = LevelBuilder()
        self.score = 0
        self.gameOver = False

        self.color = (55,255,55)
        self.x = self.radius
        self.y = self.levelBuilder.getLevelStartPoint()
        self.shape = shapes.Circle(x=self.x, y=self.y, radius=self.radius, segments=20,
                                   color=self.color)

    # Convert frequency to appropriate pixel value
    def convertToPixels(self, frequency):
        if frequency > self.maxFreq:
            frequency = self.maxFreq
        diff = self.maxFreq - frequency
        return WINDOW_HEIGHT - diff * (
                WINDOW_HEIGHT / (self.maxFreq - self.minFreq))

    # Main Method to get the main frequency and translate it into movement
    def update(self, delta_time):
        peak = get_main_frequency(100000)
        if peak is not None and peak > 1:
            if self.frequency is None:
                self.frequency = peak
            else:
                if peak > self.frequency:
                    if self.y < WINDOW_HEIGHT - self.radius:
                        self.y += self.movementRate
                        self.frequency = peak
                elif peak < self.frequency:
                    if self.y > self.radius:
                        self.y -= self.movementRate
                        self.frequency = peak
                else:
                    frequencyPosition = self.convertToPixels(peak)
                    if self.y > frequencyPosition:
                        self.y -= self.movementRate
                        self.frequency = peak
                    elif self.y < frequencyPosition:
                        if self.y < WINDOW_HEIGHT - self.radius:
                            self.y += self.movementRate
                            self.frequency = peak

        self.x += 1
        self.shape = shapes.Circle(x=self.x, y=self.y, radius=self.radius, segments=20,
                                   color=self.color)

        # reset level when circle out of window
        if self.x == WINDOW_WIDTH + self.radius:
            self.resetLevel()

    def draw(self):
        if not self.gameOver:
            backgroundImage.blit(0, 0)
            self.drawLabels()
            self.updateScore()
            self.levelBuilder.draw()
            self.shape.draw()
        else:
            self.drawGameOverScreen()

    # reset the whole game
    def reset(self):
        self.gameOver = False
        self.score = 0
        self.levelBuilder.reset()
        self.x = self.radius
        self.y = WINDOW_HEIGHT / 2

    def updateScore(self):
        if not self.gameOver:
            if self.x < len(self.levelBuilder.points):
                ball_pos = int(self.y)
                hitrange = self.levelBuilder.points[int(self.x)]
                if ball_pos in hitrange:
                    self.score += 1
                    self.color = (55,255,55)
                else:
                    self.color = (255,55,55)

    def resetLevel(self):
        if self.levelBuilder.currentLevel < 3:
            self.levelBuilder.level_up()
            self.x = 0
            self.y = self.levelBuilder.getLevelStartPoint()
        else:
            self.endGame()

    # display current Level and Score
    def drawLabels(self):
        level = '1' if self.levelBuilder.currentLevel == 1 else '2' if self.levelBuilder.currentLevel == 2 else '3'
        pyglet.text.Label(
            'Level: ' + str(level),
            font_name='Times New Roman',
            font_size=18,
            x=10, y=100,
            anchor_x='left', anchor_y='center').draw()
        pyglet.text.Label(
            'Score: ' + str(self.score),
            font_name='Times New Roman',
            font_size=18,
            x=10, y=150,
            anchor_x='left', anchor_y='center').draw()

    def endGame(self):
        self.gameOver = True
        self.drawGameOverScreen()

    def drawGameOverScreen(self):
        pyglet.text.Label('Game Over',
                          font_name='Times New Roman',
                          font_size=36,
                          x=WINDOW_WIDTH / 2,
                          y=WINDOW_HEIGHT / 2,
                          anchor_x='center',
                          anchor_y='center').draw()
        pyglet.text.Label(
            'final Score: ' + str(self.score) + "/" + str(self.levelBuilder.levelCount * WINDOW_WIDTH),
            font_name='Times New Roman',
            font_size=18,
            x=WINDOW_WIDTH / 2,
            y=WINDOW_HEIGHT / 2 - 50,
            anchor_x='center',
            anchor_y='center').draw()
        pyglet.text.Label('Press 2 to reset the game',
                          font_name='Times New Roman',
                          font_size=18,
                          x=WINDOW_WIDTH / 2,
                          y=WINDOW_HEIGHT / 2 - 100,
                          anchor_x='center',
                          anchor_y='center').draw()
        pyglet.text.Label('Press 3 to end the game',
                          font_name='Times New Roman',
                          font_size=18,
                          x=WINDOW_WIDTH / 2,
                          y=WINDOW_HEIGHT / 2 - 150,
                          anchor_x='center',
                          anchor_y='center').draw()


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


# init game
game = Game()


@window.event
def on_draw():
    window.clear()
    game.draw()


@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key._2:
        game.reset()
    elif symbol == pyglet.window.key._3:
        sys.exit()


clock.schedule_interval(game.update, 0.01)

pyglet.app.run()
