import io
import os
from typing import Optional, Tuple, Set

from rdkit import Chem
from rdkit.Chem import rdDepictor, AllChem
from rdkit.Chem.Draw import rdMolDraw2D
from PIL import Image
import cairosvg


from rdkit.Chem import rdFMCS


def draw_mcs_parts_pair(
    smiles1: str,
    smiles2: str,
    fo1: str,
    fo2: str,
    increase_factor: int = 100,
    border_width: int = 1,
    highlight_color: Tuple[float, float, float] = (0.2, 0.8, 0.2),
    verbose: bool = False,
    ring_matches_ring_only: bool = True,
    complete_rings_only: bool = True,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Render two molecules highlighting only their Maximum Common Substructure (MCS)
    and save both as transparent PNG images.

    Parameters
    ----------
    smiles1 : str
        First molecule.
    smiles2 : str
        Second molecule.
    fo1 : str
        Output path for molecule 1 PNG.
    fo2 : str
        Output path for molecule 2 PNG.
    increase_factor : int
        Coordinate to pixel scaling.
    border_width : int
        Bond line width.
    highlight_color : tuple
        RGB highlight color.
    verbose : bool
        Print progress messages.
    ring_matches_ring_only : bool
        Restrict ring atoms to match only rings.
    complete_rings_only : bool
        Require full rings in MCS.

    Returns
    -------
    Tuple[Optional[str], Optional[str]]
        Output file paths.
    """

    mol1 = Chem.MolFromSmiles(smiles1)
    mol2 = Chem.MolFromSmiles(smiles2)

    if mol1 is None or mol2 is None:
        raise ValueError("Invalid SMILES string provided")

    # ---------- Find MCS ----------
    mcs_result = rdFMCS.FindMCS(
        [mol1, mol2],
        ringMatchesRingOnly=ring_matches_ring_only,
        completeRingsOnly=complete_rings_only,
        atomCompare=rdFMCS.AtomCompare.CompareElements,
        bondCompare=rdFMCS.BondCompare.CompareOrder,
    )

    if mcs_result.numAtoms == 0:
        if verbose:
            print("No MCS found")
        return None, None

    mcs_mol = Chem.MolFromSmarts(mcs_result.smartsString)

    match1 = mol1.GetSubstructMatch(mcs_mol)
    match2 = mol2.GetSubstructMatch(mcs_mol)

    def get_bonds_from_atoms(mol, atom_indices: Tuple[int, ...]) -> Set[int]:
        bonds = set()
        atom_set = set(atom_indices)

        for bond in mol.GetBonds():
            a1 = bond.GetBeginAtomIdx()
            a2 = bond.GetEndAtomIdx()
            if a1 in atom_set and a2 in atom_set:
                bonds.add(bond.GetIdx())

        return bonds

    bonds1 = get_bonds_from_atoms(mol1, match1)
    bonds2 = get_bonds_from_atoms(mol2, match2)

    def draw_and_save(mol, atoms, bonds, fo):
        rdDepictor.Compute2DCoords(mol)

        if mol.GetNumAtoms() == 0:
            return None

        conf = mol.GetConformer()
        xs = [conf.GetAtomPosition(i).x for i in range(mol.GetNumAtoms())]
        ys = [conf.GetAtomPosition(i).y for i in range(mol.GetNumAtoms())]

        width_px = int((max(xs) - min(xs)) * increase_factor)
        height_px = int((max(ys) - min(ys)) * increase_factor)

        drawer = rdMolDraw2D.MolDraw2DSVG(width_px, height_px)
        options = drawer.drawOptions()
        options.bondLineWidth = border_width
        options.setBackgroundColour((1.0, 1.0, 1.0, 0.0))

        atom_colors = {i: highlight_color for i in atoms}
        bond_colors = {i: highlight_color for i in bonds}

        drawer.DrawMolecule(
            mol,
            highlightAtoms=list(atoms),
            highlightBonds=list(bonds),
            highlightAtomColors=atom_colors,
            highlightBondColors=bond_colors,
        )

        drawer.FinishDrawing()
        svg_data = drawer.GetDrawingText()
        svg_data = svg_data.replace("<rect", '<rect fill="none"')

        png_bytes = cairosvg.svg2png(bytestring=svg_data.encode("utf-8"))
        image = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

        # Make white transparent
        new_pixels = []
        for pixel in image.getdata():
            if pixel[:3] == (255, 255, 255):
                new_pixels.append((255, 255, 255, 0))
            else:
                new_pixels.append(pixel)
        image.putdata(new_pixels)

        os.makedirs(os.path.dirname(fo), exist_ok=True)
        image.save(fo, "PNG")

        return fo

    out1 = draw_and_save(mol1, match1, bonds1, fo1)
    out2 = draw_and_save(mol2, match2, bonds2, fo2)

    if verbose:
        print("Saved MCS highlight images:", out1, out2)

    return out1, out2



def draw_shared_morgan_parts_pair(
    smiles1: str,
    smiles2: str,
    fo1: str,
    fo2: str,
    radius: int = 2,
    nbits: int = 2048,
    increase_factor: int = 100,
    border_width: int = 1,
    highlight_color: Tuple[float, float, float] = (0.2, 0.8, 0.2),
    verbose: bool = False,
    ignore_radius: list = []
) -> Tuple[Optional[str], Optional[str]]:
    """
    Render two molecules highlighting the structural regions shared
    according to Morgan fingerprint bits and save both as transparent PNG.

    Parameters
    ----------
    smiles1 : str
        First molecule.
    smiles2 : str
        Second molecule.
    fo1 : str
        Output path for molecule 1 PNG.
    fo2 : str
        Output path for molecule 2 PNG.
    radius : int
        Morgan fingerprint radius.
    nbits : int
        Fingerprint size.
    increase_factor : int
        Coordinate to pixel scaling.
    border_width : int
        Bond line width.
    highlight_color : tuple
        RGB highlight color.
    verbose : bool
        Print progress messages.

    Returns
    -------
    Tuple[Optional[str], Optional[str]]
        Output file paths.
    """

    mol1 = Chem.MolFromSmiles(smiles1)
    mol2 = Chem.MolFromSmiles(smiles2)

    if mol1 is None or mol2 is None:
        raise ValueError("Invalid SMILES string provided")

    # ---------- Morgan fingerprints with bitInfo ----------
    bitInfo1 = {}
    bitInfo2 = {}

    fp1 = AllChem.GetMorganFingerprintAsBitVect(
        mol1, radius, nBits=nbits, bitInfo=bitInfo1
    )
    fp2 = AllChem.GetMorganFingerprintAsBitVect(
        mol2, radius, nBits=nbits, bitInfo=bitInfo2
    )

    shared_bits: Set[int] = set(fp1.GetOnBits()) & set(fp2.GetOnBits())

    def collect_highlights(mol, bitInfo):
        atoms: Set[int] = set()
        bonds: Set[int] = set()

        for bit in shared_bits:
            for atom_idx, rad in bitInfo.get(bit, []):
                if rad in ignore_radius:
                    continue
                env = Chem.FindAtomEnvironmentOfRadiusN(mol, rad, atom_idx)

                atoms.add(atom_idx)

                for bond_idx in env:
                    bonds.add(bond_idx)
                    bond = mol.GetBondWithIdx(bond_idx)
                    atoms.add(bond.GetBeginAtomIdx())
                    atoms.add(bond.GetEndAtomIdx())

        return atoms, bonds

    atoms1, bonds1 = collect_highlights(mol1, bitInfo1)
    atoms2, bonds2 = collect_highlights(mol2, bitInfo2)

    def draw_and_save(mol, atoms, bonds, fo):
        rdDepictor.Compute2DCoords(mol)

        if mol.GetNumAtoms() == 0:
            return None

        conf = mol.GetConformer()
        xs = [conf.GetAtomPosition(i).x for i in range(mol.GetNumAtoms())]
        ys = [conf.GetAtomPosition(i).y for i in range(mol.GetNumAtoms())]

        width_px = int((max(xs) - min(xs)) * increase_factor)
        height_px = int((max(ys) - min(ys)) * increase_factor)

        drawer = rdMolDraw2D.MolDraw2DSVG(width_px, height_px)
        options = drawer.drawOptions()
        options.bondLineWidth = border_width
        options.setBackgroundColour((1.0, 1.0, 1.0, 0.0))

        atom_colors = {i: highlight_color for i in atoms}
        bond_colors = {i: highlight_color for i in bonds}

        drawer.DrawMolecule(
            mol,
            highlightAtoms=list(atoms),
            highlightBonds=list(bonds),
            highlightAtomColors=atom_colors,
            highlightBondColors=bond_colors,
        )

        drawer.FinishDrawing()
        svg_data = drawer.GetDrawingText()
        svg_data = svg_data.replace("<rect", '<rect fill="none"')

        png_bytes = cairosvg.svg2png(bytestring=svg_data.encode("utf-8"))
        image = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

        # Make white transparent
        new_pixels = []
        for pixel in image.getdata():
            if pixel[:3] == (255, 255, 255):
                new_pixels.append((255, 255, 255, 0))
            else:
                new_pixels.append(pixel)
        image.putdata(new_pixels)

        os.makedirs(os.path.dirname(fo), exist_ok=True)
        image.save(fo, "PNG")

        return fo

    out1 = draw_and_save(mol1, atoms1, bonds1, fo1)
    out2 = draw_and_save(mol2, atoms2, bonds2, fo2)

    if verbose:
        print("Saved shared highlight images:", out1, out2)

    return out1, out2

