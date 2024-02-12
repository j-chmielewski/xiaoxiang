import asyncio
import curses
from bms import Bms
from ui import Gui

# TODO: argparse
ADDRESS = "A4:C1:37:30:8D:90"
CAPACITY_AH = 200

async def run_gui(stdscr, address, capacity):
    bms = Bms(address, capacity)
    gui = Gui(stdscr)
    async for data in bms.read():
        gui.update(data)

def main(stdscr, address, capacity):
    asyncio.run(run_gui(stdscr, address, capacity))

if __name__ == '__main__':
    curses.wrapper(main, ADDRESS, CAPACITY_AH)

