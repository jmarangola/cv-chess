"""
Handle data preprocessing for chessboard images
"""
import cv2
import matplotlib
import matplotlib.pyplot as plt
from numpy.core.fromnumeric import diagonal
from pyzbar.pyzbar import decode, ZBarSymbol
import numpy as np
from os.path import isfile, join
import os 

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
        cv2.imshow("Test Corners", nd_image)
        cv2.waitKeyEx()
    return corners

"""
Returns a dictionary of qr label:polygon pairs
"""
def extract_qr_polygon(nd_image, labels=(b"TL", b"BL", b"TR", b"BR"), show_polygons=True):
    # Split image into quadrants:
    if nd_image is None:
        print("image not found.")
        return None
    resolution = (nd_image.shape[0], nd_image.shape[1])
    (height, width) = resolution
    print((width, height))
    quadrants = quad_split(nd_image)
    corners = {}
    visual_corners = []
    for quadrant in quadrants:
        codes = decode(quadrant, symbols=[ZBarSymbol.QRCODE])
        for code in codes:
            poly_indices = {"TL":3, "btr":2, "BL":0, "BR":2} 
            opposite_ind = {"TL":2, "btr":0, "BL":2, "BR":0} 
            # Check if valid qr
            temp = code.data.decode()
            if code.data in labels:
                corners[temp] = (code.polygon[opposite_ind[temp]].x, code.polygon[opposite_ind[temp]].y)
                cv2.rectangle(nd_image, (code.polygon[0].x, code.polygon[0].y), (code.polygon[2].x, code.polygon[2].y), (0, 0, 255), 3)
        
    # Draw bounding boxes and display the result for debugging:
    if show_polygons:
        cv2.imshow("test corners", nd_image)
        cv2.waitKeyEx()
        
    return corners
    
"""
Get four corners of chessboard from polygon extraction 

Return: [list] four corners - [[x1, y1, ], [x2, y2], ..., [x4, y4]]
"""
def get_four_corners(nd_image, display_corners=False, display_color=255):
    decoded = extract_qr_polygon(nd_image, show_polygons=False)
    
    # Check if there is enough information to return the four corners
    if len(decoded.keys()) < 2 or ("TL" in decoded.keys() and "TR" in decoded.keys()) or ("BL" in decoded.keys() and "BR" in decoded.keys()):
        print("Could not find enough qr codes to perform image preprocessing")
        return None
    if len(decoded.keys()) == 4:
        output = [[decoded["TL"][0], decoded["TL"][1]], [decoded["TR"][0], decoded["TR"][1]], [decoded["BL"][0], decoded["BL"][1]], [decoded["BR"][0], decoded["BR"][1]]] 
    else:    
        if ("TL" in decoded.keys() and "BR" in decoded.keys()):
            output =  [[decoded["TL"][0], decoded["TL"][1]], [decoded["BR"][0], decoded["BR"][1]]]
        else:
            output =  [[decoded["TR"][0], decoded["TR"][1]], [decoded["BL"][0], decoded["BL"][1]]]

    print(nd_image.shape)
    print(output)
    # Quick debug display
    if display_corners:
        display_image = nd_image.copy()
        for point in output:
            cv2.line(display_image, [point[0] - 5, point[1]], [point[0] + 5, point[1]], (0, 0, 255), 3)
            cv2.line(display_image, [point[0], point[1] - 5] , [point[0], point[1] + 5], (0, 0, 255), 3)
        cv2.imshow("Corner Display", display_image)
        cv2.waitKey(10000)
            
    return output

