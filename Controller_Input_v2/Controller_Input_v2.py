import adsk.core, adsk.fusion, adsk.cam, traceback
from threading import Thread
from .lib_installer import install_libs
import time

main_thread = None
running = False
start_time = time.time()

run_duration = 480 # seconds

def main_loop():
    global running, start_time
    app = adsk.core.Application.get()

    # Initialize pygame
    pygame.init()
    screen, font = setup_pygame_window()

    # Initialize controller
    controller = ControllerInput()
    camera_control = CameraController()

    while running:
        pygame.event.pump()

        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        if elapsed_time > run_duration:
            running = False

        controller.tick()

        # Get controller input
        axis_x, axis_y, axis_z, axis_ax, axis_ay, axis_az = controller.get_input()

        # Get current camera view info
        view = app.activeViewport
        camera = view.camera

        camera_control.set_controller_input(axis_x, axis_y, axis_z, axis_ax, axis_ay, axis_az)
        # Update Fusion 360 camera
        # camera_control.update_camera(input_data)
        camera_control.update_camera(view)

        # Update the pygame UI
        #extents = view.camera.getExtents()
        extents = 0
        update_pygame_window(screen, font, elapsed_time, camera.eye, camera.target, camera.upVector, extents, axis_x, axis_y, axis_z, axis_ax, axis_ay, axis_az, camera_control)
            
        # FOR DEBUG: Update the pygame UI with a simple counter
        #update_pygame_window_simple_counter(screen, font, int(elapsed_time))

        # Update UI
        # ui.update(input_data, camera_control.get_camera_info())

        adsk.doEvents()  # Allow Fusion 360 to process other events
    
    #camera.cameraType = 0
    #view.camera = camera
    #view.refresh()
    #adsk.doEvents()

    # Clean up
    pygame.quit()

def run(context):
    ui = None
    try:
        global main_thread, running, start_time
        running = True
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox('Starting Add-In')

        # Install required libraries
        install_libs()

        # Import the libraries for real
        global pygame, np, hid, setup_pygame_window, update_pygame_window, update_pygame_window_simple_counter, pygame_print_debug_text, ControllerInput, CameraController
        import pygame
        import numpy as np
        from pywinusb import hid
        from .pygame_ui import setup_pygame_window, update_pygame_window, update_pygame_window_simple_counter, pygame_print_debug_text
        from .controller_input import ControllerInput
        from .fusion_camera_control import CameraController

        # Set start time
        start_time = time.time()

        main_thread = Thread(target=main_loop)
        main_thread.start()
    except:
        if running:
            running = False
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))




def stop(context):
    global main_thread, running
    running = False
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        if main_thread:
            main_thread.join(5)  # Wait for up to 5 seconds

            if main_thread.is_alive():
                # Log a message or take necessary action if the thread is still alive
                ui.messageBox('The main thread did not stop as expected.')

        app = adsk.core.Application.get()
        ui = app.userInterface
        #ui.messageBox('Stopping Add-In')
    except:
        if running:
            running = False
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
