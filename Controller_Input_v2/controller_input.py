from pywinusb import hid
import time
from .pygame_ui import pygame_print_debug_text

VID = 0x0483  # Replace with your vendor ID
PID = 0x572b  # Replace with your product ID

class ControllerInput:
    def __init__(self):
        self.vendor_id = VID
        self.product_id = PID
        self.device = None
        self.reconnect_delay = 1  # seconds
        self.axis_data = [0, 0, 0, 0, 0, 0]  # Initialize axis data
        self.connect()

    def connect(self):
        filter = hid.HidDeviceFilter(vendor_id=self.vendor_id, product_id=self.product_id)
        devices = filter.get_devices()

        if devices:
            self.device = devices[0]
            self.device.open()
            self.device.set_raw_data_handler(self.raw_data_handler)
            pygame_print_debug_text("Controller connected.")
        else:
            pygame_print_debug_text("Controller not found. Trying to reconnect...")
            time.sleep(self.reconnect_delay)
            self.connect()

    def raw_data_handler(self, data):
        # Assuming each axis is represented by 2 bytes in little-endian format
        try:
            for i in range(6):
                # Extract two bytes for each axis
                axis_value = int.from_bytes(data[1 + i * 2:3 + i * 2], byteorder='little', signed=True)
                self.axis_data[i] = axis_value
            #pygame_print_debug_text("Raw data processed.")
        except Exception as e:
            pygame_print_debug_text(f"Error processing raw data: {e}")

    def get_input(self):
        return tuple(self.axis_data)

    def tick(self):
        if not self.device or not self.device.is_plugged():
            pygame_print_debug_text("Controller is not connected. Reconnecting...")
            self.connect()
    
    def disconnect(self):
        if self.device:
            self.device.close()
            self.device = None
            pygame_print_debug_text("Controller disconnected.")

if __name__ == "__main__":
    controller = ControllerInput()

    while True:
        controller.tick()
        input_data = controller.get_input()
        pygame_print_debug_text("Input Data: " + str(input_data))
        time.sleep(0.1)
