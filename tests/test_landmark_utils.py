import numpy as np

from src.vision.landmark_utils import denormalize


def test_denormalize_scales_normalized_coordinates_to_pixels():
    landmarks = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.5, 0.5, 0.0],
            [1.0, 1.0, 0.0],
        ],
        dtype=np.float32,
    )

    pixels = denormalize(landmarks, image_width=100, image_height=200)

    assert pixels.dtype == np.int32
    np.testing.assert_array_equal(pixels, [[0, 0], [50, 100], [100, 200]])


def test_denormalize_ignores_z_coordinate():
    landmarks = np.array([[0.25, 0.75, 999.0]], dtype=np.float32)

    pixels = denormalize(landmarks, image_width=400, image_height=400)

    np.testing.assert_array_equal(pixels, [[100, 300]])
