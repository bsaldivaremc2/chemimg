from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit.Chem.Draw import rdMolDraw2D
from PIL import Image
import cairosvg
import io
import os

def draw_transparent_mol(ismiles, fo, increase_factor=100, scaffold_only=False, border_width=1,verbose=False):
    # Generate molecule
    mol = Chem.MolFromSmiles(ismiles)
    if not mol:
        raise ValueError("Invalid SMILES string")
    
    if scaffold_only:
        mol = MurckoScaffold.GetScaffoldForMol(mol)
        mol = MurckoScaffold.MakeScaffoldGeneric(mol)

    # Compute 2D coordinates
    rdDepictor.Compute2DCoords(mol)
    
    if mol.GetNumAtoms() == 0:
        print("Mol atoms: 0")
        return None

    # Determine bounds
    conf = mol.GetConformer()
    min_x = min([conf.GetAtomPosition(i).x for i in range(mol.GetNumAtoms())])
    max_x = max([conf.GetAtomPosition(i).x for i in range(mol.GetNumAtoms())])
    min_y = min([conf.GetAtomPosition(i).y for i in range(mol.GetNumAtoms())])
    max_y = max([conf.GetAtomPosition(i).y for i in range(mol.GetNumAtoms())])

    width_px = int((max_x - min_x) * increase_factor)
    height_px = int((max_y - min_y) * increase_factor)

    # Draw molecule to SVG
    drawer = rdMolDraw2D.MolDraw2DSVG(width_px, height_px)
    options = drawer.drawOptions()
    options.bondLineWidth = border_width
    options.setBackgroundColour((1.0, 1.0, 1.0, 0.0))  # transparent
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    svg_data = drawer.GetDrawingText()

    # Remove any rect background in SVG
    svg_data = svg_data.replace('<rect', '<rect fill="none"')

    # Convert SVG → PNG in memory
    png_bytes = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))

    # Load PNG in PIL and ensure transparency
    image = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

    # Make white pixels fully transparent (optional, in case some remained)
    datas = image.getdata()
    newData = []
    for item in datas:
        # If pixel is nearly white, make it transparent
        if item[:3] == (255, 255, 255):
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    image.putdata(newData)

    # Save the PNG
    os.makedirs(os.path.dirname(fo), exist_ok=True)
    image.save(fo, "PNG")
    if verbose:
        print("Saved (transparent):", fo)


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

