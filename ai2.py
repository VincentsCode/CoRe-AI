import requests
import time
import json
import random

from enum import Enum

from Functions import play, free, get_symbol, get_game_info

username = "VincentsCode2"
password = "vincOmOBIL89*"

# a_id = int(str(requests.get("https://games.battleofai.net/api/games/").text.split(", {")[-1]).replace('"id": ', "").replace('}]}\n', ""))
a_id = 190

# WEIGHTS
BIAS = 50
# Corners
SECURE_CORNER = 90
INSECURE_CORNER = 30
LOCK_CORNER = 90
OVERTAKE_CORNER = 110
# All fields
SECURE_FIELD = 40

# Evaluate all turns
def evaluate(board):
    turns = {}
    for i in range(8):
        for j in range(8):
            if free(i, j, board):
                turns[(i, j)] = [BIAS]
    
    game_info = get_game_info(a_id)

    # corners
    corners = [(0,0), (0, 7), (7, 0), (7, 7)]
    corner_flippers = [(1, 1), (1, 6), (6, 1), (6, 6)]

    idx = 0
    for c in corners:
        if board[c[0]][c[1]] == "#":
            # field has no owner
            if board[corner_flippers[idx][0]][corner_flippers[idx][1]] != "#":
                # corner_flipper already has an owner
                turns[(c[0], c[1])].append(SECURE_CORNER)
            else:
                # corner_flipper has no owner
                turns[(c[0], c[1])].append(INSECURE_CORNER)
        elif board[c[0]][c[1]] == get_symbol(game_info["active_player"]):
            # field is owned by you -> secure field
            c_flipper = (corner_flippers[idx][0], corner_flippers[idx][1])
            if free(c_flipper[0], c_flipper[1], board):
                turns[c_flipper].append(LOCK_CORNER)
        else:
            # field is owned by enemy -> get field
            c_flipper = (corner_flippers[idx][0], corner_flippers[idx][1])            
            if free(c_flipper[0], c_flipper[1], board):
                turns[c_flipper].append(OVERTAKE_CORNER)
        idx += 1

    # security und chips gotten
    sym = get_symbol(game_info["active_player"])
    for x, y in turns:
        turns[(x, y)].append(gets_chips(x, y, board, sym) * 10)
        turns[(x, y)].append(risks_chips(x, y, board, sym) * 10)
        turns[(x, y)].append(securely_prepares_chips(x, y, board, sym) * 5)


    for t in turns:
        turns[t] = sum(turns[t])
    return turns

# how many of my chips are in danger
def risked_chips(board, symbol):
    r_chips = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] is symbol: # is me (pot risk)
                top_enemy = False
                bot_enemy = False
                right_enemy = False
                left_enemy = False

                top_empty = False
                bot_empty = False
                right_empty = False
                left_empty = False

                # top
                for i in range(0, y):
                    if board[x][i] is "#":
                        top_empty = True
                    elif board[x][i] is not symbol: # enemy
                        top_enemy = True

                # bot
                for i in range(y, 8):
                    if board[x][i] is "#":
                        bot_empty = True
                    elif board[x][i] is not symbol: # enemy
                        bot_enemy = True
                
                # right
                for i in range(0, x):
                    if board[i][y] is "#":
                        right_empty = True
                    elif board[i][y] is not symbol: # enemy
                        right_enemy = True

                # left
                for i in range(x, 8):
                    if board[i][y] is "#":
                        left_empty = True
                    elif board[i][y] is not symbol: # enemy
                        left_enemy = True

                # eval
                if top_enemy and bot_empty: r_chips += 1
                elif bot_enemy and top_empty: r_chips += 1
                elif right_enemy and left_empty: r_chips += 1
                elif left_enemy and right_empty: r_chips += 1

    return r_chips

# makes X to O and O to X
def reverse_symbol(symbol):
    if symbol == "X":
        return "O"
    else:
        return "X"

