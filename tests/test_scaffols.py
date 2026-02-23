import os
import pytest
from PIL import Image

from chemimg.chem.scaffolds import draw_transparent_mol


# -------------------------
# Fixtures
# -------------------------

@pytest.fixture
def tmp_png(tmp_path):
    """Temporary output PNG path."""
    return tmp_path / "mol.png"


# -------------------------
# Basic functionality
# -------------------------

def test_draw_valid_smiles_creates_png(tmp_png):
    smiles = "CCO"  # ethanol

    out = draw_transparent_mol(
        ismiles=smiles,
        fo=str(tmp_png),
    )

    assert out is not None
    assert os.path.exists(out)

    img = Image.open(out)
    assert img.format == "PNG"
    assert img.mode == "RGBA"


def test_output_is_transparent(tmp_png):
    smiles = "c1ccccc1"  # benzene

    draw_transparent_mol(
        ismiles=smiles,
        fo=str(tmp_png),
    )

    img = Image.open(tmp_png).convert("RGBA")
    pixels = list(img.getdata())

    # At least some pixels should be transparent
    assert any(pixel[3] == 0 for pixel in pixels)


# -------------------------
# Error handling
# -------------------------

def test_invalid_smiles_raises_value_error(tmp_png):
    with pytest.raises(ValueError):
        draw_transparent_mol(
            ismiles="this_is_not_smiles",
            fo=str(tmp_png),
        )


# -------------------------
# Scaffold behavior
# -------------------------

def test_scaffold_only_runs(tmp_png):
    smiles = "CC1=CC=CC=C1"  # ethylbenzene

    out = draw_transparent_mol(
        ismiles=smiles,
        fo=str(tmp_png),
        scaffold_only=True,
    )

    assert out is not None
    assert os.path.exists(out)


def test_empty_scaffold_returns_none(tmp_png):
    """
    Some molecules can produce empty Murcko scaffolds.
    Aliphatic chains are a good example.
    """
    smiles = "CCCCCCCC"

    out = draw_transparent_mol(
        ismiles=smiles,
        fo=str(tmp_png),
        scaffold_only=True,
    )

    assert out is None
    assert not tmp_png.exists()


# -------------------------
# Options & parameters
# -------------------------

def test_border_width_parameter(tmp_png):
    smiles = "CCO"

    out = draw_transparent_mol(
        ismiles=smiles,
        fo=str(tmp_png),
        border_width=3,
    )

    assert out is not None
    assert os.path.exists(out)


def test_verbose_does_not_crash(tmp_png, capsys):
    smiles = "CCO"

    draw_transparent_mol(
        ismiles=smiles,
        fo=str(tmp_png),
        verbose=True,
    )

    captured = capsys.readouterr()
    assert "Saved" in captured.out
