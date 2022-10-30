#!/usr/bin/env python3
"""
Detectives today started sifting the evidences at the Tudor Hall, home of the late Dr.Black who was found
murdered last Thursday evening. A number of suspects - guests of Dr.Black - are being questioned. A collection of items
said to be the possible murder weapons have been found too.
"""

import socket
import re
import random
import sys
import time
import itertools

players = []
nicknames = []
members = {}
players_deck = {}
player_point = {}
secret_deck = {}
valid_name_pattern = r'[A-Za-z0-9-_]*'
game_art1 = '''
==================================================================
Welcome to the classic detective game: 
==================================================================
'''
game_art2 = '''
 .d8888b.     888                                          
d88P  Y88b    888                                          
888    888    888                                         
888           888    888  888     .d88b.       
888           888    888  888    d8P  Y8b     
888    888    888    888  888    88888888     
Y88b  d88P    888    Y88b 888    Y8b.        
 "Y8888P"     888     "Y88888     "Y8888      
 '''
game_art3 = '''
==================================================================
Let the investigation begin...
==================================================================
 
'''
option_table = """  
================================================
||........Suspects.......||......Weapons......||
||  1.) Colonel Mustard  ||  1.) Dagger       ||
||  2.) Professor Plum   ||  2.) Candlestick  ||
||  3.) Reverend Green   ||  3.) Revolver     ||
||  4.) Mrs. Peacock     ||  4.) Rope         ||
||  5.) Miss Scarlett    ||  5.) Lead piping  ||
||  6.) Mrs. White       ||  6.) Spanner      ||
================================================
"""
room_table = """  
=========================
||........Rooms........||
||  1.) Hall           ||
||  2.) Lounge         ||
||  3.) Library        ||
||  4.) Kitchen        ||
||  5.) Billiard Room  ||
||  6.) Study          ||
=========================
"""
suggestion = '''
--------------
| Killer: {} |
| Weapon: {} |
| Place : {} |
-------------- 
'''
cards = [["Colonel Mustard", "Professor Plum", "Reverend Green", "Mrs. Peacock", "Mrs. White", "Miss Scarlett"],
         ["Dagger", "Candlestick", "Revolver", "Rope", "Lead piping", "Spanner"], ["Hall", "Study",
                                                                                   "Billiard Room", "Lounge", "Library",
                                                                                   "Kitchen"]]
suspects = {1: "Colonel Mustard", 2: "Professor Plum", 3: "Reverend Green", 4: "Mrs. Peacock", 5: "Miss Scarlett",
            6: "Mrs. White"}
weapon = {1: "Dagger", 2: "Candlestick", 3: "Revolver", 4: "Rope", 5: "Lead piping", 6: "Spanner"}
rooms = {1: "Hall", 2: "Lounge", 3: "Library", 4: "Kitchen", 5: "Billiard Room", 6: "Study"}

print("________________Setting up the Game Server__________________")
server_type = input("Choose the type of server...\n1.)Offline Server\n2.)Online Server\n")
if server_type == "1":
    server_type = "127.0.0.1"  # .................................................................Local host IP address.
elif server_type == "2":
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.connect(("8.8.8.8", 80))  # ..................................Using Google DNS -To get your IPV4 Address.
        server_type = server.getsockname()[0]
        print(f"Players can connect using: {server_type} address.")
        server.close()
    except Exception as online_error:
        print(f"{online_error}: Check your internet connection.")
        sys.exit(1)
else:
    print("Invalid option !")
    sys.exit(1)

n_players = int(input("Enter the number of players (2-6)\n(Least 3 players are recommended)\n"))
if type(n_players) == int and 6 >= n_players >= 2:
    print("Waiting for players to join....")
else:
    print("Invalid character entered.")
    sys.exit(1)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((server_type, 55555))
server.listen(n_players)


def send_all(message, ex_id=""):
    """ Sends message to all players in the game. """
    for player in players:
        if player == ex_id:
            continue
        player.send(message.encode("utf-8"))


def dice_s():
    """ Dice simulator. """
    return random.randint(1, 6)


def shuffle_cards(t_cards, num_players, players_nicknames):
    """ Shuffle cards and distribute among players.
    Returns two dictionaries: 1.) nickname-their cards 2.) Murder Envelope cards. """
    x = 0
    y = int(15 / num_players)
    count = y
    excess_cards = 15 % num_players
    temp_decs = []
    p_cards = []
    params = ["Killer", "Weapon", "Place"]  # .................................... Keys to access Murder Envelope cards.
    for i in range(0, 3):
        random.shuffle(t_cards[i])
        secret_deck.update({params[i]: t_cards[i][i]})
    for i in range(0, 3):
        t_cards[i].remove(secret_deck[params[i]])
        p_cards.extend(t_cards[i])
    random.shuffle(p_cards)
    for i in range(0, num_players):
        dec = p_cards[x:count]
        temp_decs.append(dec)
        x = count
        count += y
    count = 15 - excess_cards
    if excess_cards != 0:
        for i in range(1, excess_cards + 1):
            temp_decs[i].append(p_cards[count + i - 1])
    decks = {}
    for i in range(0, num_players):
        decks.update({players_nicknames[i]: temp_decs[i]})
    print(decks, "\n", secret_deck)
    return decks, secret_deck


