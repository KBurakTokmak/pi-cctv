import joblib
from db_operations import log_person_to_database
from face_recognition.face_recogniser import Face
from image_utils import ExifOrientationNormalize
from PIL import Image, ImageDraw

# define constants
MODEL_PATH = 'model/face_recogniser.pkl'
CONFIDENCE_TRESHOLD = 0.49
DRAW_MARGIN = 5


def load_model() -> joblib.load:
    """"loads the trained model"""
    return joblib.load(MODEL_PATH)


def find_faces(img: Image.Image, model: joblib.load) -> list:
    return model(img)


def process_face(face: Face, img: Image.Image, draw: ImageDraw.Draw) -> None:
    """Takes face data and writes name on the image and logs to database"""
    if face.top_prediction.confidence < CONFIDENCE_TRESHOLD:
        text = "Unknown Person"
    else:
        text = f"{face.top_prediction.label.upper()} {face.top_prediction.confidence * 100:.2f}%"
    # bounding box
    draw.rectangle(
        (
            (int(face.bb.left), int(face.bb.top)),
            (int(face.bb.right), int(face.bb.bottom))
        ),
        outline='green',
        width=2
    )
    # text background
    draw.rectangle(
        (
            (int(face.bb.left - DRAW_MARGIN), int(face.bb.bottom) + DRAW_MARGIN),
            (int(face.bb.left + (len(text) * 6) + DRAW_MARGIN), int(face.bb.bottom) + 5 + 3 * DRAW_MARGIN)
        ),
        fill='black'
    )
    # write face name
    draw.text((int(face.bb.left), int(face.bb.bottom) + 2 * DRAW_MARGIN), text)
    log_person_to_database(text)


def write_faces_on_image(faces, img: Image.Image) -> None:
    """Writes names of given faces to given image"""
    draw = ImageDraw.Draw(img)
    for face in faces:
        process_face(face, img, draw)


def pre_process_image(img_path: str) -> Image.Image:
    """Preprocess the image before face receognition to match correct format"""
    preprocess = ExifOrientationNormalize()
    img = Image.open(img_path)
    img = preprocess(img)
    img = img.convert('RGB')
    return img


def find_and_write_name_on_image(img_path: str) -> None:
    """Find known or unknown faces on the image and write the names"""
    img = pre_process_image(img_path)
    model = load_model()
    faces = find_faces(img, model)
    if faces:
        write_faces_on_image(faces, img)
    else:
        log_person_to_database("No face Unkown Person")
    img.save(img_path)
