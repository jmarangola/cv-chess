"""
Initialize on empty board -> store coordinates in SETUP_FILE
"""
import cv2
from preprocessing import extract_qr_polygon
import realsense_utils as realu

SETUP_FILE = "setup.txt"

"""
"""
def initialize():
    image = realu.get_rgb_image()
    extract_qr_polygon(image, show_polygons=False)
    cv2.imwrite("testfile.jpg", image)

    """data = (20, 20, 30, 30)
    with open(SETUP_FILE, "w") as wr:
        wr.write("\n".join(map(str, data)))
    """
initialize()