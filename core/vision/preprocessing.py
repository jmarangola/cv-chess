"""
Handle data preprocessing for chessboard images
"""
import cv2
import imageio
import matplotlib
import matplotlib.pyplot as plt
from numpy.core.fromnumeric import diagonal
from pyzbar.pyzbar import decode, ZBarSymbol
import numpy as np

"""
Split raw image into quadrants
Return [list] : list of ndarray quadrant images
"""
def quad_split(nd_image, display=False):
    resolution = (nd_image.shape[0], nd_image.shape[1])
    raw_tr = np.zeros((resolution[0], resolution[1], 3))
    raw_tl = raw_tr.copy()
    raw_br = raw_tr.copy()
    raw_bl = raw_tr.copy()
    raw_tr[:resolution[0]//2+1, :resolution[1]//2+1, :] = nd_image[:resolution[0]//2+1, :resolution[1]//2+1, :]
    raw_tl[:resolution[0]//2+1, resolution[1]//2:, :] = nd_image[:resolution[0]//2+1, resolution[1]//2:, :]
    raw_br[resolution[0]//2:, :resolution[1]//2+1, :] = nd_image[resolution[0]//2:, :resolution[1]//2+1, :]
    raw_bl[resolution[0]//2:, resolution[1]//2:, :] = nd_image[resolution[0]//2:, resolution[1]//2:, :]
    result = [raw_tr, raw_tl, raw_br, raw_bl]
    
    # Display output:
    if display:
        figure, axes = plt.subplots(nrows=4, ncols=1)
        titles = ["TOP LEFT", "TOP RIGHT", "BOTTOM LEFT", "BOTTOM RIGHT"]
        for a in range(4):
            axes[a].imshow(result[a])
            axes[a].set_title(titles[a])  
        figure.tight_layout()
        plt.show()
        plt.waitforbuttonpress()
        
    return result

"""
Returns a diction of QR label:bounding box pairs. Does not find all qr codes on large images w/ small qr codes

Input: nd_image [np.ndarray] - cv2 image representation, labels [tuple, optional] default=("TL", "BL", "TR", "BR", b'https://qrs.ly/y79j33k') - valid qr labels
Return: corners [dict] - {qr label:(x, y, w, h)} pairs
"""
def extract_qr_bb(nd_image, labels=(b"TL", b"BL", b"TR", b"BR"), show_bounding_boxes=True):
    # Split image into quadrants:
    resolution = (nd_image.shape[0], nd_image.shape[1])
    (height, width) = resolution
    quadrants = quad_split(nd_image)
    corners = {}
    for quadrant in quadrants:
        codes = decode(quadrant, symbols=[ZBarSymbol.QRCODE])
        for code in codes:
            # Check if it is one of the QR codes we are looking for
            if code.data in labels:
                (x, y, w, h) = code.rect
                corners[code.data] = (x, y, w, h)
        
    # Draw bounding boxes and display the result for debugging:
    if show_bounding_boxes:
        for code in corners:
            (x, y, w, h) = corners[code]
            cv2.rectangle(nd_image, (x, y), (x + w, y + h), (0, 0, 255), 3)
        cv2.imshow("test corners", nd_image)
        cv2.waitKeyEx()
    return corners

"""
TODO Implement visualization
Returns a dictionary of qr label:polygon pairs
"""
def extract_qr_polygon(nd_image, labels=(b"TL", b"BL", b"btr", b"BR"), show_polygons=True):
    # Split image into quadrants:
    resolution = (nd_image.shape[0], nd_image.shape[1])
    (height, width) = resolution
    print((width, height))
    quadrants = quad_split(nd_image)
    corners = {}
    visual_corners = []
    for quadrant in quadrants:
        codes = decode(quadrant, symbols=[ZBarSymbol.QRCODE])
        for code in codes:
            poly_indices = {"TL":3, "TR":2, "BL":0, "BR":1} 
            opposite_ind = {"TL":1, "TR":0, "BL":2, "BR":3} 
            # Check if valid qr
            temp = code.data.decode()
            if code.data in labels:
                corners[temp] = (code.polygon[opposite_ind[temp]].x, code.polygon[opposite_ind[temp]].y)
            if show_polygons:
                cv2.rectangle(nd_image, (code.polygon[0].x, code.polygon[0].y), (code.polygon[2].x, code.polygon[2].y), (0, 0, 255), 3)
            
    # Draw bounding boxes and display the result for debugging:
    if show_polygons:
        cv2.imshow("test corners", nd_image)
        cv2.waitKeyEx()
        
    return corners
    
"""
Returns the cropped board based on qr codes at 4 corners
"""
def cropped_boad_poly(nd_image, display_result=False):
    # Get board top corners from qr codes
    qr_codes = extract_qr_polygon(nd_image, show_bounding_boxes=False)

    # Localize the board
    diagonal_pairs = [{b"TL", b"BR"}, {b"TR", b"BL"}]
    qr_elems = {code for code in qr_codes.keys()}
    # Ensure that at least one diagonal pair was decoded:
    if len(qr_codes.keys()) <= 2 and qr_elems.intersection(diagonal_pairs) not in diagonal_pairs:
        print("<Error> Cannot localize board")
        return None

    if len(qr_codes.keys()) < 4:
        # Find the single diagonal pair:
        intersections = [pair.intersection(qr_elems) for pair in diagonal_pairs]
        qr_elems = max(intersections)
        c1 = qr_elems.pop()
        c2 = qr_elems.pop()
        # TODO 
        # 
        #
        # Implement transformation and the crop for both sets of diagonal pairs
        
    else: # If all four corners of the board were recognized, optimal case
        pass
        # TODO 
        # 
        #
        # Impplement linear transformation and crop for four code case
    
    # Display the result:
    if display_result:
        cv2.imshow("Cropped board", nd_image)
        cv2.waitKeyEx()
        
    return nd_image

'''
given a board, returns a dict where each key is a tile position which is mapped to an image of that tile
'''
def cropped_board_to_tiles(img):
    CHESS_TILES = {}
    num_rows = img.shape[0]
    num_cols = img.shape[1]
    rows_per_tile = num_rows//8
    cols_per_tile = num_cols//8
    letters = "ABCDEFGH"
    for i in range(8):
        for j in range(1,9):
            CHESS_TILES[letters[i] + str(j)] = img[i * rows_per_tile : (i + 1) * rows_per_tile, (j - 1) * cols_per_tile : j * cols_per_tile] 
    return CHESS_TILES

'''
given an image, generates a random name for it and writes it
'''
def img_to_file(img):
    path = 'f' + "".join(map(str, np.random.permutation(10).tolist())) + ".jpg"
    cv2.imwrite(path, img)

'''
given a board, writes 64 files, one for each tile
'''
def board_to_64_files(img):
    CHESS_TILES = {}
    dict = cropped_board_to_tiles(img)
    for key in dict.keys():
        CHESS_TILES[key] = img_to_file(dict[key])
    return CHESS_TILES


#test_image = cv2.imread("qr-board-test.jpg")
#test_image = cv2.imread("qr-board-test.jpg")
test_image = cv2.imread("test_case_5.jpg")

extract_qr_polygon(test_image)
#raw_image_to_cropped_boad(test_image)