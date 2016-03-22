import pexpect
import numpy as np
import math
from fltk import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


GO_BLACK = True
GO_WHITE = False





class GoEngine():
    def __init__(self, user_color=GO_BLACK):
        self.user_color = user_color
        self.list_black = []
        self.list_white = []
        self.cap_black = 0
        self.cap_white = 0
        self.program = None

        self.this_turn = GO_BLACK
        self.last_stone = None

    def startEngine(self):
        self.program = pexpect.spawn('./gnugo --mode gtp')

    def stopEngine(self):
        self.program.sendline('quit')

    def clearGame(self):
        self.program.sendline('clear_board')

    def engineMove(self):
        if self.user_color != self.this_turn:
            self.program.sendline('genmove ' + GoEngine.GetColorString(self.this_turn))
            self.program.expect('\r\n\r\n', 10)

            self.this_turn = not self.this_turn

    def userMove(self, posstr):
        if self.user_color == self.this_turn:
            self.program.sendline('play ' + GoEngine.GetColorString(self.this_turn) + ' ' + posstr)
            self.program.expect('\r\n\r\n', 1)

            self.this_turn = not self.this_turn

    @staticmethod
    def PosstrToPos(posstr):
        x = ord(posstr[0]) - 75
        if x < -1:
            x += 1
        y = int(posstr[1:]) - 10
        return [x, y]

    @staticmethod
    def GetColorString(color_num):
        if color_num == GO_BLACK:
            return 'b'
        elif color_num == GO_WHITE:
            return 'w'

    def GetStatus(self):
        self.GetStones(GO_BLACK)
        self.GetStones(GO_WHITE)
        self.GetCaptureStones(GO_BLACK)
        self.GetCaptureStones(GO_WHITE)

    def GetStones(self, color):
        self.program.sendline('list_stones ' + self.GetColorString(color))
        self.program.expect('\r\n\r\n', 1)
        if color == GO_BLACK:
            del self.list_black[:]
            self.list_black = [self.PosstrToPos(posstr) for posstr in self.program.before.split()[3:]]
        elif color == GO_WHITE:
            del self.list_white[:]
            self.list_white = [self.PosstrToPos(posstr) for posstr in self.program.before.split()[3:]]

    def GetCaptureStones(self, color):
        self.program.sendline('captures ' + self.GetColorString(color))
        self.program.expect('\r\n\r\n', 1)
        if color == GO_BLACK:
            self.cap_black = int(self.program.before.split()[3])
        elif color == GO_WHITE:
            self.cap_white = int(self.program.before.split()[3])


class GoWindow(Fl_Gl_Window):
    def __init__(self):
        Fl_Gl_Window.__init__(self, 200, 200, 800, 800)

        self.engine = GoEngine()
        self.engine.startEngine()
        self.black_stones = []
        self.white_stones = []

    # def initGL(self):
    #     pass

    def draw(self):
        glClearColor(240./255., 180./255., 60./255., 1.)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        glScalef(1./10., 1./10., 1./10.)
        # glScalef(21., 21., 21.)
        glColor3f(0., 0., 0.)
        glBegin(GL_LINES)
        for i in range(-9, 10):
            glVertex2f(i, 9.)
            glVertex2f(i, -9.)
        for i in range(-9, 10):
            glVertex2f(9., i)
            glVertex2f(-9., i)
        glEnd()

        glPointSize(5.0)
        # glTranslatef(-0.01, 0., 0.)
        glBegin(GL_POINTS)
        glVertex2f(0., 0.)
        glVertex2f(6., 6.)
        glVertex2f(-6., 6.)
        glVertex2f(-6., -6.)
        glVertex2f(6., -6.)
        glVertex2f(6., 0.)
        glVertex2f(-6., 0.)
        glVertex2f(0., -6.)
        glVertex2f(0., 6.)
        glEnd()

        glPointSize(17.)
        glColor3f(1., 0., 0.)
        glBegin(GL_POINTS)
        if len(self.white_stones) > 0:
            glVertex2fv(self.white_stones[len(self.white_stones)-1])
        if len(self.black_stones) > 0:
            glVertex2fv(self.black_stones[len(self.black_stones)-1])
        glEnd()


        glPointSize(15.)
        glBegin(GL_POINTS)
        glColor3f(0., 0., 0.)
        for pos in self.engine.list_black:
            glVertex2fv(pos)
        glColor3f(1., 1., 1.)
        for pos in self.engine.list_white:
            glVertex2fv(pos)
        glEnd()

        glFlush()


    def handle(self, e):
        if e == FL_PUSH:
            x = Fl.event_x()
            y = Fl.event_y()

            modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
            projection = glGetDoublev(GL_PROJECTION_MATRIX)
            viewport = glGetIntegerv(GL_VIEWPORT)

            winX = x
            winY = viewport[3] - y
            winZ = 0
            pos = gluUnProject(winX, winY, winZ, modelview, projection, viewport)
            pos = [int(round(pos[0])), int(round(pos[1]))]
            posstr = ''
            if pos[0] < -1:
                posstr = chr(pos[0]+10+64) + str(pos[1]+10)
            else:
                # remove I
                posstr = chr(pos[0]+10+64+1) + str(pos[1]+10)
            self.engine.userMove(posstr)
            enginePos = self.engine.engineMove()
            self.engine.GetStatus()


            self.redraw()

        return Fl_Gl_Window.handle(self, e)




goWindow = GoWindow()

goWindow.show()
Fl.run()
