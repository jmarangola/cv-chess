"""
Handle preprocessing for chessboard
"""
import cv2
import imageio
import matplotlib.pyplot as plt
from pyzbar.pyzbar import decode, ZBarSymbol
import numpy as np

"""
Returns a diction of QR label:bounding rect pairs

Input: nd_image [np.ndarray] - cv2 image representation, labels [tuple, optional] default=("TL", "BL", "TR", "BR", b'https://qrs.ly/y79j33k') - valid qr labels
Return: corners [dict] - {qr label:(x, y, w, h)} pairs
"""
def extract_qr(nd_image, labels=(b"TL", b"BL", b"TR", b"BR"), show_bounding_boxes=True):
    im2 = cv2.cvtColor(nd_image, cv2.COLOR_BGR2GRAY)
    codes = decode(im2, symbols=[ZBarSymbol.QRCODE])
    corners = {}
    print(codes)
    for code in codes:
        print(code.data)
        # Check if it is one of the QR codes we are looking for
        if code.data in labels:
            (x, y, w, h) = code.rect
            corners[code.data] = (x, y, w, h)
            # Draw bounding boxes
            if show_bounding_boxes: 
                cv2.rectangle(nd_image, (x, y), (x + w, y + h), (0, 0, 255), 3)
    if show_bounding_boxes:
        cv2.imshow("test corners", nd_image)
        cv2.waitKey(5000)
    print(corners)
    return corners
        
"""
Returns the cropped board based on qr codes at 4 corners
"""
def raw_image_to_cropped_boad(nd_image, display_result=True):
    # Get board top corners from qr codes
    qr_codes = extract_qr(nd_image, show_bounding_boxes=False)
    
    # Bottom right of top left QR:
    temp = np.array(qr_codes["TL"])
    tl = np.array((temp[0], temp[1])) + np.array(temp[2], temp[3])
    # Bottom left of top right QR:
    temp = np.array(qr_codes["TR"])
    tr = np.array((temp[0], temp[1])) + np.array(0, temp[3])
    # Top right of bottom left QR:
    temp = np.array(qr_codes["BL"])
    bl = np.array((temp[0], temp[1])) + np.array(temp[2], 0)
    # Top left of bottom right QR:
    temp = np.array(qr_codes["BR"])
    br = np.array((temp[0], temp[1]))
    
    # Crop the image:
    nd_image = nd_image[tl:bl+1, tr:br+1, :] 

    # Display the result:
    if display_result:
        cv2.imshow("Cropped board", nd_image)
        cv2.waitKey(5000)
        
    return nd_image

test_image = cv2.imread("qr-board-test.jpg")
extract_qr(test_image)
