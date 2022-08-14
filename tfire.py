import argparse
import curses
import random
import time

COLOR_DICT = {
    "white": [255, 252, 250, 248, 246, 244, 242, 240, 238, 237],
    "red": [196, 196, 160, 160, 124, 124, 88, 88, 52, 52],
    "green": [46, 40, 40, 34, 34, 28, 28, 22, 22, 22],
    "blue": [21, 20, 20, 19, 19, 18, 18, 17, 17, 17],
    "yellow": [190, 154, 154, 148, 148, 148, 58, 58, 58, 58],
    "magenta": [164, 164, 127, 127, 127, 90, 90, 90, 53, 53],
    "cyan": [39, 38, 38, 38, 37, 37, 30, 30, 23, 23],
}
STANDARD_COLOR_DICT = {
    "white": curses.COLOR_WHITE, "red": curses.COLOR_RED,
    "green": curses.COLOR_GREEN, "blue": curses.COLOR_BLUE,
    "yellow": curses.COLOR_YELLOW, "magenta": curses.COLOR_MAGENTA,
    "cyan": curses.COLOR_CYAN
}
COLOR_NAMES = ["red", "green", "blue", "cyan", "magenta", "yellow", "white"]


class Cell:
    def __init__(self, screen, start_x: int, height: int):
        self.screen = screen
        self.y = height - 1
        self.x = start_x
        self.height = height
        self.max_height = random.randint(height - 16, height - 4)
        self.char = "X"
        self.brightness = 1
        self.max_height -= random.choice([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 8])

    def process(self) -> bool:
        # return True - remove, False - do not remove
        if self.y <= self.max_height:
            return True
        if self.y <= self.height - 4 and self.brightness < 10:
            self.brightness += 1
        self.y -= 1
        self.screen.addstr(
            self.y,
            self.x,
            self.char,
            curses.color_pair(self.brightness))
        return False


def next_color(current_color: str) -> str:
    index = COLOR_NAMES.index(current_color)
    if index >= len(COLOR_NAMES) - 1:
        index = 0
    else:
        index += 1
    return COLOR_NAMES[index]


def set_color(color: str) -> None:
    if curses.COLORS < 255:
        for i in range(len(COLOR_DICT[color])):
            curses.init_pair(i + 1,
                             STANDARD_COLOR_DICT[color],
                             curses.COLOR_BLACK)
    else:
        for i, c in enumerate(COLOR_DICT[color]):
            curses.init_pair(i + 1, c, curses.COLOR_BLACK)


def curses_main(screen, args: argparse.Namespace):
    curses.curs_set(0)  # Set the cursor to off.
    screen.timeout(0)  # Turn blocking off for screen.getch().
    height = curses.LINES
    width = curses.COLS
    set_color(args.color)
    cell_list = []

    run = True
    while run:
        screen.erase()
        remove_list = []
        for cell in cell_list:
            if cell.process():
                remove_list.append(cell)
        screen.refresh()
        for cell in remove_list:
            cell_list.remove(cell)
        new = [Cell(screen, x + 1, height) for x in range(width - 2)]
        cell_list.extend(new)
        ch = screen.getch()
        if ch in [81, 113]:  # q, Q
            run = False
        elif ch == 99:  # c
            args.color = next_color(args.color)
            set_color(args.color)
        time.sleep(0.02)


def argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--color", default="white",
                        help="Set the color.")
    return parser.parse_args()


def main():
    args = argument_parser()
    curses.wrapper(curses_main, args)


if __name__ == "__main__":
    main()
