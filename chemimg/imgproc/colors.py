from PIL import Image
import os

def change_to_white(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Loop through all files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith('.png'):
            # Open the image
            file_path = os.path.join(input_folder, file_name)
            img = Image.open(file_path).convert("RGBA")

            # Process the image
            data = img.getdata()
            new_data = []
            for item in data:
                # If the pixel is not transparent, change it to white
                if item[3] > 0:  # Alpha channel > 0 means not transparent
                    new_data.append((255, 255, 255, 255))  # White with full opacity
                else:
                    new_data.append(item)  # Keep the transparent pixel unchanged

            # Save the modified image
            img.putdata(new_data)
            output_path = os.path.join(output_folder, file_name)
            img.save(output_path)

            print(f"Processed and saved: {output_path}")

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

            # Process the image
            data = img.getdata()
            new_data = []
            for item in data:
                # If the pixel is black and fully opaque, change it to the replacement color
                if item[:3] == original_color and item[3] > 0:  # RGB is black and alpha > 0
                    new_data.append((*replacement_color, 255))  # Replacement color with full opacity
                else:
                    new_data.append(item)  # Keep other pixels unchanged

            # Save the modified image
            img.putdata(new_data)
            output_path = os.path.join(output_folder, file_name)
            img.save(output_path)

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

            # Process the image
            data = img.getdata()
            new_data = []
            for item in data:
                # If the pixel is black and fully opaque, change it to the replacement color
                if item[:3] == original_color and item[3] > 0:  # RGB is black and alpha > 0
                    new_data.append((*replacement_color, 255))  # Replacement color with full opacity
                else:
                    new_data.append(item)  # Keep other pixels unchanged

            # Save the modified image
            img.putdata(new_data)
            output_path = os.path.join(output_folder, file_name)
            img.save(output_path)

            #print(f"Processed and saved: {output_path}")