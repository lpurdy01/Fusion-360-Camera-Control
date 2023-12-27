import adsk.core
import sys
import subprocess

def install_libs():
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        try:
                # Install numpy
                try:
                    import numpy as np
                except:
                    try:
                        #install numpy using subprocess
                        ui.messageBox('Installing numpy')
                        subprocess.check_call([sys.executable, "-m", "pip", "install", 'numpy'])
                    except:
                        ui.messageBox('Installing numpy failed')
                # Install pygame
                try:
                    import pygame
                except:
                    try:
                        #install pygame using subprocess
                        ui.messageBox('Installing pygame')
                        subprocess.check_call([sys.executable, "-m", "pip", "install", 'pygame'])
                    except:
                        ui.messageBox('Installing pygame failed')
                # Install pywinusb
                try:
                    from pywinusb import hid
                except:
                    try:
                        #install pywinusb using subprocess
                        ui.messageBox('Installing pywinusb')
                        subprocess.check_call([sys.executable, "-m", "pip", "install", 'pywinusb'])
                    except:
                        ui.messageBox('Installing pywinusb failed')
                # Install scipy
                try:
                    import scipy
                except:
                    try:
                        #install scipy using subprocess
                        ui.messageBox('Installing scipy')
                        subprocess.check_call([sys.executable, "-m", "pip", "install", 'scipy'])
                    except:
                        ui.messageBox('Installing scipy failed')
        except:
            ui.messageBox('Installing required libraries failed')
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
