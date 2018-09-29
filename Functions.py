import requests
import time
import json

url = "https://games.battleofai.net/api/"
account_management_url = "https://iam.battleofai.net/api/"


def free(x, y, board):
    if board[x][y] == '#':
        return True
    return False
def create_game():
    resp = requests.post(url + "games/createGame", json={"game_name": "Core"})
    assert resp.status_code == 200
    return int(resp.text)
def register_player(game_id, player_id, token):
    resp = requests.post(url+"games/"+str(game_id) + "/registerPlayer", json={"id": player_id, "token": token})
    assert resp.status_code == 200
    return 'true' in resp.text
def login(username, password):
    login_data = {
        "username": username,
        "password": password
    }
    resp = requests.post(account_management_url + "iam/login", json=login_data)
    if not resp.status_code == 200:
        exit("Account Management temporarily unavailable")
    if resp.json()["userid"] is None or resp.json()["token"] is None or resp.json()["session_token"] is None:
        exit("Invalid login credentials")
    return (resp.json()["userid"], str([resp.json()["token"], resp.json()["session_token"]]))
def get_symbol(active_player): return 'XO'[active_player]
def get_game_info(game_id):
    return requests.get(url + "games/" + str(game_id)).json()
def check_and_update_token(playerid, token, username, password):
    unwrapped_token = token.replace("['", "").replace("']", "").split("', '")
    data = {
        "userid": playerid,
        "token": unwrapped_token[0],
        "session_token": unwrapped_token[1]
    }
    resp = requests.post(account_management_url + "iam/validateToken", json=data)
    if not resp.status_code == 200 or resp.json()["success"] == False:
        return login(username, password)[1]
    return token
def play(username, password, turn, id=-1):
    # LOGIN
    player_id, token = login(username, password)
    print("logged in successfully")

    if id == -1:
        game_id = -1
        while game_id == -1:
            game_id = create_game()
            if not register_player(game_id, player_id, token):
                game_id = -1
            print("Created game.\nGameID =", game_id)

        # WAIT FOR ALL PLAYERS TO REGISTER
        waiting = True
        while waiting:
            game_state = requests.get(url + "games/" + str(game_id)).json()["game_state"]
            if not game_state == "WAITING":
                waiting = False
                continue
            print("WAITING FOR OTHER PLAYERS")
            time.sleep(5)
    else:
        game_id = -1
        resp = requests.post(url + "games/" + str(id) + "/registerPlayer", json={"id": player_id, "token": token})
        print(resp.text)
        game_id = id
        print("Joined game.\n")

    
    # CHECK IF ALL WENT WELL
    game_info = requests.get(url + "games/" + str(game_id)).json()
    registered = False
    for _, i in enumerate(game_info["players"]):
        if i['id'] == player_id:
            registered = True
            break
    assert registered
    assert game_info["game_name"] == "Core"
    assert game_info["id"] == game_id
    assert game_info["game_state"] == "STARTED"
    assert game_info["open_slots"] == 0

    # PLAY
    is_ongoing = True
    print("PLAYING THE GAME " + str(game_id))
    while is_ongoing:
        game_info = requests.get(url + "games/" + str(game_id)).json()
        if not game_info["game_state"] == "STARTED":
            break
        is_active = game_info["players"][game_info["active_player"]]["id"] == player_id
        if is_active:
            pos_x, pos_y = turn(game_info['history'][-1]['board'], get_symbol(game_info["active_player"]))
            status_code = 401
            while status_code == 401:
                token = check_and_update_token(player_id, token, username, password)
                data = {"player": {"id": player_id, "token": token}, "turn": str([pos_x, pos_y])}
                resp = requests.post(url + "games/" + str(game_id) + "/makeTurn", json=data)
                if resp.status_code == 200 and 'false' in resp.text:
                    is_ongoing = False
                status_code = resp.status_code
        time.sleep(5)
    return True