def player_nickname(player):
    """ Ask newly joined players to choose and nickname and checks if there is no same name collision."""

    player.send("Please choose a nickname: ".encode("utf-8"))
    nickname = player.recv(1024).decode("utf-8")
    while True:
        if re.fullmatch(valid_name_pattern, nickname):
            break
        else:
            player.send('Invalid character used !'.encode("utf-8"))
            player.send("Choose a valid nickname: ".encode("utf-8"))
            nickname = player.recv(1024).decode("utf-8")
    while nickname in nicknames:
        player.send("This name is not available!\nPlease choose another nickname: ".encode("utf-8"))
        nickname = player.recv(1024).decode("utf-8")
    nicknames.append(nickname)
    members.update({nickname: player})
    player_point.update({nickname: 0})
    return nickname


def accept_requests():
    """Accepts new connection until selected number of people join."""
    global players_deck, secret_deck
    while len(players) < n_players:
        send_all("Waiting for other players to join...")
        player, address = server.accept()
        players.append(player)
        player.send("Hey there!\n".encode("utf-8"))
        nickname = player_nickname(player)
        send_all(f"{nickname} has joined the Game.\n")
    players_deck, secret_deck = shuffle_cards(cards, n_players, nicknames)
    time.sleep(2)
    send_all("\nShuffling Cards...")
    time.sleep(2)
    send_all("...")
    time.sleep(2)
    send_all("...")
    time.sleep(2)
    send_all(game_art1)
    time.sleep(2)
    send_all(game_art2)
    time.sleep(2)
    send_all(game_art3)
    time.sleep(2)
    nicknames.sort()
    main_game()
    return None


def player_turn(nickname):
    """Ask the given player to roll dice and enter in room to make suggestion if applicable.
    returns True only when player wins."""
    player_id = members[nickname]
    temp_win = True
    player_id.send("---------------------------------------------------\n".encode("utf-8"))
    player_id.send("Hit 'y' to Roll Dice..".encode("utf-8"))
    player_id.recv(1024).decode("utf-8")
    dice_count = dice_s()
    player_id.send("\n=============================================".encode("utf-8"))
    player_id.send(f"You have rolled: {dice_count}.".encode("utf-8"))
    send_all(f"{nickname} rolled: {dice_count}", ex_id=player_id)
    player_point[nickname] += dice_count
    if player_point[nickname] >= 8:
        player_id.send("\nWant to enter in a room ? (y/n)".encode("utf-8"))
        choice = player_id.recv(1024).decode("utf-8")
        if choice == 'y':
            player_point[nickname] = 0
            player_id.send(room_table.encode("utf-8"))
            player_id.send("\nChoose a room to enter: ".encode("utf-8"))
            room_no = 0
            while room_no > 6 or room_no < 1 or type(room_no) != int:  # .......... To check if entered option is valid.
                try:
                    room_no = int(player_id.recv(1024).decode("utf-8"))
                except Exception as e:
                    player_id.send("Invalid room selected!\n".encode("utf-8"))
                    print(f"Invalid Character Entered by user: {e}")
                    room_no = 0
            player_id.send("\nChoose Suspect and Weapon. (separated by space)".encode("utf-8"))
            time.sleep(0.5)
            player_id.send(option_table.encode("utf-8"))
            sus_wea = [0, 0]
            while sus_wea[0] > 6 or sus_wea[0] < 1 or type(sus_wea[0]) != int or len(sus_wea) != 2:
                # ..................................................................To check if entered option is valid.
                try:
                    sus_wea = list(map(int, player_id.recv(1024).decode("utf-8").split(" ")))
                except Exception as er:
                    print(f"Invalid Character Entered: {er}")
                    player_id.send("Invalid Character selected!".encode("utf-8"))
                    sus_wea = [0, 0]
            while sus_wea[1] > 6 or sus_wea[1] < 1 or type(sus_wea[1]) != int or len(sus_wea) != 2:
                # ..................................................................To check if entered option is valid.
                try:
                    sus_wea = list(map(int, player_id.recv(1024).decode("utf-8").split(" ")))
                except Exception as er:
                    print(f"Invalid Weapon Entered: {er}")
                    player_id.send("Invalid Character selected!".encode("utf-8"))
                    sus_wea = [0, 0]
            send_all(f"\n{nickname}'s suggestion:")
            send_all(suggestion.format((suspects[sus_wea[0]]), weapon[sus_wea[1]], rooms[room_no]))
            accused = [suspects[sus_wea[0]], weapon[sus_wea[1]], rooms[room_no]]
            time.sleep(2)
            for name in nicknames:
                for accuse in accused:
                    if accuse in players_deck[name] and name != nickname:
                        send_all(f"{name} has disapproved {nickname}'s suggestion.", player_id)
                        player_id.send(f"{name} has {accuse}.".encode("utf-8"))
                        temp_win = False
                        break
                if not temp_win:
                    break
            if temp_win:
                send_all(f"No proof against {nickname}'s suggestion.")
            player_id.send("Do you want to revel cards ?(y/n)".encode("utf-8"))
            choice_r = player_id.recv(1024).decode("utf-8")
            if choice_r == 'y':
                if secret_deck["Killer"] == suspects[sus_wea[0]] and secret_deck["Weapon"] == weapon[sus_wea[1]] and \
                        secret_deck["Place"] == rooms[room_no]:
                    send_all(f"{nickname} WON !")
                    player_id.send(f"\nCongrats {nickname} you have solved the case !".encode("utf-8"))
                    return True
                else:
                    send_all(f"Wrong accusation !\n{nickname} will no longer make accusations.")
                    nicknames.remove(nickname)
            else:
                pass
        else:
            pass
    return False


