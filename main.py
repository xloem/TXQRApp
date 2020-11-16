#!/usr/bin/env python3

from kivy.app import App

from kivy.clock import Clock

from kivy.config import ConfigParser
from kivy.core.image import Image as CoreImage

from kivy.graphics import Color, Scale, Rectangle, PushMatrix, PopMatrix, Translate
from kivy.graphics.texture import Texture
from kivy.graphics.transformation import Matrix

from kivy.properties import ObjectProperty, ListProperty, BoundedNumericProperty, StringProperty

from kivy.uix.pagelayout import PageLayout
from kivy.uix.camera import Camera
from kivy.uix.filechooser import FileChooserListView as FileChooser
from kivy.uix.image import Image
from kivy.uix.settings import SettingsWithNoMenu as Settings
from kivy.uix.widget import Widget

import base64
import fountaincoding
import io
import math
import os
import random
import pyzint
import zbarlight
import PIL.Image

class QRCode(Image):
    data = ListProperty()
    error = BoundedNumericProperty(0.5, min=0, max=1)
    borderwidth = BoundedNumericProperty(10, min=0)
    codestandard = StringProperty('QRCODE')

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

        # borderwidth doesn't seem to do anything?  so we do borders manually
        Barcode = getattr(pyzint.Barcode, self.codestandard)
        barcodes = (Barcode(data, option_1 = int(self.error * 4 + 1)) for data in data)

        images = (CoreImage(io.BytesIO(barcode.render_bmp()), ext='bmp') for barcode in barcodes)
        sizepixels = [(image.texture.size, image.texture.pixels) for image in images]
        size = max((max(size) for size, pixels in sizepixels))
        outersize = size + self.borderwidth * 2
        if outersize >= self.rectangle.texture.width:
            texsize = 1 << (int(outersize) - 1).bit_length()
            self.rectangle.texture = Texture.create(size=(texsize,texsize), colorfmt='rgb')
        #self.rectangle.texture.blit_buffer(sizepixels[0][1], size=sizepixels[0][0])
        #return
        newpixels = bytearray(b'\xff\xff\xff') * outersize*outersize
        startoffset = (self.borderwidth + outersize * self.borderwidth) * 3
        for y in range(size):
            for x in range(size):
                values = [0] * min(len(sizepixels),3)
                offset = startoffset + (x + y * outersize) * 3
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

        self.rectangle.texture.blit_buffer(newpixels, size = (outersize,outersize), colorfmt = 'rgb')
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

    def build_config(self, config):
        config.setdefaults('settings', {
            'blocksize': 512,
            'borderwidth': 10,
            'duration': 300,
            'error': '33%',
            'base64': 1,
            'codestandard': 'QRCODE',
            'multicolor': 0,
            'fountaincoding': 1,
            'extra': 10
        })
        # todo: organize config and settings entries to be in the same order, for clarity
        
    def build_settings(self, settings):
        settings.add_json_panel('QR Encoding Settings', self.config, data = 
            """[{
                "type": "numeric",
                "title": "Chunk Size",
                "desc": "Size of chunks data is broken into",
                "section": "settings",
                "key": "blocksize"
            },{
                "type": "numeric",
                "title": "Border Width",
                "desc": "Number of cells used for the border",
                "section": "settings",
                "key": "borderwidth"
            },{
                "type": "numeric",
                "title": "Duration",
                "desc": "The duration of each individual frame",
                "section": "settings",
                "key": "duration"
            },{
                "type": "options",
                "title": "Error",
                "desc": "The degree of additional error correction",
                "section": "settings",
                "key": "error",
                "options": ["0%", "33%", "66%", "100%"]
            },{
                "type": "bool",
                "title": "Base64",
                "desc": "Whether to base64 encode the data as TXQR does",
                "section": "settings",
                "key": "base64"
            },{
                "type": "bool",
                "title": "Multicolor",
                "desc": "Whether to display 3-channel colored images",
                "section": "settings",
                "key": "multicolor"
            },{
                "type": "options",
                "title": "Code Standard",
                "desc": "What kind of 2D barcodes to display",
                "section": "settings",
                "key": "codestandard",
                "options": ["QRCODE", "AZTEC"]
            },{
                "type": "bool",
                "title": "Fountain Coding",
                "desc": "Whether to encode data using txqr fountain coding",
                "section": "settings",
                "key": "fountaincoding"
            },{
                "type": "numeric",
                "title": "Extra",
                "desc": "The number of extra QR codes to generate",
                "section": "settings",
                "key": "extra"
            }]""")

    def build(self):

        pagelayout = PageLayout()#orientation = 'vertical')

        self.filechooser = FileChooser(path = os.path.abspath('.'), on_submit = self.on_file_submit)
        pagelayout.add_widget(self.filechooser)

        self.qrwidget = QRCode()
        pagelayout.add_widget(self.qrwidget)
        self.qrwidget.borderwidth = self.config.getint('settings', 'borderwidth')
        self.on_config_change(self.config, 'settings', 'error', self.config.get('settings', 'error'))
        self.qrwidget.codestandard = self.config.get('settings', 'codestandard')

        self.interval = Clock.schedule_interval(self.on_interval, float(self.config.get('settings', 'duration')) / 1000)
        self.iterdata = None

        #self.camera = Camera(index=1)
        #self.camera._camera.bind(on_texture = self.on_camtexture)
        #self.camera._camera.widget = self.camera
        #pagelayout.add_widget(self.camera)

        self.pagelayout = pagelayout

        return pagelayout

    def on_file_submit(self, chooser, selection, touch):
        if len(selection) == 0:
            return
        blocksize = self.config.getint('settings', 'blocksize')
        with open(selection[0], 'rb') as file:
            if self.config.getint('settings', 'fountaincoding'):
                data, score, compressed, compressed_data = fountaincoding.encode_and_compress(file, blocksize, extra = self.config.getint('settings', 'extra'))
            else:
                data = file.read()
                data = [data[i:i+blocksize] for i in range(0, len(data), blocksize)]
        self.data = data
        self.iterdata = iter(data)
        self.pagelayout.page = 1

    def on_config_change(self, config, section, key, value):
        if key == 'borderwidth':
            self.qrwidget.borderwidth = int(value)
        elif key == 'error':
            self.qrwidget.error = float(value[:value.find('%')])/100
        elif key == 'codestandard':
            self.qrwidget.codestandard = value
        elif key == 'duration':
            self.interval.cancel()
            self.interval = Clock.schedule_interval(self.on_interval, float(value) / 1000)

    def on_interval(self, clock):
        if self.iterdata is None:
            return
        count = 3 if self.config.getint('settings', 'multicolor') else 1
        datas = []
        for index in range(count):
            try:
                data = next(self.iterdata)
            except StopIteration:
                self.iterdata = iter(self.data)
                data = next(self.iterdata)
            if self.config.getint('settings', 'base64'):
                data = base64.b64encode(data)
            datas.append(data)
        self.qrwidget.data = datas

    def on_camtexture(self, camera):
        image = PIL.Image.frombytes('RGBA', camera.texture.size, camera.texture.pixels)
        codes = zbarlight.scan_codes(['qrcode'], image)
        print(codes)
        

            # zbarlight

if __name__ == '__main__':
    app = TXQRApp()
    app.run()
