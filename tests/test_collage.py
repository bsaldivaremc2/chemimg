import os
import numpy as np
import pytest
from PIL import Image

from chemimg.imgproc.collage import create_collage_randomNoCollapse


@pytest.fixture
def temp_image_folder(tmp_path):
    """
    Creates a temporary folder with a few transparent PNG images.
    """
    img_dir = tmp_path / "images"
    img_dir.mkdir()

    for i in range(5):
        img = Image.new("RGBA", (50, 30), (255, 0, 0, 128))
        img.save(img_dir / f"img_{i}.png")

    return img_dir


def test_create_collage_random_no_collapse_creates_output(tmp_path, temp_image_folder):
    output_file = tmp_path / "collage.png"

    create_collage_randomNoCollapse(
        output_size=(200, 200),
        folder_path=str(temp_image_folder),
        max_time_seconds=1,
        max_images=3,
        output_file=str(output_file),
        min_scale_factor=0.5,
        max_scale_factor=1.0,
        lower_alpha=0.5,
        upper_alpha=1.0,
    )

    assert output_file.exists(), "Collage output file was not created"

    # Verify the image is loadable
    img = Image.open(output_file)
    assert img.size == (200, 200)
    assert img.mode == "RGBA"


def test_empty_folder_does_not_crash(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    output_file = tmp_path / "collage.png"

    # Should not raise
    create_collage_randomNoCollapse(
        output_size=(100, 100),
        folder_path=str(empty_dir),
        max_time_seconds=1,
        max_images=5,
        output_file=str(output_file),
    )

    assert not output_file.exists(), "Output should not be created for empty input folder"
