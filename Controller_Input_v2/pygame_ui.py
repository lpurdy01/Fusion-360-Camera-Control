import pygame
import numpy as np

debug_text_block = "Init Text"

def setup_pygame_window():
    screen = pygame.display.set_mode((1000, 800))  # Adjust size as needed
    pygame.display.set_caption("Camera Debug Information")
    font = pygame.font.Font(None, 18)  # Adjust font and size as needed

    debug_text_block = "Init Text"

    return screen, font

def pygame_print_debug_text(text):
    '''
    This function will print the text to the pygame window. The debug text will always be on the bottom of the screen, 
    and the last 20 lines of text will be displayed.
    '''
    global debug_text_block
    debug_text_block = text + "\n" + debug_text_block
    debug_text_block = "\n".join(debug_text_block.split("\n")[:20])

def render_multiline_text(screen, text, pos, font, color):
    lines = text.split('\n')
    x, y = pos
    for line in lines:
        line_surface = font.render(line, True, color)
        screen.blit(line_surface, (x, y))
        y += font.get_linesize()  # Move to the next line position

def project_3d_to_2d(point):
    """Project a 3D point to 2D using an orthographic projection."""
    # For simplicity, ignore the z-coordinate (depth)
    return point[0], point[1]

def perspective_projection(point, camera_pos, screen_size, fov=100, near_plane=0.1, far_plane=200.0):
    """Project a 3D point into 2D using a perspective projection matrix."""
    # Adjust the point relative to the camera position
    adjusted_point = point - camera_pos

    # Perspective projection matrix
    aspect_ratio = screen_size[0] / screen_size[1]
    f = 1 / np.tan(np.radians(fov) / 2)
    projection_matrix = np.array([
        [f / aspect_ratio, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far_plane + near_plane) / (near_plane - far_plane), (2 * far_plane * near_plane) / (near_plane - far_plane)],
        [0, 0, -1, 0]
    ])

    # Convert the point to homogeneous coordinates and apply the projection
    homogeneous_point = np.append(adjusted_point, 1)
    projected_point = projection_matrix @ homogeneous_point

    # Perform perspective divide and convert to screen coordinates
    if projected_point[3] != 0:
        projected_point /= projected_point[3]
        screen_x = int((projected_point[0] + 1) * screen_size[0] / 2)
        screen_y = int((1 - projected_point[1]) * screen_size[1] / 2)
        return screen_x, screen_y
    else:
        return None  # Point cannot be projected

# Usage in the rendering function remains the same as before


def draw_vector(screen, start, end, color=(255, 255, 255)):
    """Draw a line representing a vector."""
    start_2d = project_3d_to_2d(start)
    end_2d = project_3d_to_2d(end)
    pygame.draw.line(screen, color, start_2d, end_2d, 2)

def draw_vector_3d(screen, start, end, color, camera_pos, screen_size):
    """Draw a 3D vector on the screen."""
    start_2d = perspective_projection(start, camera_pos, screen_size)
    end_2d = perspective_projection(end, camera_pos, screen_size)
    pygame.draw.line(screen, color, start_2d, end_2d, 2)

def render_3d_view(screen, camera_control, font):
    """Render the 3D view including vectors."""
    camera_pos = np.array([25, -30, 80])  # Camera position for visualization
    screen_size = (screen.get_width(), screen.get_height())
    scale = 10

    # Define the origin in world coordinates
    world_origin = np.array([0, 0, 0])

    # Global axes
    draw_vector_3d(screen, world_origin, np.array([scale, 0, 0]), (255, 0, 0), camera_pos, screen_size)  # X-axis (Red)
    draw_vector_3d(screen, world_origin, np.array([0, scale, 0]), (0, 255, 0), camera_pos, screen_size)  # Y-axis (Green)
    draw_vector_3d(screen, world_origin, np.array([0, 0, scale]), (0, 0, 255), camera_pos, screen_size)  # Z-axis (Blue)

    # Camera vectors
    draw_vector_3d(screen, camera_control.eye_vector, camera_control.eye_vector + (camera_control.view_direction_norm * scale), (0, 100, 0), camera_pos, screen_size)  # Direction (y) (Dark Green)
    draw_vector_3d(screen, camera_control.eye_vector, camera_control.eye_vector + (camera_control.up_vector * scale), (80, 0, 140), camera_pos, screen_size)  # Up (z) (Purple)
    draw_vector_3d(screen, camera_control.eye_vector, camera_control.eye_vector + (camera_control.right_vector * scale), (255, 70, 50), camera_pos, screen_size)  # Right (x) (Pink)

    # Translation vectors
    draw_vector_3d(screen, world_origin, ( camera_control.translation_vector * scale * 0.001), (255, 165, 0), camera_pos, screen_size)  # Translation (Orange)
    draw_vector_3d(screen, camera_control.eye_vector, camera_control.eye_vector + ( camera_control.rotated_translation_vector * scale * 0.001), (0, 255, 0), camera_pos, screen_size)  # Rotated translation (Lime)

    # Rotation forward vectors
    draw_vector_3d(screen, world_origin, camera_control.global_input_rotation_forward_vector * scale, (255, 255, 0), camera_pos, screen_size)  # Yaw (Yellow)
    draw_vector_3d(screen, camera_control.eye_vector, camera_control.eye_vector + (camera_control.camera_input_rotation_forward_vector * scale), (255, 0, 255), camera_pos, screen_size)  # Pitch (Magenta)

    # Rotation up vectors
    draw_vector_3d(screen, world_origin, camera_control.global_input_rotation_up_vector * scale, (255, 255, 0), camera_pos, screen_size)  # Yaw (Yellow)
    draw_vector_3d(screen, camera_control.eye_vector, camera_control.eye_vector + (camera_control.camera_input_rotation_up_vector * scale), (255, 0, 255), camera_pos, screen_size)  # Pitch (Magenta)
    
    # Draw the color key
    draw_color_key(screen, font)