"""
'Quick and dirty' implementation without warp
"""
def cropped_boad_poly(nd_image, display_result=False, crop_pad=(0, 0)):
    # Get board top corners from qr codes
    if nd_image is None:
        print("image not found.")
        return None
    original_image = nd_image.copy()
    qr_codes = extract_qr_polygon(nd_image, show_polygons=False)

    # Localize the board
    diagonal_pairs = [{"TL", "BR"}, {"TR", "BL"}]
    qr_elems = {code for code in qr_codes.keys()}
    
    # Ensure that at least one diagonal pair was decoded:
    if len(qr_codes.keys()) <= 2 and qr_elems.intersection(diagonal_pairs[0]) not in diagonal_pairs and qr_elems.intersection(diagonal_pairs[1]) not in diagonal_pairs:
        print("<Error> Cannot localize board")
        return None

    intersections = [pair.intersection(qr_elems) for pair in diagonal_pairs]
    qr_elems = max(intersections)
    # Use diagonal pair to get board with reasonable accuracy
    if len(qr_codes.keys()) < 4:
        # Find the single diagonal pair:
        print("TL") if "TL" in qr_elems else "TR"
        nd_image = nd_image[qr_codes["TL"][1]:qr_codes["BR"][1]+1,qr_codes["TL"][0]:qr_codes["BR"][0]+1,:] if "TL" in qr_elems else nd_image[qr_codes["TR"][1]:qr_codes["BL"][1]+1,qr_codes["TR"][0]:qr_codes["BL"][0]+1,:]
    else:   # Use diagonal pairings for better accuracy if 4 points have been found
        nd_image = nd_image[qr_codes["TL"][1]:qr_codes["BR"][1]+1, qr_codes["TR"][0]:qr_codes["BL"][0]+1, :]
    # Display the result:
    if display_result:
        figure, axes = plt.subplots(nrows=1, ncols=2)
        axes[0].imshow(original_image)
        axes[0].set_title("Original")
        axes[1].imshow(nd_image)
        axes[1].set_title("Cropped Version")
        figure.tight_layout()
        plt.show()
        plt.waitforbuttonpress()
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
    print(CHESS_TILES["A1"])
    return CHESS_TILES

'''
given an image, generates a random name for it and writes it
'''
def img_to_file(img, base_directory=None):
    name = 'f' + "".join(map(str, np.random.permutation(10).tolist())) + ".jpg"
    if base_directory is None:
        wpath = name
    else: 
        wpath = base_directory + 'f' + "".join(map(str, np.random.permutation(10).tolist())) + ".jpg"
    cv2.imwrite(wpath, img)
    return name

'''
given a board, writes 64 files, one for each tile
'''
def board_to_64_files(img, base_directory=None):
    CHESS_TILES = {}
    filenames = {}
    dict = cropped_board_to_tiles(img)
    for key in dict.keys():
        CHESS_TILES[key] = img_to_file(dict[key], base_directory=base_directory)
    return CHESS_TILES

"""
Delete all the output .jpgs saved by board_to_64_tiles(img) 
"""
def delete_board2_64_output(base_directory=None):
    if base_directory is None:
        files = [f for f in os.listdir(os.getcwd()) if isfile(os.path.join(os.getcwd(), f))]
        for file in files:
            if file[-4:] == ".jpg" and file[0] == "f":
                os.remove(file)
    else:
        files = [f for f in os.listdir(base_directory) if isfile(os.path.join(base_directory, f))]
        for file in files:
            if file[-4:] == ".jpg" and file[0] == "f":
                os.remove(base_directory + file)
            
def warp(img, corners):
    """
    Warp img by applying perspective transform based on the positions of four chessboard corners (found during calibration)

    Args:
        img (ndarray): input image
        corners (list): [description]

    Returns:
        ndarray: warped output
    """
    img = cv2.imread('test_case_3.jpg',0)
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    pt_A, pt_B, pt_C, pt_D = corners[0], corners[1], corners[2], corners[3]
 
    width_AD = np.sqrt(((pt_A[0] - pt_D[0]) ** 2) + ((pt_A[1] - pt_D[1]) ** 2))
    width_BC = np.sqrt(((pt_B[0] - pt_C[0]) ** 2) + ((pt_B[1] - pt_C[1]) ** 2))
    maxWidth = max(int(width_AD), int(width_BC))
    height_AB = np.sqrt(((pt_A[0] - pt_B[0]) ** 2) + ((pt_A[1] - pt_B[1]) ** 2))
    height_CD = np.sqrt(((pt_C[0] - pt_D[0]) ** 2) + ((pt_C[1] - pt_D[1]) ** 2))
    maxHeight = max(int(height_AB), int(height_CD))

    input_pts = np.float32([pt_A, pt_B, pt_C, pt_D])
    output_pts = np.float32([[0, 0],
                            [0, maxHeight - 1],
                            [maxWidth - 1, maxHeight - 1],
                            [maxWidth - 1, 0]])

    M = cv2.getPerspectiveTransform(input_pts,output_pts)
    out = cv2.warpPerspective(img,M,(maxWidth, maxHeight),flags=cv2.INTER_LINEAR)
    return out

