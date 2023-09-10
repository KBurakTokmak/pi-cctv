from PIL import Image

from FastAPI_backend.utils.image_utils import ExifOrientationNormalize


def test_ExifOrientationNormalize():
    test_image = Image.open("tests/test_image.jpg")
    preprocess = ExifOrientationNormalize()
    processed_image = preprocess(test_image)
    assert(test_image == processed_image)


if __name__ == "__main__":
    test_ExifOrientationNormalize()
