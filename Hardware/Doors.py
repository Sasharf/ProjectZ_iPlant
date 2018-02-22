from random import randint
import sys
import time

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

class Doors:

   # stepPinsR = None
   # stepPinsL = None
    is_open = False
    door_movement_time = 800
    calibrate_time = 100
    left = 1
    Seq = [[1, 0, 0, 1],
           [1, 0, 0, 0],
           [1, 1, 0, 0],
           [0, 1, 0, 0],
           [0, 1, 1, 0],
           [0, 0, 1, 0],
           [0, 0, 1, 1],
           [0, 0, 0, 1]]

    stepCount = len(Seq)

    def __init__(self, left_door_pins, right_door_pins, is_open):
        self.stepPinsL = [int(x) for x in left_door_pins.split(" ")]
        self.stepPinsR = [int(x) for x in right_door_pins.split(" ")]
        self.is_open = is_open

        for pin in self.stepPinsR:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)

        for pin in self.stepPinsL:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)

    def isDoorsOpen(self):
        return self.is_open

    def moveDoors(self, side, door_move_time):
        if side == self.left:
            stepDirR = -1
            stepDirL = 1
        else:
            stepDirR = 1
            stepDirL = -1

        stepCounterL = 0
        stepCounterR = 0
        loopCounter = door_move_time

        try:
            while loopCounter > 0:
                loopCounter -= 1

                for pin in range(0, 4):
                    if self.Seq[stepCounterR][pin] != 0:
                        GPIO.output(self.stepPinsR[pin], True)
                    else:
                        GPIO.output(self.stepPinsR[pin], False)

                    if self.Seq[stepCounterL][pin] != 0:
                        GPIO.output(self.stepPinsL[pin], True)
                    else:
                        GPIO.output(self.stepPinsL[pin], False)

                    stepCounterR += stepDirR
                    stepCounterL += stepDirL

                if stepCounterR >= self.stepCount:
                    stepCounterR = 0
                if stepCounterR < 0:
                    stepCounterR = self.stepCount + stepDirR

                if stepCounterL >= self.stepCount:
                    stepCounterL = 0
                if stepCounterL < 0:
                    stepCounterL = self.stepCount + stepDirL

        except KeyboardInterrupt:
            print('error')
        for pin in self.stepPinsR:
            GPIO.output(pin, False)
        for pin in self.stepPinsL:
            GPIO.output(pin, False)
        return

    def calibrateUp(self):
        self.moveDoors(1, self.calibrate_time)
        return

    def calibrateDown(self):
        self.moveDoors(-1, self.calibrate_time)
        return

    def Doors(self):
        if not self.is_open:
            self.moveDoors(1, self.door_movement_time)
            self.is_open = True
        else:
            self.moveDoors(-1, self.door_movement_time)
            self.is_open = False

    def setDoorsStatus(self, is_open):
        self.is_open = is_open
        return
