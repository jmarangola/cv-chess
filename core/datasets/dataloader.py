"""
Upload the dataset
"""
import numpy as np
from enum import Enum
from numpy.core.fromnumeric import resize
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cv2
from time import sleep
import os


# Chessboard tile color enum
class TileColor(Enum):
    BLACK = 1
    WHITE = 2 

# Chess piece enum
class PieceType(Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6
  
# An object that encapsulates the piece and piece color associated with that piece at a chess tile (both are None in absence of piece)
class ChessPiece:
    def __init__(self, piece_type=None, piece_color=None):
        self.piece_type = piece_type
        self.piece_color = piece_color
  
  # Return array representation of Tile object 
    def to_array(self):
        return [self.position, self.piece, self.tile_color]

# Class for color of chess pieces
class PieceColor(Enum):
    ORANGE = 1
    BLUE = 2
  
# Chessboard Class used to easily access any attributes of the chessboard or the pieces on the chessboard 
class Board:
    # Dictionary of {Position : TileColor} values
    CHESS_TILES = {list("ABCDEFGH")[x]+str(y):TileColor((y+x+1)%2+1) for x in range(len(list("ABCDEFGH"))) for y in range(1, 9)} 
    VISUAL_PATH = r"../../resources/visual"
    def __init__(self):
        self.board = {}
        self.n_pieces = 0
        
    """ 
    Add a single piece to the board @ a position (ex. "A1")
    Parameters: piece_data (dict) format: {position : Tile()}
    """
    def add_pieces(self, pieces_dict):
        for key in pieces_dict: 
            # Increment piece number if it is a new square:
            if key not in self.board: 
                self.n_pieces += 1
            # Add piece to dictionary self.board:
            self.board[key.upper()] = pieces_dict[key]
            
    """
    Visualize chessboard object as an image
    """
    def display_board(self):
        images = {}
        for filename in os.listdir(self.VISUAL_PATH):
            img = cv2.imread(os.path.join(self.VISUAL_PATH,filename), 1)
            if img is not None:
                images[filename] = img
        tile_colors = np.zeros(64*3).reshape(8, 8, 3)
        tile_colors[1::2, :-1:2, :] = 1
        tile_colors[::2, 1::2, :] = 1
        resized_board = cv2.resize(tile_colors, (1024, 1024), 0, 0, interpolation=cv2.INTER_NEAREST)
        offset = 20
        piece_size = (1024//8-offset, 1024//8-offset)
        resized_piece = cv2.resize(np.array(images["orange_queen.png"]), piece_size, 0, 0, interpolation = cv2.INTER_AREA)
        x_translation = {x:ord(x) - ord("A")  for x in list("ABCDEFGH")}
        hf_piece_sz = (piece_size[0]//2, piece_size[1]//2)
        visual_labels = {
                            PieceType.PAWN: "P",
                            PieceType.KING: "K", 
                            PieceType.KNIGHT: "KN", 
                            PieceType.BISHOP: "B",
                            PieceType.QUEEN: "Q",
                        }
        #rgb = lambda h: tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) 
        visual_colors = {PieceColor.ORANGE : (0, 10, 255), PieceColor.BLUE : (255, 0, 0)}
        for position in self.board:
            print(position)
            if self.board[position] is not None:
                center_x = (int(x_translation[position[0]])) * 1024//8 + 1024//32
                center_y = 1024  - (int(position[1]) - 1) * 1024//8 - 1024//32
                font = cv2.FONT_HERSHEY_SIMPLEX
                if self.board[position].piece_type != PieceType.KNIGHT:
                    cv2.putText(resized_board, visual_labels[self.board[position].piece_type], (center_x,center_y), font, 3, visual_colors[self.board[position].piece_color], 2, cv2.LINE_8)
                else:
                    cv2.putText(resized_board, visual_labels[self.board[position].piece_type], (center_x-35,center_y), font, 3, visual_colors[self.board[position].piece_color], 2, cv2.LINE_8)
        cv2.imshow("cv-chessboard test", resized_board)
        cv2.waitKey(100000) # kill board image
        
    """
    Returns the ChessPiece at a position, returns None if empty
    """
    def get_chess_piece(self, position):
        return self.board.get(position, None)
    
    """
    Get color of the chessboard at a position 
    Returns: TileColor object
    """ 
    def get_tile_color(self, position):
        return self.CHESS_TILES[position.upper()]
        
board = Board()
board.add_pieces({"e2":ChessPiece(PieceType.PAWN, PieceColor.ORANGE)})

# Examples:
# 
# get color of chessboard at random tiles
print("Colors of chessboard at A8:")
print(board.get_tile_color("A8"))
print("Color of chessboard at H8:")
print(board.get_tile_color("H8"))
print()
#
#
# Get piece at A4 (empty):
print("Checking empty square A4:")
print(board.get_chess_piece("A4")) 
print()
#
# Add orange pawn to A4:
print("Adding orange pawn to A4 and checking again:")
board.add_pieces({"A4":ChessPiece(PieceType.KNIGHT, PieceColor.BLUE)})
# Get piece at A4 again:
a4 = board.get_chess_piece("A4")
print(a4.piece_type)
print(a4.piece_color)
# print the tile color of a4
print("tile color: ",  end='')
print(board.get_tile_color("a4"))

board.display_board()