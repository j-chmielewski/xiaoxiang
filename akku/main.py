import asyncio
import curses
from akku.bms import Bms
from akku.ui import Gui


ADDRESS = "A4:C1:37:30:8D:90"

async def run_gui(stdscr, address):
    bms = Bms(address)
    gui = Gui(stdscr)
    async for data in bms.read():
        gui.update(data)


def main(stdscr, address):
    asyncio.run(run_gui(stdscr, address))


if __name__ == '__main__':
    curses.wrapper(main, ADDRESS)

