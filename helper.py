import string, random, time, threading, os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Callable
import flet as ft
import asyncio

# Game constants
MIN_PLAYERS = 0
MAX_PLAYERS = 8
ROOM_CODE_LENGTH = 4
COUNTDOWN_SECONDS = 5
VOTING_TIME = 30
RESULT_DISPLAY_TIME = 10
ROUNDS_PER_GAME = 3
MAIN_COLOR = ft.Colors.DEEP_ORANGE_ACCENT
VOLUME = 0.5


@dataclass
class Player:
    name: str
    page: ft.Page
    is_host: bool = False
    score: int = 0
    is_faker: bool = False
    current_prompt: str = ""
    has_voted: bool = False
    vote: Optional[str] = None

@dataclass
class GameRoom:
    code: str
    players: Dict[str, Player] = field(default_factory=dict)
    host: Optional[str] = None
    game_state: str = "lobby"  # lobby, prompt, voting, results, game_over
    faker: Optional[str] = None
    round_number: int = 0
    current_category: str = ""
    current_prompt: str = ""
    faker_prompt: str = ""
    votes: Dict[str, str] = field(default_factory=dict)
    round_start_time: float = 0
    used_prompts: Set[str] = field(default_factory=set)


rooms: Dict[str, GameRoom] = {}

def generate_room_code() -> str:
    """Generate a unique room code."""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=ROOM_CODE_LENGTH))
        if code not in rooms:
            return code
        


async def countdown(countdown_text: ft.Text, page: ft.Page):
    for i in range(5, 0, -1):
        countdown_text.value = f"Starting in {i}"
        page.update()
        await asyncio.sleep(1)
    countdown_text.value = "Go!"
    page.update()



def create_banner(text: str, page: ft.Page):
    def close_banner(e):
        page.close(b)


    b = ft.Banner(
        bgcolor=ft.Colors.AMBER_100,
        leading=ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER, size=40),
        content=ft.Text(
            value=text,
            color=ft.Colors.BLACK,
        ),
        actions=[
            ft.TextButton(text="Close", style=ft.ButtonStyle(color=ft.Colors.BLUE), on_click=close_banner)
        ],
    )


    page.add(b)
    page.open(b)
    page.update()
    time.sleep(3)  # Keep the banner open for 5 seconds
    page.close(b)
    page.update()