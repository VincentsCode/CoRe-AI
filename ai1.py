import requests
import time
import json
from Functions import play, free, get_symbol


username = "VincentsCode"
password = "vincOmOBIL89*"

def turn(board, symbol):
    # Dummy Player
    
    for i in range(8):
        for j in range(8):
            if free(i, j, board):
                return i, j

if __name__ == "__main__": play(username, password, turn)