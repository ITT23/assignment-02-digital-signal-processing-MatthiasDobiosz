import numpy as np
import pyglet
from pyglet import shapes


# LevelBuilder class that generates the Pixels for the current level
class LevelBuilder:

    def __init__(self):
        self.frequency = 1
        self.amplitude = 1
        self.sample_length = 1
        self.sampling_rate = 800
        self.shapes = []
        self.points = []
        self.outlineColor = (64, 224, 208)
        self.outlineWidth = 5
        self.areaColor = (255, 255, 255)
        self.batch = self.setup_wave()
        self.currentLevel = 1
        self.levelCount = 3

    # get center of first narrow to position the ball
    def getLevelStartPoint(self):
        firstpoint = self.points[0]
        centerIdx = int((len(firstpoint) - 1)/2)
        return firstpoint[centerIdx]

    # reset to level 1
    def reset(self):
        self.currentLevel = 1
        self.frequency = 1
        self.batch = self.setup_wave()

    def level_up(self):
        if self.currentLevel == 1:
            self.currentLevel = 2
            self.frequency = 2
            self.batch = self.setup_wave()
        elif self.currentLevel == 2:
            self.currentLevel = 3
            self.frequency = 3
            self.batch = self.setup_wave()


    # Method that generates the points for the sine waves
    def setup_wave(self):
        # Clear Arrays
        self.shapes = []
        self.points = []

        x = np.arange(0, self.sample_length, 1 / self.sampling_rate)
        batch = pyglet.graphics.Batch()

        # create 2 sine waves
        y1 = 200 * self.amplitude * np.sin(self.frequency * 2 * np.pi * x)
        y2 = (200 * self.amplitude * np.sin(
            self.frequency * 2 * np.pi * x)) - 150

        for y in range(0, len(y1)):
            # Create a circle for each point in the sinewave
            p1 = y1[y] + 400
            p2 = y2[y] + 400
            point1 = shapes.Circle(x=y, y=p1, radius=self.outlineWidth,
                                   color=self.outlineColor,
                                   batch=batch)
            point2 = shapes.Circle(x=y, y=p2, radius=self.outlineWidth,
                                   color=self.outlineColor,
                                   batch=batch)

            # Fill the space between the 2 waves
            line = shapes.Line(x=y, y=p1 - 1, x2=y, y2=p2 + 1, width=1,
                               color=self.areaColor, batch=batch)

            # store all points and ranges to check scoring later
            self.shapes.append(point1)
            self.shapes.append(point2)
            self.shapes.append(line)
            self.points.append(range(int(p2), int(p1)))

        return batch

    def draw(self):
        self.batch.draw()
