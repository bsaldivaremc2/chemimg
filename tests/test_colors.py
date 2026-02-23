import os
import numpy as np
import pytest
from PIL import Image

from chemimg.imgproc.colors import (
    change_color_to_color_np,
    change_color_to_color_fast,
)


@pytest.fixture
def simple_rgba_image():
    """
    Create a 3x3 RGBA image:
    - center pixel is black and opaque
    - corners are red and opaque
    - one pixel is transparent
    """
    data = np.array([
        [[255, 0, 0, 255], [255, 0, 0, 255], [255, 0, 0, 255]],
        [[255, 0, 0, 255], [0,   0, 0, 255], [255, 0, 0, 255]],
        [[255, 0, 0, 255], [255, 0, 0,   0], [255, 0, 0, 255]],
    ], dtype=np.uint8)

    return Image.fromarray(data, mode="RGBA")


def test_change_specific_color(simple_rgba_image):
    """Only the target RGB color should be replaced."""
    out = change_color_to_color_np(
        simple_rgba_image,
        original_color=(0, 0, 0),
        replacement_color=(0, 255, 0),
        any_color=False,
    )

    arr = np.array(out)

    # Center pixel should be green
    assert tuple(arr[1, 1, :3]) == (0, 255, 0)

    # Red pixels unchanged
    assert tuple(arr[0, 0, :3]) == (255, 0, 0)


def test_any_color_replaces_all_nontransparent(simple_rgba_image):
    """All pixels with alpha > 0 should be replaced."""
    out = change_color_to_color_np(
        simple_rgba_image,
        replacement_color=(0, 0, 255),
        any_color=True,
    )

    arr = np.array(out)

    # Opaque pixels should be blue
    assert tuple(arr[0, 0, :3]) == (0, 0, 255)
    assert tuple(arr[1, 1, :3]) == (0, 0, 255)

    # Transparent pixel should remain transparent
    assert arr[2, 1, 3] == 0


def test_alpha_channel_preserved(simple_rgba_image):
    """Alpha values must not be modified."""
    out = change_color_to_color_np(
        simple_rgba_image,
        replacement_color=(123, 123, 123),
        any_color=True,
    )

    original_alpha = np.array(simple_rgba_image)[:, :, 3]
    new_alpha = np.array(out)[:, :, 3]

    assert np.array_equal(original_alpha, new_alpha)


def test_change_color_fast_single_file(tmp_path, simple_rgba_image):
    """Single image file input → single output file."""
    input_file = tmp_path / "input.png"
    output_file = tmp_path / "output.png"

    simple_rgba_image.save(input_file)

    change_color_to_color_fast(
        str(input_file),
        str(output_file),
        original_color=(0, 0, 0),
        replacement_color=(255, 255, 0),
    )

    assert output_file.exists()

    out = Image.open(output_file)
    arr = np.array(out)

    # Center pixel should be yellow
    assert tuple(arr[1, 1, :3]) == (255, 255, 0)


def test_change_color_fast_directory(tmp_path, simple_rgba_image):
    """Directory input → directory output."""
    input_dir = tmp_path / "in"
    output_dir = tmp_path / "out"

    input_dir.mkdir()
    img_path = input_dir / "test.png"
    simple_rgba_image.save(img_path)

    change_color_to_color_fast(
        str(input_dir),
        str(output_dir),
        any_color=True,
        replacement_color=(10, 20, 30),
    )

    out_img_path = output_dir / "test.png"
    assert out_img_path.exists()

    out = Image.open(out_img_path)
    arr = np.array(out)

    # Any non-transparent pixel should be replaced
    assert tuple(arr[0, 0, :3]) == (10, 20, 30)
