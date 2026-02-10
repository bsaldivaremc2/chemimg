import os
import random
import time
from tqdm import tqdm
import numpy as np
from PIL import Image

def create_collage_randomNoCollapse(output_size, folder_path, max_time_seconds=10, max_images=100,
                   output_file="output.png", min_scale_factor=-1, max_scale_factor=-1,
                   lower_alpha=0.5, upper_alpha=1.0,rotate_only_if_vertical=False):
    """
    Creates an image collage by pasting transparent images randomly from a folder onto an output canvas.

    Args:
        output_size (tuple): The size (width, height) of the output image.
        folder_path (str): Path to the folder containing transparent images.
        max_time_seconds (int): Maximum time in seconds for the operation.
        max_images (int): Maximum number of images to paste.
        output_file (str): File name for the resulting output image.
        min_scale_factor (float): Minimum scaling factor for resizing images.
        max_scale_factor (float): Maximum scaling factor for resizing images.
        lower_alpha (float): Minimum alpha transparency for pasted images (0.0 to 1.0).
        upper_alpha (float): Maximum alpha transparency for pasted images (0.0 to 1.0).
    """
    start_time = time.time()
    pasted_images = 0

    # Create a blank transparent canvas
    output_image = Image.new("RGBA", output_size, (255, 255, 255, 0))

    # Get all image files from the folder
    valid_extensions = (".png", ".jpg", ".jpeg")
    image_files = [
        os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)
    ]

    if not image_files:
        print("No valid images found in the folder.")
        return
    else:
        print(f"Found {len(image_files)} valid images in the folder.")

    with tqdm(total=100) as pbar:
        while pasted_images < max_images and (time.time() - start_time) < max_time_seconds:
            # Load a random image
            image_path = random.choice(image_files)
            try:
                img = Image.open(image_path).convert("RGBA")
            except Exception as e:
                print(f"Could not load image {image_path}: {e}")
                continue

            # Randomly rotate the image
            if rotate_only_if_vertical:
              if img.width<img.height:
                img = img.rotate(90, expand=True)
            else:
              angle = random.uniform(0, 360)
              img = img.rotate(angle, expand=True)
              if img.width<img.height//2:
                continue

            # Randomly scale the image
            if min_scale_factor != -1 and max_scale_factor != -1:
                scale_factor = random.uniform(min_scale_factor, max_scale_factor)
                new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
                #img = img.resize(new_size, Image.ANTIALIAS)
                img = img.resize(new_size, resample=Image.Resampling.LANCZOS)

            else:
                scale_factor = 1
                new_size = (int(img.width * scale_factor), int(img.height * scale_factor))

            # Randomly adjust alpha transparency
            alpha_level = random.uniform(lower_alpha, upper_alpha)
            alpha_channel = img.split()[3]  # Extract alpha channel
            alpha_channel = alpha_channel.point(lambda p: int(p * alpha_level))  # Scale alpha values
            img.putalpha(alpha_channel)  # Update image alpha channel

            # Random position to paste the image
            x = random.randint(0, output_size[0] - new_size[0])
            y = random.randint(0, output_size[1] - new_size[1])

            # Check for overlap
            region = output_image.crop((x, y, x + new_size[0], y + new_size[1]))
            region_alpha = np.array(region.split()[3])  # Extract alpha channel of the region
            img_alpha = np.array(img.split()[3])  # Extract alpha channel of the image to paste

            if np.any((region_alpha > 0) & (img_alpha > 0)):
                # Overlap detected; skip this image
                continue

            # Paste the image
            output_image.paste(img, (x, y), mask=img)
            pasted_images += 1

            # Update progress bar
            max1 = int(np.floor(100 * pasted_images / max_images))
            current_time = time.time()
            max2 = int(np.floor(100 * (current_time - start_time) / max_time_seconds))
            pbar.n = max(max1, max2)
            pbar.refresh()

    # Save the result
    output_image.save(output_file, "PNG")
    print(f"Collage created with {pasted_images} images. Saved to {output_file}.")


