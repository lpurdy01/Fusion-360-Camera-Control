#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import sys
import subprocess
import time

dead_zone = 0.15
speed_multipler = 2

def install_libs():
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        try:
                try:
                    import numpy as np
                except:
                    try:
                        #install numpy using subprocess
                        ui.messageBox('Installing numpy')
                        subprocess.check_call([sys.executable, "-m", "pip", "install", 'numpy'])
                    except:
                        ui.messageBox('Installing numpy failed')
                try:
                    import pygame
                except:
                    try:
                        #install pygame using subprocess
                        ui.messageBox('Installing pygame')
                        subprocess.check_call([sys.executable, "-m", "pip", "install", 'pygame'])
                    except:
                        ui.messageBox('Installing pygame failed')
        except:
            ui.messageBox('Installing required libraries failed')
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def get_controller_input():
    pygame.event.pump()
    axis_x = joystick.get_axis(0)  # Adjust the axis as needed
    axis_y = joystick.get_axis(1)
    axis_z = joystick.get_axis(5)-joystick.get_axis(4)
    axis_a = joystick.get_axis(2)
    axis_b = joystick.get_axis(3)

    if abs(axis_x) < dead_zone:
        axis_x = 0
    if abs(axis_y) < dead_zone:
        axis_y = 0
    if abs(axis_z) < dead_zone:
        axis_z = 0
    if abs(axis_a) < dead_zone:
        axis_a = 0
    if abs(axis_b) < dead_zone:
        axis_b = 0
    return axis_x, axis_y, axis_z, axis_a, axis_b

def setup_pygame_window():
    screen = pygame.display.set_mode((800, 400))  # Adjust size as needed
    pygame.display.set_caption("Camera Debug Information")
    font = pygame.font.Font(None, 18)  # Adjust font and size as needed

    return screen, font

def update_pygame_window(screen, font, eye, target, up, extents, axis_x, axis_y, axis_z, axis_a, axis_b):
    screen.fill((0, 0, 0))  # Clear screen (fill with black)

    # Render the text
    # create the eye text x, y, z
    eye_text = font.render("Eye: {:.2f}, {:.2f}, {:.2f}".format(eye.x, eye.y, eye.z), True, (255, 255, 255))
    # create the target text x, y, z
    target_text = font.render("Target: {:.2f}, {:.2f}, {:.2f}".format(target.x, target.y, target.z), True, (255, 255, 255))
    # create the up text x, y, z
    up_text = font.render("Up: {:.2f}, {:.2f}, {:.2f}".format(up.x, up.y, up.z), True, (255, 255, 255))
    # print the extents variable
    extents_text = font.render(f"View Extents: {extents}", True, (255, 255, 255))

    # create the text for the axies
    axis_x_text = font.render(f"Axis X: {axis_x}", True, (255, 255, 255))
    axis_y_text = font.render(f"Axis Y: {axis_y}", True, (255, 255, 255))
    axis_z_text = font.render(f"Axis Z: {axis_z}", True, (255, 255, 255))
    axis_a_text = font.render(f"Axis A: {axis_a}", True, (255, 255, 255))
    axis_b_text = font.render(f"Axis B: {axis_b}", True, (255, 255, 255))

    # Blit the text to the screen
    screen.blit(eye_text, (10, 10))
    screen.blit(target_text, (10, 50))
    screen.blit(up_text, (10, 90))
    screen.blit(extents_text, (10, 130))
    screen.blit(axis_x_text, (10, 170))
    screen.blit(axis_y_text, (10, 210))
    screen.blit(axis_z_text, (10, 250))
    screen.blit(axis_a_text, (10, 290))
    screen.blit(axis_b_text, (10, 330))

    # Update the display
    pygame.display.flip()

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('Controller Session Starting')
        # try to install required libraries
        install_libs()
        # delay import of libraries until after install
        global pygame, np, joystick

        import numpy as np
        import pygame
        

        start_time = time.time()
        duration = 30  # Run for 30 seconds, adjust as needed

        pygame.init()
        pygame.joystick.init()
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        screen, font = setup_pygame_window()

        while time.time() - start_time < duration:
            try:
                axis_x, axis_y, axis_z, axis_a, axis_b = get_controller_input()
                view = app.activeViewport
                camera = view.camera
                update_pygame_window(screen, font, camera.eye, camera.target, camera.upVector, view.camera.getExtents(), axis_x, axis_y, axis_z, axis_a, axis_b)
                new_eye = adsk.core.Point3D.create(camera.eye.x + axis_a*speed_multipler, camera.eye.y + axis_b*speed_multipler, camera.eye.z + axis_z*speed_multipler*0.5)
                new_target = adsk.core.Point3D.create(camera.target.x + axis_x*speed_multipler, camera.target.y + axis_y*speed_multipler, camera.target.z)
                camera.eye = new_eye
                camera.target = new_target
                camera.isSmoothTransition = False
                view.camera = camera
                view.refresh()
                adsk.doEvents()  # Allow Fusion 360 to process other events

            except:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                break

        ui.messageBox('Controller Session Ended')  # End of script

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

    finally:
        pygame.quit()
