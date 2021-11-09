"""
Downloads the dataset given its google drive address.
"""
import numpy as np
from enum import Enum


class Tile(Enum):
  BLACK = 1
  WHITE = 2

class Piece(Enum):
  PAWN = 1
  KNIGHT = 2
  BISHOP = 3
  ROOK = 4
  QUEEN = 5
  KING = 6
  EMPTY = 9

class Color(Enum):
  ORANGE = 1
  BLUE = 2
  EMPTY = 9

class Board:
  def __init__(self):
    self.board = {}
    self.a = 'b'
    cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    for col in cols[::2]:
      for num in range(1, 9, 2):
        self.board[col + str(num)] = [Tile(1), Piece(9), Color(9)]
    for col in cols[::2]:
      for num in range(2, 9, 2):
        self.board[col + str(num)] = [Tile(2), Piece(9), Color(9)]
    for col in cols[1::2]:
      for num in range(1, 9, 2):
        self.board[col + str(num)] = [Tile(2), Piece(9), Color(9)]
    for col in cols[1::2]:
      for num in range(2, 9, 2):
        self.board[col + str(num)] = [Tile(1), Piece(9), Color(9)]
  
  def add_piece(self, tile, piece, color):
    self.board[tile][1] = Piece(piece)
    self.board[tile][2] = Color(color)

  def add_pieces(self, pieces):
    for piece in pieces:
      self.add_piece(piece[0], piece[1], piece[2])

  def show(self, tile):
    print(self.board[tile])


my_board = Board()

pieces = [['A1', Piece.ROOK, Color.ORANGE], ['A8', Piece.PAWN, Color.BLUE],
          ['A2', Piece.PAWN, Color.ORANGE], ['B8', Piece.ROOK, Color.BLUE],
          ['B1', Piece.KNIGHT, Color.ORANGE], ['D8', Piece.KNIGHT, Color.BLUE],
          ['B2', Piece.PAWN, Color.ORANGE], ['G8', Piece.KNIGHT, Color.BLUE],
          ['C1', Piece.PAWN, Color.ORANGE], ['A7', Piece.BISHOP, Color.BLUE],
          ['C2', Piece.PAWN, Color.ORANGE], ['C7', Piece.BISHOP, Color.BLUE],
          ['D1', Piece.PAWN, Color.ORANGE], ['B6', Piece.BISHOP, Color.BLUE],
          ['D2', Piece.BISHOP, Color.ORANGE], ['D7', Piece.PAWN, Color.BLUE],
          ['E1', Piece.BISHOP, Color.ORANGE], ['H7', Piece.ROOK, Color.BLUE],
          ['E2', Piece.PAWN, Color.ORANGE], ['A6', Piece.KNIGHT, Color.BLUE],
          ['F1', Piece.KNIGHT, Color.ORANGE], ['E6', Piece.KNIGHT, Color.BLUE],
          ['F2', Piece.PAWN, Color.ORANGE], ['C5', Piece.PAWN, Color.BLUE],
          ['G2', Piece.PAWN, Color.ORANGE], ['D5', Piece.PAWN, Color.BLUE],
          ['H2', Piece.ROOK, Color.ORANGE], ['G5', Piece.ROOK, Color.BLUE]]

my_board.add_pieces(pieces)