def create_collage_grid(output_size, folder_path, max_time_seconds=10, max_images=100,
                   output_file="output.png", min_scale_factor=-1, max_scale_factor=-1,
                   lower_alpha=0.5, upper_alpha=1.0, grid_rows=4, grid_cols=5, padding=10,
                   rotate_only_if_vertical=False):
    """
    Creates an image collage by pasting transparent images into an output canvas divided into a grid.

    Args:
        output_size (tuple): The size (width, height) of the output image.
        folder_path (str): Path to the folder containing transparent images.
        max_time_seconds (int): Maximum time in seconds for the operation.
        max_images (int): Maximum number of images to paste.
        output_file (str): File name for the resulting output image.
        min_scale_factor (float): Minimum scaling factor for resizing images.
        max_scale_factor (float): Maximum scaling factor for resizing images.
        lower_alpha (float): Minimum alpha transparency for pasted images (0.0 to 1.0).
        upper_alpha (float): Maximum alpha transparency for pasted images (0.0 to 1.0).
        grid_rows (int): Number of rows in the grid.
        grid_cols (int): Number of columns in the grid.
        padding (int): Padding around the images within each grid cell.
    """
    start_time = time.time()
    pasted_images = 0

    # Create a blank transparent canvas
    output_image = Image.new("RGBA", output_size, (255, 255, 255, 0))

    # Get grid dimensions
    grid_width = output_size[0] // grid_cols
    grid_height = output_size[1] // grid_rows

    # Get all image files from the folder
    valid_extensions = (".png", ".jpg", ".jpeg")
    image_files = [
        os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)
    ]

    if not image_files:
        print("No valid images found in the folder.")
        return
    else:
        print(f"Found {len(image_files)} valid images in the folder.")

    # Create a list of all grid cells
    grid_cells = [(col * grid_width, row * grid_height)
                  for row in range(grid_rows) for col in range(grid_cols)]

    random.shuffle(grid_cells)  # Randomize grid cell order

    with tqdm(total=max_images) as pbar:
        for _ in range(max_images):
            if not grid_cells or (time.time() - start_time) > max_time_seconds:
                break  # Stop if no grid cells are left or time is up

            # Load a random image
            image_path = random.choice(image_files)
            try:
                img = Image.open(image_path).convert("RGBA")
            except Exception as e:
                print(f"Could not load image {image_path}: {e}")
                continue

            # Randomly rotate the image
            if rotate_only_if_vertical:
              if img.width<img.height:
                img = img.rotate(90, expand=True)
            else:
              angle = random.uniform(0, 360)
              img = img.rotate(angle, expand=True)
              if img.width<img.height//2:
                continue

            # Randomly adjust alpha transparency
            alpha_level = random.uniform(lower_alpha, upper_alpha)
            alpha_channel = img.split()[3]  # Extract alpha channel
            alpha_channel = alpha_channel.point(lambda p: int(p * alpha_level))  # Scale alpha values
            img.putalpha(alpha_channel)  # Update image alpha channel

            # Crop image to remove fully transparent rows/columns
            bbox = img.getbbox()
            if not bbox:
                continue  # Skip empty images
            img = img.crop(bbox)

            # Get the next available grid cell
            cell_x, cell_y = grid_cells.pop()

            # Calculate the padded dimensions for the cell
            cell_width = grid_width - 2 * padding
            cell_height = grid_height - 2 * padding

            # Resize image to fit within the cell
            img.thumbnail((cell_width, cell_height), Image.ANTIALIAS)

            # Calculate the centered position within the grid cell
            paste_x = cell_x + (grid_width - img.width) // 2
            paste_y = cell_y + (grid_height - img.height) // 2

            # Paste the image into the canvas
            output_image.paste(img, (paste_x, paste_y), mask=img)
            pasted_images += 1
            pbar.update(1)

    # Save the result
    output_image.save(output_file, "PNG")
    print(f"Collage created with {pasted_images} images. Saved to {output_file}.")

