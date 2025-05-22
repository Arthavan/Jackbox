import flet as ft
from helper import *


# Load audio files
bruh = ft.Audio(src="data/amongus.mp3", autoplay=False, volume=0.5)
background_music = ft.Audio(src="data/background.mp3", autoplay=False, volume=VOLUME)


# Container for audio controls
audio_container = ft.Container()
def add(page: ft.Page):
    audio_container_row = ft.Row()

    audio_container_row.controls.append(bruh)
    audio_container_row.controls.append(background_music)

    audio_container.content = audio_container_row
    page.overlay.append(audio_container)
    page.update()