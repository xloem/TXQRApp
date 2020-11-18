#!/usr/bin/env python3

from kivy.app import App

#from kivy.uix.camera import Camera
from cameradbg import Camera
from kivy.utils import platform

class TXQRApp(App):
    def build(self):
        print('platform', platform)
        if platform == 'android':
            print('checking')
            from android.permissions import request_permission, Permission, check_permission
            if not check_permission(Permission.CAMERA):
                print('spawning request')
                print(request_permission(Permission.CAMERA))
        Camera(index = 0, play = True)

if __name__ == '__main__':
    app = TXQRApp()
    app.run()
