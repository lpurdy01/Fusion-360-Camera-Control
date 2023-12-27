import numpy as np
from scipy.spatial.transform import Rotation as R
import adsk.core, adsk.fusion
import time
from .pygame_ui import pygame_print_debug_text

class CameraController:
    def __init__(self):
        # Movement speeds
        self.translation_speed = 0.002
        self.rotation_speed = 0.1
        # Rotation Scale Factors
        # Example scale factors: scale the input values from a range of -6000 to 6000 to -0.5pi to 0.5pi
        self.scale_factors = (0.5 * np.pi / 6000, 0.5 * np.pi / 6000, 0.5 * np.pi / 6000)
        # Controller axes
        self.axis_x = 0.0
        self.axis_y = 0.0
        self.axis_z = 0.0
        self.axis_ax = 0.0
        self.axis_ay = 0.0
        self.axis_az = 0.0
        # Timing
        self.last_loop_time = time.time()
        # View Direction Vector
        self.view_direction = np.array([0.0, 0.0, 0.0])
        self.view_direction_norm = np.array([0.0, 0.0, 0.0])
        self.view_direction_mag = 0.0
        # Translation Vector
        self.translation_vector = np.array([0.0, 0.0, 0.0])
        self.translation_vector_mag = 0.0
        # Rotated Translation Vector
        self.rotated_translation_vector = np.array([0.0, 0.0, 0.0])
        self.rotated_translation_vector_mag = 0.0
        # Camera Rotation
        self.camera_rotation = R.from_matrix([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]])
        # Right Vector
        self.right_vector = np.array([0.0, 0.0, 0.0])
        # Up Vector
        self.up_vector = np.array([0.0, 0.0, 0.0])
        # Difference between the translation vector and the rotated translation vector
        self.translation_difference = np.array([0.0, 0.0, 0.0])
        # Eye Vector
        self.eye_vector = np.array([0.0, 0.0, 0.0])
        # clipped ax ay az
        self.clipped_ax = 0.0
        self.clipped_ay = 0.0
        self.clipped_az = 0.0
        # Global coordinate frame input_rotation_forward_vector
        self.global_input_rotation_forward_vector = np.array([0.0, 0.0, 0.0])
        # Camera coordinate frame input_rotation_forward_vector
        self.camera_input_rotation_forward_vector = np.array([0.0, 0.0, 0.0])
        self.camera_input_rotation_forward_vector_amplified = np.array([0.0, 0.0, 0.0])
        # Global coordinate frame input_rotation_up_vector
        self.camera_input_rotation_up_vector = np.array([0.0, 0.0, 0.0])
        # Camera coordinate frame input_rotation_up_vector
        self.camera_input_rotation_up_vector = np.array([0.0, 0.0, 0.0])
        self.camera_input_rotation_up_vector_amplified = np.array([0.0, 0.0, 0.0])
    
        

    def update_camera(self, view):
        # Fetch the current camera state
        camera = view.camera
        eye = np.array([camera.eye.x, camera.eye.y, camera.eye.z])
        target = np.array([camera.target.x, camera.target.y, camera.target.z])
        up = np.array([camera.upVector.x, camera.upVector.y, camera.upVector.z])

        # Calculate elapsed time since last update
        current_time = time.time()
        elapsed_time = current_time - self.last_loop_time
        self.last_loop_time = current_time

        # Process controller input
        transformed_eye, transformed_target, transformed_up, transformed_extents = self.process_input(eye, target, up, elapsed_time)

        # check if any of the values or nan or inf
        if np.isnan(transformed_eye).any() or np.isnan(transformed_target).any() or np.isnan(transformed_up).any() or np.isnan(transformed_extents).any():
            pygame_print_debug_text("NAN detected")
            return

        # Update Fusion 360 camera
        new_eye = adsk.core.Point3D.create(transformed_eye[0], transformed_eye[1], transformed_eye[2])
        new_target = adsk.core.Point3D.create(transformed_target[0], transformed_target[1], transformed_target[2])
        new_up = adsk.core.Vector3D.create(transformed_up[0], transformed_up[1], transformed_up[2])

        # Create a new camera object with the type 1 (Perspective)
        #camera = adsk.core.Camera.create()

        camera.eye = new_eye
        camera.target = new_target
        camera.upVector = new_up
        #camera.viewExtents = transformed_extents
        #camera.setExtents(transformed_extents, transformed_extents)
        #camera.apply()
        camera.isSmoothTransition = False
        #camera.cameraType = 1
        #Remove the extents property from the camera object

        view.camera = camera
        view.refresh()

    def create_safe_rotation_quaternion(self, ax, ay, az, max_angle=np.pi/2):
        """
        Create a safe rotation quaternion from Euler angles with scaling and clipping.

        :param ax: Rotation around the x-axis.
        :param ay: Rotation around the y-axis.
        :param az: Rotation around the z-axis.
        :param scale_factors: Tuple of scale factors for (ax, ay, az).
        :param max_angle: Maximum rotation angle in radians.
        :return: Rotation quaternion.
        """
        # Scale the inputs
        scaled_ax = ax * self.scale_factors[0]
        scaled_ay = ay * self.scale_factors[1]
        scaled_az = az * self.scale_factors[2]

        # Clip the values to [-max_angle, max_angle]
        clipped_ax = np.clip(scaled_ax, -max_angle, max_angle)
        clipped_ay = np.clip(scaled_ay, -max_angle, max_angle)
        clipped_az = np.clip(scaled_az, -max_angle, max_angle)

        # Save out to self
        self.clipped_ax = clipped_ax
        self.clipped_ay = clipped_ay
        self.clipped_az = clipped_az

        # Create the rotation quaternion
        rotation = R.from_euler('xyz', [clipped_ax, clipped_ay, clipped_az])
        return rotation



    def process_input(self, eye, target, up, elapsed_time):
        self.eye_vector = eye

        # Compute normalized direction vector (camera's y-axis)
        direction = target - eye
        self.view_direction = direction
        direction_mag = np.linalg.norm(direction)
        self.view_direction_mag = direction_mag
        extents = np.linalg.norm(direction)/10
        direction /= np.linalg.norm(direction)
        self.view_direction_norm = direction
        
        # Compute normalized up vector (camera's z-axis)
        up /= np.linalg.norm(up)
        self.up_vector = up

        # Compute the right vector (camera's x-axis) using cross product
        right = np.cross(direction, up)
        right /= np.linalg.norm(right)
        self.right_vector = right

        # Compute the adjusted up vector
        adjusted_up = np.cross(right, direction)

        # Create a rotation that aligns standard basis vectors to the camera's local axes
        #camera_rotation = R.from_matrix([right, direction, up])
        #self.camera_rotation = camera_rotation

        # Create rotation quaternion
        rotation_matrix = np.column_stack((right, direction, adjusted_up))
        rotation_quaternion = R.from_matrix(rotation_matrix)

        # Create rotation from Euler angles
        #camera_rotation = R.from_euler('xyz', [yaw, pitch, roll])
        #self.camera_rotation = camera_rotation

        # Rotate the input translation vector into the camera's local coordinate space
        translation = np.array([self.axis_x, self.axis_y, self.axis_z])
        translation_zoom = np.array([0.0, self.axis_z, 0.0])
        #rotated_translation = camera_rotation.apply(translation)
        #rotated_translation_zoom = camera_rotation.apply(translation_zoom)
        rotated_translation = rotation_quaternion.apply(translation)
        rotated_translation_zoom = rotation_quaternion.apply(translation_zoom)
        self.translation_vector = translation
        self.translation_vector_mag = np.linalg.norm(translation)
        self.rotated_translation_vector = rotated_translation
        self.rotated_translation_vector_mag = np.linalg.norm(rotated_translation)

        self.translation_difference = rotated_translation - translation

        # Apply translations to eye and target
        transformed_eye = eye + rotated_translation * self.translation_speed * elapsed_time
        transformed_target = target + rotated_translation * self.translation_speed * elapsed_time

        # Rotate a y+ vector and up vector by the input rotation
        input_rotation_forward = np.array([0, 1, 0])
        input_rotation_up = np.array([0, 0, 1])
        input_rotation_quaternion = self.create_safe_rotation_quaternion(self.axis_ax, self.axis_ay, self.axis_az)

        # Rotate the input rotation vector into the global coordinate space
        global_input_rotation_forward_vector = input_rotation_quaternion.apply(input_rotation_forward)
        self.global_input_rotation_forward_vector = global_input_rotation_forward_vector

        # Rotate the input rotation vector into the global coordinate space
        global_input_rotation_up_vector = input_rotation_quaternion.apply(input_rotation_up)
        
        # Normalize
        global_input_rotation_up_vector /= np.linalg.norm(global_input_rotation_up_vector)
        self.global_input_rotation_up_vector = global_input_rotation_up_vector

        # Rotate the input rotation forward vector into the camera's local coordinate space
        camera_input_rotation_forward_vector = rotation_quaternion.apply(global_input_rotation_forward_vector)
        self.camera_input_rotation_forward_vector = camera_input_rotation_forward_vector

        # Rotate the input rotation up vector into the camera's local coordinate space
        camera_input_rotation_up_vector = rotation_quaternion.apply(global_input_rotation_up_vector)
        self.camera_input_rotation_up_vector = camera_input_rotation_up_vector

        # Scale the rotation vector by the magnitude of the view direction
        camera_input_rotation_forward_vector_amplified = camera_input_rotation_forward_vector * direction_mag

        # Apply the rotation to the target
        transformed_target += camera_input_rotation_forward_vector_amplified * self.rotation_speed * elapsed_time

        # Apply the rotation to the up
        transformed_up = up + camera_input_rotation_up_vector * self.rotation_speed * elapsed_time
        
        # Apply the zoom vector to the eye
        #transformed_eye += rotated_translation_zoom * self.translation_speed * 10 * elapsed_time

        # Calculate the extents
        new_direction = transformed_target - transformed_eye
        extents = np.linalg.norm(new_direction)/10

        return transformed_eye, transformed_target, transformed_up, extents

    def set_controller_input(self, axis_x, axis_y, axis_z, axis_ax, axis_ay, axis_az):
        self.axis_x = -axis_x
        self.axis_y = -axis_y
        self.axis_z = axis_z
        self.axis_ax = axis_ax
        self.axis_ay = axis_ay
        self.axis_az = axis_az

    def get_diagnostic_data(self, eye, target, up):
        return {
            "eye_x": eye[0],
            "eye_y": eye[1],
            "eye_z": eye[2],
            "target_x": target[0],
            "target_y": target[1],
            "target_z": target[2],
            "up_x": up[0],
            "up_y": up[1],
            "up_z": up[2]
        }
