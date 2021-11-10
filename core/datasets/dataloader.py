"""
Upload the dataset
"""
import numpy as np
from enum import Enum
import pandas as pd

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
    def print(self):
        # TODO implement pandas df or matplotlib table  to visualize pieces on board
        pass
    
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
board.add_pieces({"A4":ChessPiece(PieceType.PAWN, PieceColor.ORANGE)})
# Get piece at A4 again:
a4 = board.get_chess_piece("A4")
print(a4.piece_type)
print(a4.piece_color)
# print the tile color of a4
print("tile color: ",  end='')
print(board.get_tile_color("a4"))

