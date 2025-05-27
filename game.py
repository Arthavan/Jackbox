from helper import *
from audio import *
#from menu import *

#Functions










''''# Countdown before starting the game
async def main(page: ft.Page):
    countdown_text = ft.Text("Starting in 5", size=40)
    page.add(countdown_text)

    async def countdown():
        for i in range(5, 0, -1):
            countdown_text.value = f"Starting in {i}"
            page.update()
            await asyncio.sleep(1)
        countdown_text.value = "Go!"
        page.update()

    await countdown()

ft.app(target=main)
'''