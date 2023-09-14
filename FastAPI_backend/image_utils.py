from PIL import Image

exif_orientation_tag = 0x0112
exif_transpose_sequences = [
    [],
    [],
    [Image.FLIP_LEFT_RIGHT],
    [Image.ROTATE_180],
    [Image.FLIP_TOP_BOTTOM],
    [Image.FLIP_LEFT_RIGHT, Image.ROTATE_90],
    [Image.ROTATE_270],
    [Image.FLIP_TOP_BOTTOM, Image.ROTATE_90],
    [Image.ROTATE_90],
]


class ExifOrientationNormalize:
    def __call__(self, img: Image.Image):
        if 'parsed_exif' in img.info and exif_orientation_tag in img.info['parsed_exif']:
            orientation = img.info['parsed_exif'][exif_orientation_tag]
            transposes = exif_transpose_sequences[orientation]
            for trans in transposes:
                img = img.transpose(trans)
        return img
