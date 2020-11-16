#!/usr/bin/env python3

from kivy.app import App

#from kivy.uix.camera import Camera
from cameradbg import Camera
from kivy.utils import platform

class TXQRApp(App):
    def build(self):
        print('platform', platform)
        if platform == 'android':
            print('spawning request')
            from android.permissions import request_permissions, Permission
            print(request_permissions([Permission.CAMERA]))
        Camera(index = 0, play = True)

if __name__ == '__main__':
    app = TXQRApp()
    app.run()