def draw_color_key(screen, font):
    """Draw the color key for the vectors on the screen."""
    color_descriptions = [
        ("Red", "X-axis"),
        ("Green", "Y-axis"),
        ("Blue", "Z-axis"),
        ("Dark Green", "Direction"),
        ("Purple", "Up"),
        ("Pink", "Right"),
        ("Orange", "Translation"),
        ("Lime", "Rotated Translation"),
        ("Yellow", "Yaw"),
        ("Magenta", "Pitch")
    ]
    x, y = 10, screen.get_height() - 20 * len(color_descriptions)  # Starting position for the color key
    for color_name, description in color_descriptions:
        text_surface = font.render(f"{color_name}: {description}", True, (255, 255, 255))
        screen.blit(text_surface, (x, y))
        y += 20  # Move to the next line


def update_pygame_window(screen, font, time, eye, target, up, extents, axis_x, axis_y, axis_z, axis_ax, axis_ay, axis_az, camera_control):
    screen.fill((0, 0, 0))  # Clear screen (fill with black)

    # Render the 3D view with vectors
    render_3d_view(screen, camera_control, font)

    # Render the text
    # create the time text
    time_text = font.render(f"Time: {time}", True, (255, 255, 255))
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
    axis_ax_text = font.render(f"Axis A: {axis_ax}", True, (255, 255, 255))
    axis_ay_text = font.render(f"Axis B: {axis_ay}", True, (255, 255, 255))
    axis_az_text = font.render(f"Axis C: {axis_az}", True, (255, 255, 255))


    # Blit the text to the screen
    screen.blit(time_text, (10, 10))
    screen.blit(eye_text, (10, 30))
    screen.blit(target_text, (10, 50))
    screen.blit(up_text, (10, 70))
    screen.blit(extents_text, (10, 90))
    screen.blit(axis_x_text, (10, 110))
    screen.blit(axis_y_text, (10, 130))
    screen.blit(axis_z_text, (10, 150))
    screen.blit(axis_ax_text, (10, 170))
    screen.blit(axis_ay_text, (10, 190))
    screen.blit(axis_az_text, (10, 210))

    # render the debug text
    render_multiline_text(screen, debug_text_block, (10, 230), font, (255, 255, 255))

    # Create the debug text for the camera control (to the right of the other text)
    
    view_direction_text = font.render(f"View Direction: {camera_control.view_direction}", True, (255, 255, 255))
    view_direction_norm_text = font.render(f"View Direction Norm: {camera_control.view_direction_norm}", True, (255, 255, 255))
    view_direction_mag_text = font.render(f"View Direction Mag: {camera_control.view_direction_mag}", True, (255, 255, 255))
    translation_vector_text = font.render(f"Translation Vector: {camera_control.translation_vector}", True, (255, 255, 255))
    translation_vector_mag_text = font.render(f"Translation Vector Mag: {camera_control.translation_vector_mag}", True, (255, 255, 255))
    rotated_translation_vector_text = font.render(f"Rotated Translation Vector: {camera_control.rotated_translation_vector}", True, (255, 255, 255))
    rotated_translation_vector_mag_text = font.render(f"Rotated Translation Vector Mag: {camera_control.rotated_translation_vector_mag}", True, (255, 255, 255))
    camera_rotation_text = font.render(f"Camera Rotation: {camera_control.camera_rotation}", True, (255, 255, 255))
    right_vector_text = font.render(f"Right Vector: {camera_control.right_vector}", True, (255, 255, 255))
    translation_difference = font.render(f"Translation Difference: {camera_control.translation_difference}", True, (255, 255, 255))
    up_vector_text = font.render(f"Up Vector: {camera_control.up_vector}", True, (255, 255, 255))
    clipped_ax_text = font.render(f"Clipped Axis X: {camera_control.clipped_ax}", True, (255, 255, 255))
    clipped_ay_text = font.render(f"Clipped Axis Y: {camera_control.clipped_ay}", True, (255, 255, 255))
    clipped_az_text = font.render(f"Clipped Axis Z: {camera_control.clipped_az}", True, (255, 255, 255))


    # Blit the text to the screen
    screen.blit(view_direction_text, (400, 10))
    screen.blit(view_direction_norm_text, (400, 30))
    screen.blit(view_direction_mag_text, (400, 50))
    screen.blit(translation_vector_text, (400, 70))
    screen.blit(translation_vector_mag_text, (400, 90))
    screen.blit(rotated_translation_vector_text, (400, 110))
    screen.blit(rotated_translation_vector_mag_text, (400, 130))
    screen.blit(camera_rotation_text, (400, 150))
    screen.blit(right_vector_text, (400, 170))
    screen.blit(translation_difference, (400, 190))
    screen.blit(up_vector_text, (400, 210))
    screen.blit(clipped_ax_text, (400, 230))
    screen.blit(clipped_ay_text, (400, 250))
    screen.blit(clipped_az_text, (400, 270))
    
    


    # Update the display
    pygame.display.flip()


def update_pygame_window_simple_counter(screen, font, number):
    screen.fill((0, 0, 0))  # Clear screen (fill with black)

    # render the number given
    number_text = font.render(f"Number: {number}", True, (255, 255, 255))

    # Blit the text to the screen
    screen.blit(number_text, (10, 10))

    # Update the display
    pygame.display.flip()