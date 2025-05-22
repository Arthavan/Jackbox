import flet as ft
from helper import *
from flet_audio import Audio


# Load audio files
bruh = Audio(src="data/amongus.mp3", autoplay=False, volume=0.5)
background_music = Audio(src="data/background.mp3", autoplay=False, volume=VOLUME)


# Container for audio controls
audio_container = ft.Container()
def add(page: ft.Page):
    audio_container_row = ft.Row()

    audio_container_row.controls.append(bruh)
    audio_container_row.controls.append(background_music)

    audio_container.content = audio_container_row
    page.overlay.append(audio_container)
    page.update()