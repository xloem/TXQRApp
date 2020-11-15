#!/usr/bin/env python3

from kivy.app import App

from kivy.clock import Clock

from kivy.core.image import Image as CoreImage

from kivy.graphics import Color, Scale, Rectangle, PushMatrix, PopMatrix, Translate
from kivy.graphics.texture import Texture
from kivy.graphics.transformation import Matrix

from kivy.properties import ObjectProperty, ListProperty, BoundedNumericProperty

from kivy.uix.button import Button

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.filechooser import FileChooserListView as FileChooser
from kivy.uix.image import Image
from kivy.uix.widget import Widget

import base64
import fountaincoding
import io
import math
import os
import random
import pyzint

class QRCode(Image):
    data = ListProperty()
    ec = BoundedNumericProperty(0.5, min=0, max=1)
    border_width = BoundedNumericProperty(10, min=0)

    def __init__(self, *args, **kwargs):
        #self.gfxtranslate = Translate()
        #self.gfxscale = Scale()
        super().__init__(*args, **kwargs)
        with self.canvas:
            self.rectangle = Rectangle(texture = Texture.create())
        self.on_size(self, self.size)
        self.on_pos(self, self.pos)
        #self.fbos = []

    def on_size(self, instance, size):
        pos = self.pos
        if size[0] > size[1]:
            pos = (pos[0] + (size[0] - size[1]) / 2, pos[1])
            size = (size[1], size[1])
        else:
            pos = (pos[0], pos[1] + (size[1] - size[0]) / 2)
            size = (size[0], size[0])
        self.rectangle.size = size
        self.rectangle.pos = pos
    #    size = min(size)
    #    self.gfxscale.x = size
    #    self.gfxscale.y = size

    def on_pos(self, instance, pos):
        self.on_size(instance, instance.size)
    #    self.gfxtranslate.x = pos[0] + self.width / 2
    #    self.gfxtranslate.y = pos[1] + self.height / 2

    count = 0
    def on_data(self, instance, data):
        version = 0
        QRCode.count += 1

        # TODO: provide interface settings of barcode, bordersize etc

        # border_width doesn't seem to do anything?  so we do borders manually
        barcodes = (pyzint.Barcode.QRCODE(data, option_1 = int(self.ec * 4 + 1)) for data in data)

        images = (CoreImage(io.BytesIO(barcode.render_bmp()), ext='bmp') for barcode in barcodes)
        sizepixels = [(image.texture.size, image.texture.pixels) for image in images]
        size = max((max(size) for size, pixels in sizepixels))
        outersize = size + self.border_width * 2
        if outersize >= self.rectangle.texture.width:
            texsize = 1 << (int(outersize) - 1).bit_length()
            self.rectangle.texture = Texture.create(size=(texsize,texsize))
        #self.rectangle.texture.blit_buffer(sizepixels[0][1], size=sizepixels[0][0])
        #return
        newpixels = bytearray(size*size*3)
        for y in range(size):
            for x in range(size):
                values = [0] * min(len(sizepixels),3)
                offset = (x+y*size)*3
                for index, sizepixel in enumerate(sizepixels):
                    if index > len(values):
                        raise AssertionError('too many images')
                    pixelsize, pixels = sizepixel
                    if x >= pixelsize[0] or y >= pixelsize[1]:
                        continue
                    values[index] = pixels[(x+y*pixelsize[0])*4]
                if len(values) == 1:
                    values *= 3
                elif len(values) == 2:
                    values.append((values[0] + values[1]) // 2)
                newpixels[offset:offset+len(values)] = values

        self.rectangle.texture.blit_buffer(newpixels, pos = (self.border_width, self.border_width), size = (size,size), colorfmt = 'rgb')
        self.rectangle.texture = self.rectangle.texture

        ratio = outersize / self.rectangle.texture.width
        self.rectangle.tex_coords = [0,0,ratio,0,ratio,ratio,0,ratio]
        

        #size = self.qrcodes[0].modules_count
        #border = max((qrcode.border for qrcode in self.qrcodes))
        #outersize = size + border * 2

        #self.canvas.clear()
        #with self.canvas.before:
        #    PushMatrix()
        #    self.gfxtranslate = Translate()
        #    Scale(1/outersize, 1/outersize, 1)
        #    self.gfxscale = Scale()
        #    self.on_pos(self, self.pos)
        #    self.on_size(self, self.size)
        #    Translate(-size/2,-size/2,0)
        #    Color(1,1,1)
        #    Rectangle(pos=(-border,-border),size=(outersize,outersize))
        #    for r in range(size):
        #        for c in range(size):
        #            values = [qrcode.modules[r][c] for qrcode in self.qrcodes]
        #            if len(values) == 1:
        #                values = values * 3
        #            if values[0] is None:
        #                break
        #            Color(*values)
        #            Rectangle(pos=(r,c), size=(1,1))
        #    PopMatrix()

class TXQRApp(App):
    def build(self):
        parent = BoxLayout(orientation = 'vertical')

        self.duration = 300
        self.blocksize = 512
        self.extra = 10
        self.error = 2
        self.base64 = True
        self.multicolor = True

        self.interval = Clock.schedule_interval(self.on_interval, self.duration / 1000)

        self.qrwidget = QRCode()
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
