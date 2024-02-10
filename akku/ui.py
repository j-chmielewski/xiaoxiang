import curses
from akku.bms import BmsData


class Gui:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.initscr()
        curses.start_color()
        self._init_colors()

    def update(self, data: BmsData):
        self.stdscr.clear()
        capacity = f'Capacity: {data.capacity}%'
        self.stdscr.addstr(0, 0, capacity, self._percent_color(data.capacity))
        power = data.current * data.voltage
        color = self._power_color(power)
        power = f'Power: {power:.0f}W ({data.voltage:.2f}V * {data.current:.2f}A)'
        self.stdscr.addstr(1, 0, power, color)
        self.stdscr.refresh()

    @staticmethod
    def _init_colors():
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    @staticmethod
    def _percent_color(percent: int):
        if percent <= 33:
            return curses.color_pair(1)
        elif percent <= 66:
            return curses.color_pair(2)
        else:
            return curses.color_pair(3)

    @staticmethod
    def _power_color(power: float):
        if power < 0:
            return curses.color_pair(1)
        elif power < 50:
            return curses.color_pair(2)
        else:
            return curses.color_pair(3)


# def main(stdscr):
#     curses.initscr()
#     curses.start_color()
#     init_colors()
#     while True:
#         stdscr.clear()
#         # bars
#         data = benedict(get_data(sys.argv[1]))
#         bars = data[BARS_PATH]
#         bars_str = f'[{BARS[data[BARS_PATH]]}]'
#         stdscr.addstr(0, 0, bars_str, bars_color(bars))

#         # network
#         network = current_network(data[SCANLIST_PATH])
#         stdscr.addstr(0, 8, network)

#         # connection type
#         connection = data[CONNECTION_PATH]
#         stdscr.addstr(0, 9 + len(network), f'({connection})')

#         # signal
#         for i, (k, v) in enumerate(METRICS.items()):
#             percent = metric_percent(k, data[v])
#             color = percent_color(percent)
#             value = f'{k}: {data[v]}'
#             stdscr.addstr(i+1, 0, value, color)
#             percent = metric_percent(k, data[v])
#             stdscr.addstr(i+1, len(value) + 1, f'({percent}%)', color)
#         stdscr.refresh()
#         time.sleep(1)

# if __name__ == '__main__':
#     curses.wrapper(main)
