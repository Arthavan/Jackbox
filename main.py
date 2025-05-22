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
from menu import *










def main(page: ft.Page):
    page.title = "Flet Chat"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    add(page)


    #Create Random Player
    player_initial_name = f"Player{random.randint(100, 999)}"
    player = Player(name=player_initial_name, page=page)
    page.session.set("player_name", player_initial_name)


    # Create a TextField popup for the player to enter their name
    player_name_flet = ft.TextField(page.session.get("player_name"), read_only=True, width=200, border=ft.InputBorder.NONE)

    def submit_name(e):
        name = player_name_flet.value.strip()
        if name and name not in rooms:
            page.session.set("player_name", name)
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
        
    volume_slider = ft.Slider(min=0, max=1, divisions=10, label="{value}%", value=0.5, width=300)

    def on_volume_change(e):
        VOLUME = volume_slider.value
        background_music.volume = VOLUME
        #print("Volume changed to: ", VOLUME)
        background_music.update()

    volume_slider.on_change = on_volume_change

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
    
    main_menu(page)
    page.update()



if __name__ == "__main__":
    #ft.app(target=main, view=ft.WEB_BROWSER)
    ft.app(target=main)











