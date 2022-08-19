import argparse
import curses
import random
import time

COLOR_DICT = {
    "white": [255, 252, 250, 248, 246, 244, 242, 240, 238, 237],
    "red": [196, 196, 160, 160, 124, 124, 88, 88, 52, 52],
    "green": [46, 40, 40, 34, 34, 28, 28, 22, 22, 22],
    "blue": [21, 20, 20, 19, 19, 18, 18, 17, 17, 17],
    "yellow": [154, 190, 190, 148, 149, 101, 58, 58, 58, 58],
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
SPEED_LIST = [0.006, 0.007, 0.008, 0.009, 0.01, 0.02, 0.03, 0.05, 0.08, 0.1]
DEFAULT_SPEED = 5
MIN_HEIGHT = 16


class TFireError(Exception):
    pass


class Cell:
    def __init__(self, screen, start_x: int, height: int):
        self.screen = screen
        self.y = height - 1
        self.x = start_x
        self.height = height
        self.max_height = random.choices(
            [(height - x) for x in range(2, 15)],
            [5, 10, 25, 7, 10, 12, 9, 20, 12, 10, 5, 2, 4]
        )[0]
        self.char = "X"
        self.base_char = "#"
        self.brightness = 1

    def process(self) -> bool:
        # return True - remove, False - do not remove
        if self.y <= self.max_height:
            return True
        if self.y <= self.height - 4 and self.brightness < 10:
            self.brightness += 1
        self.y -= 1
        if self.y <= self.height - 3:
            char = self.char
        else:
            char = self.base_char
        self.screen.addstr(
            self.y,
            self.x,
            char,
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
    if height <= MIN_HEIGHT:
        raise TFireError("Screen height is too short.")
    set_color(args.color)
    cell_list = []
    speed = SPEED_LIST[args.speed]

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
        if ch == curses.KEY_RESIZE:
            curses.update_lines_cols()
            height = curses.LINES
            if height <= MIN_HEIGHT:
                raise TFireError("Error screen/window height is too short.")
            if curses.COLS < width:
                cell_list.clear()
            width = curses.COLS
        if ch != -1 and args.screensaver:
            run = False
        elif ch in [81, 113]:  # q, Q
            run = False
        elif ch == 99:  # c
            args.color = next_color(args.color)
            set_color(args.color)
        elif 48 <= ch <= 57:  # number keys 0 to 9
            speed = SPEED_LIST[int(chr(ch))]
        time.sleep(speed)


def positive_int_zero_to_nine(value: str) -> int:
    """
    Used with argparse.
    Checks to see if value is positive int between 0 and 10.
    """
    msg = f"{value} is an invalid positive int value 0 to 9"
    try:
        int_value = int(value)
        if int_value < 0 or int_value >= 10:
            raise argparse.ArgumentTypeError(msg)
        return int_value
    except ValueError:
        raise argparse.ArgumentTypeError(msg)


def argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--color", default="white",
                        help="Set the color.")
    parser.add_argument("-s", "--speed",
                        default=DEFAULT_SPEED,
                        type=positive_int_zero_to_nine,
                        help="Set the speed (delay) 0-Fast, 5-Default,"
                             " 9-Slow")
    parser.add_argument("--screensaver", action="store_true",
                        help="Screensaver mode. Any key will exit.")
    return parser.parse_args()


def main():
    args = argument_parser()
    try:
        curses.wrapper(curses_main, args)
    except TFireError as e:
        print(e)


if __name__ == "__main__":
    main()
