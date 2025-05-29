# Fakin it parody from jackbox!

#imports
import flet as ft
import asyncio
import random
import string
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Callable
import threading
# My Helper Libraries
from helper import * 
#from audio import *
from flet_audio import Audio

#Audio
background_music = Audio(src="data/background.mp3", autoplay=False, volume=VOLUME)
bruh = Audio(src="data/amongus.mp3", autoplay=False, volume=0.5)

def appbar(page: ft.Page):
    player_name_flet = ft.TextField(page.client_storage.get("player_name"), read_only=True, width=200, border=ft.InputBorder.NONE)
    
    def submit_name(e):
        name = player_name_flet.value.strip()
        if name and name not in rooms:
            page.client_storage.set("player_name", name)
            player_name_flet.read_only = True
            player_name_flet.border = ft.InputBorder.NONE
            player_name_flet.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Name cannot be blank or already taken!"))
            page.snack_bar.open = True
            page.update()

    def change_name(e):
        player_name_flet.read_only = False
        player_name_flet.border = ft.InputBorder.OUTLINE
        player_name_flet.focus()
        player_name_flet.on_submit = lambda e: submit_name(e)
        player_name_flet.update()

    def toggle_theme():
        page.theme_mode = "DARK" if page.theme_mode == "LIGHT" else "LIGHT"
        page.update()

    def change_main_color(color):
        global MAIN_COLOR
        if color == "Red":
            MAIN_COLOR = ft.Colors.RED
        elif color == "Green":
            MAIN_COLOR = ft.Colors.GREEN
        elif color == "Blue":
            MAIN_COLOR = ft.Colors.BLUE
        #print("color: ", color, type(color))
        page.appbar.bgcolor = MAIN_COLOR
        page.update()
        
    def on_volume_change(e):
        VOLUME = volume_slider.value
        background_music.volume = VOLUME
        #print("Volume changed to: ", VOLUME)
        background_music.update()

    volume_slider = ft.Slider(min=0, max=1, divisions=10, label="{value}%", value=0.5, width=300, on_change=on_volume_change)


    page.appbar = ft.AppBar(
        leading=ft.Row([ft.IconButton(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, on_click=change_name, hover_color=ft.Colors.AMBER), player_name_flet]),
        title=ft.Text("Not-Jackbox Jackbox"),
        center_title=True,
        bgcolor=MAIN_COLOR,
        actions=[ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="Red", icon=ft.Icons.PALETTE, data="Red", on_click=lambda e: change_main_color("Red")),
                    ft.PopupMenuItem(text="Green", icon=ft.Icons.PALETTE, data="Green", on_click=lambda e: change_main_color("Green")),
                    ft.PopupMenuItem(text="Blue", icon=ft.Icons.PALETTE, data="Blue", on_click=lambda e: change_main_color("Blue")),
                ]),
                ft.IconButton(ft.Icons.MUSIC_NOTE, tooltip="Volume", on_click=lambda e: background_music.play()),
                volume_slider,
            ft.IconButton(
            icon=ft.icons.LIGHT_MODE if page.theme_mode == "LIGHT" else ft.Icons.DARK_MODE,
            tooltip="Toggle Theme",
            on_click=lambda e: toggle_theme()),
            ft.IconButton(ft.Icons.HELP, tooltip="Settings", on_click=lambda e: bruh.play()),
            background_music])
    page.update()


def main(page: ft.Page):
    page.title = "Flet Chat"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.overlay.append(background_music)
    #Player
    if page.client_storage.contains_key("player_name"):
        player_initial_name = page.session.get("player_name")
    else:
        player_initial_name = f"Player{random.randint(100, 999)}"
        player = Player(name=player_initial_name, page=page)
        page.client_storage.set("player_name", player_initial_name)


    # Create a TextField popup for the player to enter their name
    appbar(page)


    page.update()
    main_menu(page)





# ----- Main Menu ----
def main_menu(page: ft.Page):
    page.controls.clear()
    print("Main Menu")
    page.title = "Fakin' It Clone"
    page.theme_mode = "LIGHT"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.overlay.append(background_music)
    appbar(page)

    join_input = ft.TextField(label="Enter Room Code", width=200)

    '''def go_to_lobby(e):
        room_code = generate_room_code()
        rooms[room_code] = {
            "players": [],
            "faker": None,
            "current_prompt": None,
            "state": "lobby"
        }
        page.session.set("room_code", room_code)
        page.session.set("is_host", True)
        rooms[room_code]["players"].append(page.session.get("player_name"))
        lobby(page)'''

    def join_room(e):
        code = join_input.value.upper()
        if code in rooms:
            page.client_storage.set("room_code", code)
            page.client_storage.set("is_host", False)
            page.pubsub.send_all_on_topic("PlayerJoined", [page.client_storage.get("player_name"), page])
            lobby(page)
        else:
            create_banner("Room Not Found", page)
            

    def create_room(e):
        room_code = generate_room_code()
        rooms[room_code] = GameRoom(code=room_code)
        page.client_storage.set("room_code", room_code)
        page.client_storage.set("is_host", True)
        lobby(page)



    page.add(join_input, ft.ElevatedButton("Join Nuts Room", on_click=join_room))
    page.add(ft.ElevatedButton("Create Room", on_click=create_room))
    page.update()