def paste_images_in_transparent_areas(
    input_folder,
    output_image_path,
    output_image_size,
    padding,
    max_time_seconds,
    resize_factor
):
    """
    Pastes images randomly selected from a folder onto a transparent output image.
    Ensures that images are pasted with a padding around non-transparent regions.
    Stops after a specified maximum time.

    Args:
        input_folder (str): Path to the folder containing input images.
        output_image_path (str): Path to save the final output image.
        output_image_size (tuple): Size of the output image (width, height).
        padding (int): Padding between pasted images and surrounding areas.
        max_time_seconds (int): Maximum time in seconds to run the function.
    """
    # Create an empty (transparent) output image
    output_image = Image.new("RGBA", output_image_size, (0, 0, 0, 0))
    output_width, output_height = output_image_size

    start_time = time.time()  # Record the start time

    # Loop until the image has no more transparent areas to fill or time runs out
    while True:
        # Check if the maximum time has been exceeded
        elapsed_time = time.time() - start_time
        if elapsed_time >= max_time_seconds:
            print("Time limit exceeded. Stopping the process.")
            break

        # Find all transparent areas in the output image
        transparent_pixels = [
            (x, y)
            for x in range(output_width)
            for y in range(output_height)
            if output_image.getpixel((x, y))[3] == 0
        ]

        if not transparent_pixels:
            # If no transparent areas remain, we are done
            break

        # Select a random image from the input folder
        file_name = random.choice(
            [f for f in os.listdir(input_folder) if f.lower().endswith('.png')]
        )
        img_path = os.path.join(input_folder, file_name)
        img = Image.open(img_path).convert("RGBA")

        # Resize the image to a tenth of its original size, keeping the aspect ratio
        original_width, original_height = img.size
        new_width = max(1, original_width // resize_factor)  # Ensure minimum width is 1 pixel
        new_height = max(1, original_height // resize_factor)  # Ensure minimum height is 1 pixel
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Find a random position in the transparent area
        x_min = max(0, padding)
        y_min = max(0, padding)
        x_max = max(0, output_width - img.width - padding)
        y_max = max(0, output_height - img.height - padding)

        paste_x = random.randint(x_min, x_max)
        paste_y = random.randint(y_min, y_max)

        # Ensure the region is not overlapping an existing non-transparent area
        paste_region = (paste_x, paste_y, paste_x + img.width, paste_y + img.height)
        overlapping = False
        for x in range(paste_region[0], paste_region[2]):
            for y in range(paste_region[1], paste_region[3]):
                if x < output_width and y < output_height:
                    if output_image.getpixel((x, y))[3] != 0:  # Non-transparent
                        overlapping = True
                        break
            if overlapping:
                break

        if not overlapping:
            # Paste the image onto the output image
            output_image.paste(img, (paste_x, paste_y), img)
            print(f"Pasted {file_name} at {paste_x}, {paste_y}")

    # Save the final output image
    output_image.save(output_image_path)
    print(f"Final image saved to {output_image_path}")

def create_collage(output_size, folder_path, max_time_seconds=10, max_images=100,
                   output_file="output.png", min_scale_factor=-1, max_scale_factor=-1,
                   lower_alpha=0.5, upper_alpha=1.0):
    """
    Creates an image collage by pasting transparent images randomly from a folder onto an output canvas.

    Args:
        output_size (tuple): The size (width, height) of the output image.
        folder_path (str): Path to the folder containing transparent images.
        max_time_seconds (int): Maximum time in seconds for the operation.
        max_images (int): Maximum number of images to paste.
        output_file (str): File name for the resulting output image.
        min_scale_factor (float): Minimum scaling factor for resizing images.
        max_scale_factor (float): Maximum scaling factor for resizing images.
        lower_alpha (float): Minimum alpha transparency for pasted images (0.0 to 1.0).
        upper_alpha (float): Maximum alpha transparency for pasted images (0.0 to 1.0).
    """
    start_time = time.time()
    pasted_images = 0

    # Create a blank transparent canvas
    output_image = Image.new("RGBA", output_size, (255, 255, 255, 0))

    # Get all image files from the folder
    valid_extensions = (".png", ".jpg", ".jpeg")
    image_files = [
        os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)
    ]

    if not image_files:
        print("No valid images found in the folder.")
        return
    else:
        print(f"Found {len(image_files)} valid images in the folder.")

    with tqdm(total=100) as pbar:
        while pasted_images < max_images and (time.time() - start_time) < max_time_seconds:
            # Load a random image
            image_path = random.choice(image_files)
            try:
                img = Image.open(image_path).convert("RGBA")
            except Exception as e:
                print(f"Could not load image {image_path}: {e}")
                continue

            # Randomly rotate the image
            angle = random.uniform(0, 360)
            img = img.rotate(angle, expand=True)

            # Randomly scale the image
            if min_scale_factor != -1 and max_scale_factor != -1:
                scale_factor = random.uniform(min_scale_factor, max_scale_factor)
                new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
                img = img.resize(new_size, Image.ANTIALIAS)
            else:
                scale_factor = 1
                new_size = (int(img.width * scale_factor), int(img.height * scale_factor))

            # Randomly adjust alpha transparency
            alpha_level = random.uniform(lower_alpha, upper_alpha)
            alpha_channel = img.split()[3]  # Extract alpha channel
            alpha_channel = alpha_channel.point(lambda p: int(p * alpha_level))  # Scale alpha values
            img.putalpha(alpha_channel)  # Update image alpha channel

            # Random position to paste the image
            x = random.randint(0, output_size[0] - new_size[0])
            y = random.randint(0, output_size[1] - new_size[1])

            # Paste the image
            output_image.paste(img, (x, y), mask=img)

            pasted_images += 1

            # Update progress bar
            max1 = int(np.floor(100 * pasted_images / max_images))
            current_time = time.time()
            max2 = int(np.floor(100 * (current_time - start_time) / max_time_seconds))
            pbar.n = max(max1, max2)
            pbar.refresh()

    # Save the result
    output_image.save(output_file, "PNG")
    print(f"Collage created with {pasted_images} images. Saved to {output_file}.")