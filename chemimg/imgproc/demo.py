import os
from ..chem.scaffolds import draw_transparent_mol
from PIL import Image

import matplotlib.pyplot as plt
import math

def show_images_grid(
    image_paths,
    input_ratio=(1, 2),
    figsize_factor=3.0
):
    """
    image_paths : list of str
        Paths to images to load
    input_ratio : tuple (rows, cols)
        Desired layout ratio (e.g. (1,2), (2,2))
    figsize_factor : float
        Size multiplier per subplot
    """

    n_images = len(image_paths)
    r, c = input_ratio

    # --- determine grid layout ---
    if r == c:
        # make it as square as possible
        cols = int(math.ceil(math.sqrt(n_images)))
        rows = int(math.ceil(float(n_images) / cols))
    else:
        # keep ratio, scale grid until it fits all images
        scale = math.ceil(
            max(float(n_images) / (r * c), 1)
        )
        rows = int(r * scale)
        cols = int(c * scale)

    # --- compute figsize ---
    figsize = (cols * figsize_factor, rows * figsize_factor)

    fig, axes = plt.subplots(rows, cols, figsize=figsize)

    # Make axes iterable in all cases
    if rows * cols == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    # --- plot images ---
    for i, ax in enumerate(axes):
        if i < n_images:
            img_path = image_paths[i]
            img = Image.open(img_path)

            ax.imshow(img)
            ax.axis("off")

            # title = filename
            ax.set_title(os.path.basename(img_path), fontsize=9)
        else:
            ax.axis("off")

    plt.tight_layout()
    plt.show()


def generate_grid(ismiles, out_dir, border_widths, scales, scaffold_only=False, prefix="mol"):
    """
    Generate images for a molecule or its scaffold with varying border widths and scales,
    save them in out_dir, and return a grid image.
    
    Parameters:
    - ismiles: str, SMILES of the molecule
    - out_dir: str, directory to save images
    - border_widths: list of ints, border widths to loop over (N)
    - scales: list of ints, increase_factor for chemimg (M)
    - scaffold_only: bool, whether to draw only the scaffold
    - prefix: str, prefix for saved filenames
    
    Returns:
    - PIL.Image of the NxM grid
    """
    os.makedirs(out_dir, exist_ok=True)
    tmp_files = []

    # Generate images
    for bw in border_widths:
        for scale in scales:
            tmp_file = os.path.join(out_dir, f"{prefix}_bw{bw}_scale{scale}.png")
            draw_transparent_mol(
                ismiles,
                tmp_file,
                increase_factor=scale,
                scaffold_only=scaffold_only,
                border_width=bw
            )
            tmp_files.append(tmp_file)
    
    # Load images
    images = [Image.open(f) for f in tmp_files]
    widths, heights = zip(*(i.size for i in images))
    
    # Grid dimensions
    N = len(border_widths)
    M = len(scales)
    grid_image = Image.new('RGBA', (max(widths)*M, max(heights)*N), (255,255,255,0))
    
    for i, img in enumerate(images):
        row = i // M
        col = i % M
        x = col * max(widths)
        y = row * max(heights)
        grid_image.paste(img, (x, y), img)
    
    # Save grid
    grid_file = os.path.join(out_dir, f"{prefix}_grid.png")
    grid_image.save(grid_file)
    print(f"Grid saved as {grid_file}")
    
    return grid_image