# how many enemy chips are in danger
def risked_enemy_chips(board, symbol):
    r_chips = 0
    symbol = reverse_symbol(symbol)
    for x in range(8):
        for y in range(8):
            if board[x][y] is symbol: # is me (pot risk)
                top_enemy = False
                bot_enemy = False
                right_enemy = False
                left_enemy = False

                top_empty = False
                bot_empty = False
                right_empty = False
                left_empty = False

                # top
                for i in range(0, y):
                    if board[x][i] is "#":
                        top_empty = True
                    elif board[x][i] is not symbol: # enemy
                        top_enemy = True

                # bot
                for i in range(y, 8):
                    if board[x][i] is "#":
                        bot_empty = True
                    elif board[x][i] is not symbol: # enemy
                        bot_enemy = True
                
                # right
                for i in range(0, x):
                    if board[i][y] is "#":
                        right_empty = True
                    elif board[i][y] is not symbol: # enemy
                        right_enemy = True

                # left
                for i in range(x, 8):
                    if board[i][y] is "#":
                        left_empty = True
                    elif board[i][y] is not symbol: # enemy
                        left_enemy = True

                # eval
                if top_enemy and bot_empty: r_chips += 1
                elif bot_enemy and top_empty: r_chips += 1
                elif right_enemy and left_empty: r_chips += 1
                elif left_enemy and right_empty: r_chips += 1
    return r_chips

# how much chips would i get
def gets_chips(x, y, board, symbol):
    num_get = 0

    # top
    pending_pts = 0
    for i in range(y, 0, -1):
        if board[x][i] is symbol: # me
            num_get += pending_pts
            break
        elif board[x][i] is not "#": # enemy
            pending_pts += 1

    # bot
    pending_pts = 0
    for i in range(y, 8, 1):
        if board[x][i] is symbol: # me
            num_get += pending_pts
            break
        elif board[x][i] is not "#": # enemy
            pending_pts += 1
            
    # right    
    pending_pts = 0
    for i in range(x, 8, 1):
        if board[i][y] is symbol: # me
            num_get += pending_pts
            break
        elif board[i][y] is not "#": # enemy
            pending_pts += 1

    # left    
    pending_pts = 0
    for i in range(x, 0, -1):
        if board[i][y] is symbol: # me
            num_get += pending_pts
            break
        elif board[i][y] is not "#": # enemy
            pending_pts += 1
    if num_get > 2:
        print(x, y, num_get)
    return num_get

# how many chips would i risk
def risks_chips(x, y, board, symbol):
    init_risked_chips = risked_chips(board, symbol)
    
    n_board = board
    n_board[x][y] = symbol
    # top
    for i in range(y, 0, -1):
        if n_board[x][i] is symbol: # me
            for i in range(y, i, -1):
                n_board[x][i] = symbol
            break

    # bot
    for i in range(y, 8, 1):
        if n_board[x][i] is symbol: # me
            for i in range(y, i, 1):
                n_board[x][i] = symbol
            break
            
    # right
    for i in range(x, 8, 1):
        if n_board[i][y] is symbol: # me
            for i in range(x, i, 1):
                n_board[i][y] = symbol
            break

    # left
    for i in range(x, 0, -1):
        if n_board[i][y] is symbol: # me
            for i in range(x, i, -1):
                n_board[i][y] = symbol
            break


    new_risked_chips = risked_chips(n_board, symbol)

    return init_risked_chips - new_risked_chips

# how many chips can securely be prepared for being taken
def securely_prepares_chips(x, y, board, symbol):
    r_chips = 0
    if board[x][y] is symbol: # is me (pot risk)
        top_enemy = False
        bot_enemy = False
        right_enemy = False
        left_enemy = False

        top_empty = False
        bot_empty = False
        right_empty = False
        left_empty = False

        # top
        for i in range(0, y):
            if board[x][i] is "#":
                top_empty = True
            elif board[x][i] is not symbol: # enemy
                top_enemy = True

        # bot
        for i in range(y, 8):
            if board[x][i] is "#":
                bot_empty = True
            elif board[x][i] is not symbol: # enemy
                bot_enemy = True

        # right
        for i in range(0, x):
            if board[i][y] is "#":
                right_empty = True
            elif board[i][y] is not symbol: # enemy
                right_enemy = True

        # left
        for i in range(x, 8):
            if board[i][y] is "#":
                left_empty = True
            elif board[i][y] is not symbol: # enemy
                left_enemy = True

        # eval
        if top_enemy and bot_empty: r_chips += 1
        elif bot_enemy and top_empty: r_chips += 1
        elif right_enemy and left_empty: r_chips += 1
        elif left_enemy and right_empty: r_chips += 1
    if r_chips != 0:
        return 0 # not secure
    
    ini = risked_enemy_chips(board, symbol)
    board[x][y] = symbol
    n = risked_enemy_chips(board, symbol)

    return (ini - n) *-1

def turn(board, symbol):
    turns = evaluate(board)
    s = [(k, turns[k]) for k in sorted(turns, key=turns.get, reverse=True)]
    print(s)
    print(s[0][0])

    return s[0][0]


if __name__ == "__main__": play(username, password, turn, id=a_id)