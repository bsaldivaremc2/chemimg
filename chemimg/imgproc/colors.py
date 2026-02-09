import os
from typing import Tuple

import numpy as np
from PIL import Image
from tqdm import tqdm

def change_color_to_color_np(
    img: Image.Image,
    original_color: Tuple[int, int, int] = (0, 0, 0),
    replacement_color: Tuple[int, int, int] = (255, 255, 255),
    any_color: bool = False
) -> Image.Image:
    """
    Replace a specific RGB color (or any non-transparent color) in an image.

    The operation is performed using NumPy for fast pixel-wise manipulation.
    Transparency (alpha channel) is preserved.

    Parameters
    ----------
    img : PIL.Image.Image
        Input image to process.
    original_color : Tuple[int, int, int], optional
        RGB color to replace. Ignored if `any_color=True`.
    replacement_color : Tuple[int, int, int], optional
        RGB color to apply where the mask matches.
    any_color : bool, optional
        If True, replace all non-transparent pixels regardless of color.

    Returns
    -------
    PIL.Image.Image
        A new image with the color replacements applied.
    """
    # Convert image to RGBA to ensure alpha channel exists
    data: np.ndarray = np.array(img.convert("RGBA"))

    # Separate RGB and alpha channels
    rgb: np.ndarray = data[:, :, :3]
    alpha: np.ndarray = data[:, :, 3]

    # Build mask:
    # - any_color=True: replace all pixels with alpha > 0
    # - otherwise: replace only pixels matching original_color and alpha > 0
    if any_color:
        mask: np.ndarray = alpha > 0
    else:
        mask = np.all(rgb == original_color, axis=-1) & (alpha > 0)

    # Apply replacement color to masked pixels
    data[mask, :3] = replacement_color

    return Image.fromarray(data)


def change_color_to_color_fast(
    input_path: str,
    output_path: str,
    original_color: Tuple[int, int, int] = (0, 0, 0),
    replacement_color: Tuple[int, int, int] = (255, 255, 255),
    any_color: bool = False
) -> None:
    """
    Apply color replacement to a single image or all images in a directory.

    Supported image formats: PNG, JPG, JPEG, WEBP.

    Parameters
    ----------
    input_path : str
        Path to an image file or a directory containing images.
    output_path : str
        Destination file path (for single input file) or output directory.
    original_color : Tuple[int, int, int], optional
        RGB color to replace. Ignored if `any_color=True`.
    replacement_color : Tuple[int, int, int], optional
        RGB color to apply where the mask matches.
    any_color : bool, optional
        If True, replace all non-transparent pixels regardless of color.

    Returns
    -------
    None
    """
    # Determine if input is a single file or a directory
    if os.path.isfile(input_path):
        files_to_process = [input_path]
        is_single_file = True
    elif os.path.isdir(input_path):
        files_to_process = [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
        ]
        is_single_file = False
    else:
        print(f"Error: {input_path} is neither a file nor a directory.")
        return

    # Process images with progress bar
    for file_path in tqdm(files_to_process, desc="Processing images"):
        img: Image.Image = Image.open(file_path)

        new_img: Image.Image = change_color_to_color_np(
            img,
            original_color=original_color,
            replacement_color=replacement_color,
            any_color=any_color
        )

        # Determine save path
        if is_single_file:
            # If output_path is a directory, keep original filename
            if os.path.isdir(output_path) or output_path.endswith(('/', '\\')):
                os.makedirs(output_path, exist_ok=True)
                save_path = os.path.join(output_path, os.path.basename(file_path))
            else:
                # output_path is treated as a file path
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                save_path = output_path
        else:
            # Directory input always writes to output directory
            os.makedirs(output_path, exist_ok=True)
            save_path = os.path.join(output_path, os.path.basename(file_path))

        new_img.save(save_path)

def recolor_pixels_with_pillow(img, original_color=(0, 0, 0), replacement_color=(255, 0, 0)):
    """
    Replaces a specific RGB color with a new color in an RGBA image.
    Returns a new Image object.
    """
    # Ensure image is in RGBA mode to handle transparency correctly
    img_rgba = img.convert("RGBA")
    
    data = img_rgba.getdata()
    new_data = []
    
    for item in data:
        # item is (R, G, B, A)
        # Check if RGB matches original_color and pixel is not fully transparent
        if item[:3] == original_color and item[3] > 0:
            # Apply replacement color, keeping it fully opaque (255)
            new_data.append((*replacement_color, 255))
        else:
            new_data.append(item)

    # Create a new image to hold the modified data
    new_img = Image.new("RGBA", img_rgba.size)
    new_img.putdata(new_data)
    
    return new_img

def change_color_to_color(input_folder, output_folder, original_color=(0,0,0),replacement_color=(255,255,255)):
    """
    Changes black (0, 0, 0) pixels with full opacity to a specified color in PNG images.

    Args:
        input_folder (str): Path to the input folder containing images.
        output_folder (str): Path to the output folder where processed images will be saved.
        replacement_color (tuple): RGB tuple for the new color (e.g., (255, 0, 0) for red).
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Loop through all files in the input folder
    for file_name in tqdm(os.listdir(input_folder)):
        if file_name.lower().endswith('.png'):
            # Open the image
            file_path = os.path.join(input_folder, file_name)
            img = Image.open(file_path).convert("RGBA")
            img = recolor_pixels_with_pillow(img, original_color, replacement_color)
            output_path = os.path.join(output_folder, file_name)
            img.save(output_path)