def show_player_detail():
    """Display each player their cards and points."""
    for name in nicknames:
        player_id = members[name]
        point = player_point[name]
        deck = players_deck[name]
        player_id.send("\n=============================================\n".encode("utf-8"))
        player_id.send(f"Your Cards: {deck}\nYour points: {point}\n\n".encode("utf-8"))


def main_game():
    """Passes player name to 'player_turn' function turn-by-turn until one player wins."""
    iter_nickname = itertools.cycle(nicknames)
    nickname = next(iter_nickname)
    win = False
    while not win:
        time.sleep(1)
        show_player_detail()
        time.sleep(1)
        win = player_turn(nickname)
        nickname = next(iter_nickname)
    send_all("\nThanks for playing.\nAnd now we present you the finale of the game according to the characters you have:"
             "\nMiss Scarlet: Once miss Scarlet is discovered for the murder of Professor Plum, she escapes across the people and manages"
             "to escape, near the mannor there is a cliff and she commits suicide.\nColonel Mustard: After the events that ocurred during"
             "the night, it was discovered that the Colonel Mustard is the actual killer, while the debate about the Colonel´s fate is happening,"
             "Ms. White comes from behind and takes a headshot with the revolver, the homicide weapon..."
             "\nMs. White: By being discovered for the murder of Miss Scarlet who was killed with the lead piping that was under the sink in the kitchen,"
             " Ms. White´s fate was decided to be delivered to the authorities, while everybody was waiting for their arrival, Ms. White gets a heart attack"
             "giving the murder and the victim full circle...\nReverend Green: After a long and rainy night at the mannor, we reached to the conlusion that the "
             "homicide of Ms. Peacock was made by Reverend Green ´cause he decided to scrag her due to her secret confession, she said that she hid her family´s fortune"
             "in the mannor´s catacombs,when Reverend Green heard this, he entered into a frenzy state and acted the worst way posible, now that he got discovered "
             "and captured by evereyone else, he´ll be handed over to the authorities and proceed with his sentence.\nMs. Peacock: Befeore the whole investigation"
             "took place, there was a debate between Ms. Peacock and Prof. Plum, he will take all of her families fortune due to this fact she killed him with the "
             "candlestick in the study room leaving the body without life, ´cause if the fortune could belong to her, she would´nt allow to someone else to take it,"
             "I´d rather die before being poor!-she said. At the end of the night the terrible acts of the twisted lady were discovered and she´ll be prosecuted"
             "according to the law, reaching full circle to this story of mystery.\nProf. Plum: In the murder´s afternoon, Prof. Plum & Ms. Peacock were chatting "
             "as normal as posible, what the lady didn´t know, it was the dark intentions from the Prof. at a certain point in the conversation, Ms. Peacock got "
             "distracted leaving her most precious jewels at a sight, this provoked that the shameless Prof. took the chance to grab them all due to money problems"
             "so he can continue his investigations, far away from him, Ms. White saw the act, so she decided to face the Prof. but he decided to cut her throat open"
             "and leave her bleed out so he can manage to escape. In that night, he got discovered due to the fact that his footprints were found and since never"
             "washed his shoes, he got captured and handed over to the police so he can receive his sentence.")
    try:
        members.get(nickname).recv(1024).decode("utf-8")
    except Exception as e:
        print(e)
    server.close()


accept_requests()
