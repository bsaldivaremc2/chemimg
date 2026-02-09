import io
import os
from typing import Optional

from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit.Chem.Draw import rdMolDraw2D
from PIL import Image

try:
    import cairosvg
except Exception as e:
    raise RuntimeError(
        "chemimg requires Cairo (native library) to function.\n\n"
        "On Windows, install via conda:\n"
        "  conda install -c conda-forge cairo\n"
        "  pip install cairosvg\n\n"
        "On Linux:\n"
        "  sudo apt install libcairo2\n\n"
        "On macOS:\n"
        "  brew install cairo\n"
    ) from e


def draw_transparent_mol(
    ismiles: str,
    fo: str,
    increase_factor: int = 100,
    scaffold_only: bool = False,
    border_width: int = 1,
    verbose: bool = False,
) -> Optional[str]:
    """
    Render a molecule from a SMILES string as a transparent PNG image.

    The molecule is drawn using RDKit's SVG drawer, converted to PNG in memory,
    and post-processed to ensure a fully transparent background.

    Parameters
    ----------
    ismiles : str
        Input SMILES string describing the molecule.
    fo : str
        Output file path where the PNG image will be saved.
    increase_factor : int, default=100
        Scaling factor converting RDKit 2D coordinates to pixel dimensions.
        Larger values produce higher-resolution images.
    scaffold_only : bool, default=False
        If True, extract the Murcko scaffold and make it generic before drawing.
    border_width : int, default=1
        Width of bond lines in the rendered molecule.
    verbose : bool, default=False
        If True, print status messages during execution.

    Returns
    -------
    Optional[str]
        The output file path if the image was successfully created,
        or None if the molecule contained no atoms.

    Raises
    ------
    ValueError
        If the provided SMILES string is invalid.
    """

    # Parse SMILES into an RDKit molecule
    mol = Chem.MolFromSmiles(ismiles)
    if mol is None:
        raise ValueError("Invalid SMILES string")

    # Optionally extract and genericize the Murcko scaffold
    if scaffold_only:
        mol = MurckoScaffold.GetScaffoldForMol(mol)
        mol = MurckoScaffold.MakeScaffoldGeneric(mol)

    # Compute 2D coordinates for drawing
    rdDepictor.Compute2DCoords(mol)

    # Abort if molecule has no atoms (can happen for empty scaffolds)
    if mol.GetNumAtoms() == 0:
        if verbose:
            print("Mol atoms: 0")
        return None

    # Determine molecule bounding box from atomic coordinates
    conf = mol.GetConformer()
    xs = [conf.GetAtomPosition(i).x for i in range(mol.GetNumAtoms())]
    ys = [conf.GetAtomPosition(i).y for i in range(mol.GetNumAtoms())]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # Convert coordinate span to pixel dimensions
    width_px = int((max_x - min_x) * increase_factor)
    height_px = int((max_y - min_y) * increase_factor)

    # Draw molecule to SVG with transparent background
    drawer = rdMolDraw2D.MolDraw2DSVG(width_px, height_px)
    options = drawer.drawOptions()
    options.bondLineWidth = border_width
    options.setBackgroundColour((1.0, 1.0, 1.0, 0.0))  # RGBA, fully transparent

    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    svg_data = drawer.GetDrawingText()

    # Remove any SVG <rect> background elements
    svg_data = svg_data.replace("<rect", '<rect fill="none"')

    # Convert SVG to PNG in memory
    png_bytes = cairosvg.svg2png(bytestring=svg_data.encode("utf-8"))

    # Load PNG with PIL and ensure RGBA mode
    image = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

    # Make pure white pixels fully transparent (safety pass)
    new_pixels = []
    for pixel in image.getdata():
        if pixel[:3] == (255, 255, 255):
            new_pixels.append((255, 255, 255, 0))
        else:
            new_pixels.append(pixel)

    image.putdata(new_pixels)

    # Ensure output directory exists and save image
    os.makedirs(os.path.dirname(fo), exist_ok=True)
    image.save(fo, "PNG")

    if verbose:
        print("Saved (transparent):", fo)

    return fo



def draw_transparent_mol_v2024(ismiles, fo,increase_factor=100,scaffold_only=False,border_width=1):
    from rdkit import Chem
    from rdkit.Chem import Draw
    from rdkit.Chem import rdDepictor
    from rdkit.Chem.Scaffolds import MurckoScaffold
    # Generate molecule object from SMILES
    mol = Chem.MolFromSmiles(ismiles)
    if not mol:
        raise ValueError("Invalid SMILES string")
    if scaffold_only:
      mol = MurckoScaffold.GetScaffoldForMol(mol)
      mol = MurckoScaffold.MakeScaffoldGeneric(mol)

    # Prepare molecule for drawing
    rdDepictor.Compute2DCoords(mol)

    # Create a temporary drawer to calculate molecule bounds
    temp_drawer = Draw.MolDraw2DCairo(1, 1)
    temp_drawer.DrawMolecule(mol)
    temp_drawer.FinishDrawing()

    # RDKit does not provide a straightforward way to get bounds,
    # so we use a method to manually calculate bounds from atom coordinates.
    if mol.GetNumAtoms()==0:
      print("Mol atoms:0")
      return None

    conf = mol.GetConformer()
    min_x = min([conf.GetAtomPosition(i).x for i in range(mol.GetNumAtoms())])
    max_x = max([conf.GetAtomPosition(i).x for i in range(mol.GetNumAtoms())])
    min_y = min([conf.GetAtomPosition(i).y for i in range(mol.GetNumAtoms())])
    max_y = max([conf.GetAtomPosition(i).y for i in range(mol.GetNumAtoms())])

    # Calculate the size of the molecule
    width = max_x - min_x
    height = max_y - min_y

    # Set canvas size based on molecule size with no padding
    scale = increase_factor  # Scaling factor for better resolution
    width_px = int(width * scale)
    height_px = int(height * scale)

    # Create the actual drawer with the calculated size
    drawer = Draw.MolDraw2DCairo(width_px, height_px)
    options = drawer.drawOptions()
    #
    # Adjust bond line width for thicker strokes
    options.bondLineWidth = border_width  # Set this to a higher value for thicker strokes

    # Set a transparent background
    options.setBackgroundColour((1.0, 1.0, 1.0, 0.0))

    # Draw the molecule
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()

    # Save the image with a transparent background
    image_data = drawer.GetDrawingText()
    dn = os.path.dirname(fo)
    #print(dn)
    os.makedirs(dn, exist_ok=True)
    with open(fo, "wb") as f:
        f.write(image_data)

    print("Saved:", fo)

