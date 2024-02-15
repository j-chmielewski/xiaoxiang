import argparse
import asyncio
import curses
from bms import Bms
from ui import Gui


async def run_gui(stdscr, address, capacity):
    bms = Bms(address, capacity)
    gui = Gui(stdscr)
    async for data in bms.read():
        gui.update(data)


def main(stdscr, address, capacity):
    asyncio.run(run_gui(stdscr, address, capacity))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('address', type=str, help="BMS Bluetooth address")
    parser.add_argument('-c', '--capacity', type=int, default=200, help="Total battery capacity")
    args = parser.parse_args()

    curses.wrapper(main, args.address, args.capacity)