# ----- Main Lobby ----
def lobby(page: ft.Page):
    page.controls.clear()
    page.title = "Lobby"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER


    room_code = page.client_storage.get("room_code")
    player_name = page.client_storage.get("player_name")
    is_host = page.client_storage.get("is_host")

    if room_code not in rooms:
        main_menu(page)
        return

    room = rooms[room_code]
    room.players[player_name] = Player(name=player_name, page=page, is_host=is_host)




    def start_game(e):
        if len(room.players) < MIN_PLAYERS:
            page.snack_bar = ft.SnackBar(ft.Text(f"Minimum {MIN_PLAYERS} players required to start the game."))
            page.snack_bar.open = True
            page.update()
            return

        # Start the game
        room.game_state = "prompt"
        room.round_number = 1
        room.current_category = "Category 1"  # Placeholder for category
        room.current_prompt = "Prompt 1"  # Placeholder for prompt
        room.faker_prompt = "Faker Prompt"  # Placeholder for faker prompt
        room.faker = random.choice(list(room.players.keys()))
        for player in room.players.values():
            player.is_faker = (player.name == room.faker)
            player.has_voted = False
            player.vote = None

        # Notify all players to start the game
        for player in room.players.values():
            page.pubsub.send_others_on_topic("GameStarted", [player.name, player.page])
            player.page.go("/game")
        
        print(f"Game started in room {room_code} with faker: {room.faker}")
        asyncio.run(game(page))

    def leave_room(e):
        #print("Leaving room")
        if page.client_storage.get("is_host"):
            if room_code in rooms:
                del rooms[room_code]
                page.client_storage.remove("room_code")
                page.client_storage.remove("is_host")
                page.pubsub.send_all_on_topic("PlayerLeft", [player_name, page])
                page.controls.clear()
                main_menu(page)
        else:
            
            page.pubsub.send_all_on_topic("PlayerLeft", [player_name, page])
            page.client_storage.remove("room_code")
            page.client_storage.remove("is_host")
            main_menu(page)

    page.add(ft.Text(f"Room Code: {room.code}"))
    page.add(ft.Text(f"Players: {', '.join(room.players.keys())}"))
    if is_host:
        page.add(ft.ElevatedButton("Start Game", on_click=start_game))
    page.add(ft.ElevatedButton("Leave Room", on_click=leave_room))
    page.update()



    def on_player_joined(e, message):
        name, p = message
        if name == page.client_storage.get("player_name"):
            return
        #print("Player Joined")
        #print(room.players)
        page.controls.clear()
        room.players[name] = Player(name=name, page=p, is_host=False)
        page.add(ft.Text(f"Player {name} has joined the room."))
        page.add(ft.Text(f"Room Code: {room.code}"))
        page.add(ft.Text(f"Players: {', '.join(room.players.keys())}"))
        if is_host:
            page.add(ft.ElevatedButton("Start Game", on_click=start_game))
        page.add(ft.ElevatedButton("Leave Room", on_click=leave_room))
        page.update()

    def on_player_left(e, message):
        name, p = message
        if name in room.players and room.players[name].page != page:
            del room.players[name]
            print(f"Player {name} has left the room.")
            page.controls.clear()
            page.add(ft.Text(f"Player {name} has left the room."))
            page.add(ft.Text(f"Room Code: {room.code}"))
            page.add(ft.Text(f"Players: {', '.join(room.players.keys())}"))
            if is_host:
                page.add(ft.ElevatedButton("Start Game", on_click=start_game))
            page.add(ft.ElevatedButton("Leave Room", on_click=leave_room))
            page.update()

    page.pubsub.subscribe_topic("PlayerJoined", on_player_joined)
    page.pubsub.subscribe_topic("PlayerLeft", on_player_left)
    page.pubsub.subscribe_topic("GameStarted", lambda e, m: asyncio.run(game(page)) if m[0] == page.client_storage.get("player_name") else None)



async def game(page: ft.Page):
    room = rooms[page.client_storage.get("room_code")]
    print("Game started")
    page.controls.clear()
    # Countdown before starting the game
    countdown_text = ft.Text("Starting in 5", size=40)
    page.add(countdown_text)
    await countdown(countdown_text, page)
    await asyncio.sleep(1)  # Simulate countdown delay
    page.controls.clear()


    if page.client_storage.get("player_name") == room.faker:
        role_text = ft.Text(f"You are the Faker!", size=30)
    else:
        role_text = ft.Text(f"You are a normal chump!", size=30)

    page.add(role_text)



    page.title = "Flet Chat - Game"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    await asyncio.sleep(1)  # Simulate game start delay

    page.add(ft.Text(f"Round {room.round_number} - Category: {room.current_category}"))
    page.add(ft.Text(f"Prompt: {room.current_prompt}"))
    page.add(ft.Text(f"Faker Prompt: {room.faker_prompt}"))
    page.add(ft.Text(f"Faker: {room.faker}"))
    page.add(ft.Text(f"Players: {', '.join([p.name for p in room.players.values()])}"))
    page.add(ft.ElevatedButton("Vote", on_click=lambda e: vote(page)))
    page.update()

def vote(page: ft.Page):
    room = rooms[page.client_storage.get("room_code")]
    player_name = page.client_storage.get("player_name")
    player = room.players[player_name]

    if player.has_voted:
        page.snack_bar = ft.SnackBar(ft.Text("You have already voted!"))
        page.snack_bar.open = True
        page.update()
        return

    def submit_vote(e):
        vote = vote_input.value.strip()
        if vote:
            player.vote = vote
            player.has_voted = True
            room.votes[player_name] = vote
            page.snack_bar = ft.SnackBar(ft.Text(f"You voted for: {vote}"))
            page.snack_bar.open = True
            page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Vote cannot be empty!"))
            page.snack_bar.open = True
            page.update()

    vote_input = ft.TextField(label="Enter your vote", width=200, on_submit=submit_vote)
    page.add(vote_input)
    page.add(ft.ElevatedButton("Submit Vote", on_click=submit_vote))
    page.update()








# ----- Game Logic ----
if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
    #ft.app(target=main)




