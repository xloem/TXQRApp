#!/usr/bin/env python3

from kivy.app import App

from kivy.graphics import Color, Scale, Rectangle, PushMatrix, PopMatrix, Translate
from kivy.graphics.texture import Texture
from kivy.graphics.transformation import Matrix

from kivy.clock import Clock

from kivy.properties import ObjectProperty, ListProperty

from kivy.uix.button import Button

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.filechooser import FileChooserListView as FileChooser
from kivy.uix.image import Image
from kivy.uix.widget import Widget

import base64
import fountaincoding
import math
import os
import qrcode
import random

class QRCode(Widget):
    data = ListProperty()

    def __init__(self, qrcodes, *args, **kwargs):
        self.qrcodes = qrcodes
        self.gfxtranslate = Translate()
        self.gfxscale = Scale()
        super().__init__(*args, **kwargs)

    def on_size(self, instance, size):
        size = min(size)
        self.gfxscale.x = size
        self.gfxscale.y = size

    def on_pos(self, instance, pos):
        self.gfxtranslate.x = pos[0] + self.width / 2
        self.gfxtranslate.y = pos[1] + self.height / 2

    count = 0
    def on_data(self, instance, data):
        version = 0
        QRCode.count += 1
        print(QRCode.count)
        for qrcode, item in zip(self.qrcodes, data):
            qrcode.clear()
            qrcode.add_data(item)
            version = max(version, qrcode.best_fit())
        for qrcode, item in zip(self.qrcodes, data):
            qrcode.best_fit(version)
            mask = random.randint(0,8)
            while True:
                try:
                    qrcode.makeImpl(False, mask)
                    break
                except TypeError:
                    mask = (mask + 1) % 8
            
        size = self.qrcodes[0].modules_count
        border = max((qrcode.border for qrcode in self.qrcodes))
        outersize = size + border * 2

        self.canvas.clear()
        with self.canvas.before:
            PushMatrix()
            self.gfxtranslate = Translate()
            Scale(1/outersize, 1/outersize, 1)
            self.gfxscale = Scale()
            self.on_pos(self, self.pos)
            self.on_size(self, self.size)
            Translate(-size/2,-size/2,0)
            Color(1,1,1)
            Rectangle(pos=(-border,-border),size=(outersize,outersize))
            for r in range(size):
                for c in range(size):
                    values = [qrcode.modules[r][c] for qrcode in self.qrcodes]
                    if len(values) == 1:
                        values = values * 3
                    if values[0] is None:
                        break
                    Color(*values)
                    Rectangle(pos=(r,c), size=(1,1))
            PopMatrix()

class TXQRApp(App):
    def build(self):
        parent = BoxLayout(orientation = 'vertical')

        self.duration = 300
        self.blocksize = 512
        self.extra = 10
        self.error = 1
        self.base64 = True
        self.multicolor = True

        self.interval = Clock.schedule_interval(self.on_interval, self.duration / 1000)
        #self.image = Image()
        #parent.add_widget(self.image)
        self.qrwidget = QRCode([qrcode.QRCode(version=None,
                           error_correction={
                               0: qrcode.constants.ERROR_CORRECT_L,
                               1: qrcode.constants.ERROR_CORRECT_M,
                               2: qrcode.constants.ERROR_CORRECT_Q,
                               3: qrcode.constants.ERROR_CORRECT_H,
                           }.get(self.error, 1),
                           box_size=8,
                           border=10)])
        parent.add_widget(self.qrwidget)
        parent.add_widget(Button())
        self.filechooser = FileChooser(path = os.path.abspath('.'), on_submit = self.on_file_submit)
        parent.add_widget(self.filechooser)

        self.iterdata = None


        return parent

    def on_file_submit(self, chooser, selection, touch):
        with open(selection[0], 'rb') as file:
            data, score, compressed, compressed_data = fountaincoding.encode_and_compress(file, self.blocksize, extra = math.floor(self.extra))
        self.data = data
        self.iterdata = iter(data)

    def on_interval(self, clock):
        if self.iterdata is None:
            return
        try:
            data = next(self.iterdata)
        except StopIteration:
            self.iterdata = iter(self.data)
            data = next(self.iterdata)
        if self.base64:
            data = base64.b64encode(data)
        self.qrwidget.data = [data]

if __name__ == '__main__':
    app = TXQRApp()
    app.run()
