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
from audio import *



# ----- Main Menu ----
def main_menu(page: ft.Page):
    page.controls.clear()
    page.title = "Fakin' It Clone"
    page.theme_mode = "LIGHT"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER


    join_input = ft.TextField(label="Enter Room Code", width=200)

    def go_to_lobby(e):
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
        lobby(page)

    def join_room(e):
        code = join_input.value.upper()
        if code in rooms:
            page.session.set("room_code", code)
            page.session.set("is_host", False)
            lobby(page)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Room not found"))
            page.snack_bar.open = True
            page.update()

    def create_room(e):
        room_code = generate_room_code()
        rooms[room_code] = GameRoom(code=room_code)
        page.session.set("room_code", room_code)
        page.session.set("is_host", True)
        lobby(page)



    page.add(join_input, ft.ElevatedButton("Join Nuts Room", on_click=join_room))
    page.add(ft.ElevatedButton("Create Room", on_click=create_room))
    page.update()



# ----- Main Lobby ----
def lobby(page: ft.Page):
    page.controls.clear()
    page.title = "Lobby"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER


    room_code = page.session.get("room_code")
    player_name = page.session.get("player_name")
    is_host = page.session.get("is_host")

    if room_code not in rooms:
        main_menu(page)
        return

    room = rooms[room_code]

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
            player.page.go("/game")

    page.add(ft.Text(f"Room Code: {room.code}"))
    page.add(ft.Text(f"Players: {', '.join(room.players.keys())}"))
    if is_host:
        page.add(ft.ElevatedButton("Start Game", on_click=start_game))
    page.add(ft.ElevatedButton("Leave Room", on_click=lambda e: main_menu(page)))
    page.update()