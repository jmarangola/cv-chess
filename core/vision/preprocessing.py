"""
Handle preprocessing for chessboard
"""
import cv2
import imageio
import matplotlib.pyplot as plt
from pyzbar.pyzbar import decode
import numpy as np

"""
Returns a diction of Label:Bounding Rect pairs
Bounding rect: (x, y, w, h) tuple
"""
def extract_qr(nd_image, labels=("TL", "BL", "TR", "BR", b'https://qrs.ly/y79j33k'), show_bounding_boxes=True):
    codes = decode(nd_image)
    corners = {}
    for code in codes:
        print(code.data)
        # Check if it is one of the QR codes we are looking for
        if code.data in labels:
            (x, y, w, h) = code.rect
            corners[code.data] = (x, y, w, h)
            # Draw bounding boxes
            if show_bounding_boxes: 
                cv2.rectangle(nd_image, (x, y), (x + w, y + h), (0, 0, 255), 2)
    if show_bounding_boxes:
        cv2.imshow("test corners", nd_image)
        cv2.waitKey(5000)
    print(corners)
        
"""
Return resized img to size resolution
"""
def resize(img, resolution=(800, 800)):
    pass # TODO

"""
Return the cropped image at the four corners, 
"""
def crop_and_div(img, img_corners):
    pass # TODO

test_image = cv2.imread("original-5181958-3.jpg")
extract_qr(test_image, )
