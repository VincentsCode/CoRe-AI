import time

from BOAIapi import BOAIapi, MatchMethod

def transpose(array):
    array = array[:]  # make copy to avoid changing original
    n = len(array)
    for i, row in enumerate(array):
        array[i] = row + [None for _ in range(n - len(row))]

    array = zip(*array)

    for i, row in enumerate(array):
        array[i] = [elem for elem in row if elem is not None]

    return array

def turn(board, symbol):
    board = transpose(board)
    for x in range(8):
        for y in range(8):
            if board[x][y] == "#":
                return x, y

api = BOAIapi(turn, verbose=1, username="VincentsCode", password="vincOmOBIL89*")

api.match(17, mode=MatchMethod.JOIN)