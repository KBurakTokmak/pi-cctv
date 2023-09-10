from pi_cam.RaspCam import RaspCam


def test_RaspCam() -> None:
    cam = RaspCam(640, 480, test=True)
    assert(cam.width == 640 and cam.height == 480)


if __name__ == "__main__":
    test_RaspCam()
