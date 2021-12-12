"""
Dataset related classes

John Marangola - marangol@bc.edu 
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
    Function for visualizing chessboard objects as images
    """
    def display_board(self, dest=None):
        # Create base chess board of B/W pixels
        tile_colors = np.zeros(64*3).reshape(8, 8, 3)
        tile_colors[1::2, :-1:2, :] = 1
        tile_colors[::2, 1::2, :] = 1
        # Scale up board to 1024x1024:
        resized_board = cv2.resize(tile_colors, (1024, 1024), 0, 0, interpolation=cv2.INTER_NEAREST)
        x_translation = {x:ord(x) - ord("A")  for x in list("ABCDEFGH")}
        # Labels for visual board
        visual_labels = {
                            PieceType.PAWN: "P",
                            PieceType.KING: "K", 
                            PieceType.KNIGHT: "KN", 
                            PieceType.BISHOP: "B",
                            PieceType.QUEEN: "Q",
                        }
        visual_colors = {PieceColor.ORANGE : (0, 0, 255), PieceColor.BLUE : (255, 0, 0)}
        for position in self.board:
            if self.board[position] is not None:
                center_x = (int(x_translation[position[0]])) * 1024//8 + 1024//32
                center_y = 1024  - (int(position[1]) - 1) * 1024//8 - 1024//32
                font = cv2.FONT_HERSHEY_SIMPLEX
                # Label board with proper pieces and colors 
                if self.board[position].piece_type != PieceType.KNIGHT:
                    cv2.putText(resized_board, visual_labels[self.board[position].piece_type], (center_x,center_y), font, 3, visual_colors[self.board[position].piece_color], 2, cv2.LINE_8)
                # Knight label has two characters, ensure it is centered
                else:
                    cv2.putText(resized_board, visual_labels[self.board[position].piece_type], (center_x-35,center_y), font, 3, visual_colors[self.board[position].piece_color], 2, cv2.LINE_8)
        if dest is None:
            cv2.imshow("cv-chessboard test", resized_board)
            # Wait to kill the board image
            cv2.waitKey(100000) 
        else:
            cv2.imwrite(dest, 255*resized_board)
        
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
    
    """
    Return a .csv representation of the board
    """
    def to_csv(self):
        datafr = pd.DataFrame(
            {   "Position" : [position for position in sorted(self.board.keys())],
                "Piece Type" : [self.board[position].piece_type.name for position in sorted(self.board.keys())], 
                "Piece Color" : [self.board[position].piece_color.name for position in sorted(self.board.keys())], 
                "Tile Color" : [self.get_tile_color(position).name for position in sorted(self.board.keys())]
            }
        )
        return datafr