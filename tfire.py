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
REAL_FIRE = [196, 166, 214, 190, 149, 58, 240, 238, 238, 237]
REAL_FIRE_STANDARD = [curses.COLOR_RED, curses.COLOR_YELLOW,
                      curses.COLOR_YELLOW, curses.COLOR_YELLOW,
                      curses.COLOR_YELLOW, curses.COLOR_WHITE,
                      curses.COLOR_WHITE, curses.COLOR_WHITE,
                      curses.COLOR_WHITE, curses.COLOR_WHITE]
STANDARD_COLOR_DICT = {
    "white": curses.COLOR_WHITE, "red": curses.COLOR_RED,
    "green": curses.COLOR_GREEN, "blue": curses.COLOR_BLUE,
    "yellow": curses.COLOR_YELLOW, "magenta": curses.COLOR_MAGENTA,
    "cyan": curses.COLOR_CYAN
}
COLOR_NAMES = ["red", "green", "blue", "cyan", "magenta", "yellow", "white"]
LEN_COLOR_NAME = len(COLOR_NAMES)
BG_COLORS = {"black": curses.COLOR_BLACK, "white": curses.COLOR_WHITE,
             "red": curses.COLOR_RED, "green": curses.COLOR_GREEN,
             "blue": curses.COLOR_BLUE, "yellow": curses.COLOR_YELLOW,
             "magenta": curses.COLOR_MAGENTA, "cyan": curses.COLOR_CYAN}
SPEED_LIST = [0.006, 0.007, 0.008, 0.009, 0.01, 0.02, 0.03, 0.05, 0.08, 0.1]
DEFAULT_SPEED = 5
MIN_HEIGHT = 18
FIRE_CHARACTER_LIST = ["X", "x", "O", "F", "0", ":", ".", "+", "|",
                       "@", "*", "#"]
DEFAULT_FIRE_CHARACTER = "X"
BASE_CHARACTER_LIST = ["#", "=", "@", "-", "+", "X", "W", "0", "M", "V", ""]
DEFAULT_BASE_CHARACTER = "#"


class TFireError(Exception):
    pass


class Cell:
    def __init__(self, screen, start_x: int, height: int,
                 multi: bool, fire_size: str, char: str, base_char: str,
                 quarter_width: int):
        self.multi = multi
        self.fire_size = fire_size
        self.screen = screen
        self.y = height - 1
        self.x = start_x
        self.height = height
        self.quarter_width = quarter_width
        if self.fire_size == "small":
            self.max_height = random.choices(
                [(height - x) for x in range(2, 10)],
                [5, 10, 25, 7, 10, 5, 2, 5]
            )[0]
        elif self.fire_size == "medium":
            self.max_height = random.choices(
                [(height - x) for x in range(2, 15)],
                [5, 10, 25, 7, 10, 12, 9, 20, 12, 10, 5, 2, 4]
            )[0]
        elif self.fire_size == "large":
            self.max_height = random.choices(
                [(height - x) for x in range(2, 20)],
                [5, 10, 25, 7, 10, 12, 9, 20, 12, 8, 10, 5, 4, 2, 4, 3, 1, 4]
            )[0]
        self.char = char
        self.base_char = base_char
        self.brightness = 1
        if multi:
            self.multi_color_offset = random.choice([0, 10, 20, 30, 40, 50, 60])

    def process(self, bold: bool, bold_all: bool) -> bool:
        # return True - remove, False - do not remove
        if self.y <= self.max_height:
            return True
        if self.y <= self.height - 4 and self.brightness < 10:
            if self.fire_size == "small" and self.brightness < 7:
                self.brightness += 2
            else:
                self.brightness += 1
        self.y -= 1
        char = self.char if self.y <= self.height - 3 else self.base_char
        if self.multi:
            color_number = self.multi_color_offset + self.brightness
        else:
            color_number = self.brightness
        if bold_all:
            bold = curses.A_BOLD
        elif bold:
            randint = random.randint(0, 5)
            bold = curses.A_BOLD if randint <= 1 else curses.A_NORMAL
        else:
            bold = curses.A_NORMAL
        self.screen.addstr(
            self.y,
            self.x,
            char,
            curses.color_pair(color_number) + bold)
        self.screen.addstr(
            self.y,
            self.x + self.quarter_width,
            char,
            curses.color_pair(color_number) + bold)
        self.screen.addstr(
            self.y,
            self.x + self.quarter_width * 2,
            char,
            curses.color_pair(color_number) + bold)
        self.screen.addstr(
            self.y,
            self.x + self.quarter_width * 3,
            char,
            curses.color_pair(color_number) + bold)
        return False


def next_color(current_color: str) -> str:
    index = COLOR_NAMES.index(current_color)
    index = 0 if index >= LEN_COLOR_NAME - 1 else index + 1
    return COLOR_NAMES[index]


def next_color_bg(current_color: str) -> str:
    color_list = list(BG_COLORS.keys())
    index = color_list.index(current_color)
    index = 0 if index >= len(color_list) - 1 else index + 1
    return color_list[index]


def set_color(color: str, back_ground_color) -> None:
    if curses.COLORS < 255:
        [curses.init_pair(i + 1, STANDARD_COLOR_DICT[color],
         BG_COLORS[back_ground_color]) for i in range(len(COLOR_DICT[color]))]

    else:
        [curses.init_pair(i + 1, c, BG_COLORS[back_ground_color])
         for i, c in enumerate(COLOR_DICT[color])]


def setup_colors(back_ground_color: str):
    if curses.COLORS < 255:
        offset = 0
        for color in COLOR_NAMES:
            [curses.init_pair(offset + i + 1, STANDARD_COLOR_DICT[color],
                              BG_COLORS[back_ground_color])
             for i in range(len(COLOR_DICT[color]))]

            offset += 10
    else:
        offset = 0
        for color in COLOR_NAMES:
            [curses.init_pair(offset + i + 1, c, BG_COLORS[back_ground_color])
             for i, c in enumerate(COLOR_DICT[color])]

            offset += 10


def setup_real_fire_colors(back_ground_color: str):
    if curses.COLORS < 255:
        [curses.init_pair(i + 1, c, BG_COLORS[back_ground_color])
         for i, c in enumerate(REAL_FIRE_STANDARD)]
    else:
        [curses.init_pair(i + 1, c, BG_COLORS[back_ground_color])
         for i, c in enumerate(REAL_FIRE)]


def curses_main(screen, args: argparse.Namespace):
    curses.curs_set(0)  # Set the cursor to off.
    screen.timeout(0)  # Turn blocking off for screen.getch().
    height = curses.LINES
    width = curses.COLS
    quarter_width = (width - 1) // 4
    if height <= MIN_HEIGHT:
        raise TFireError("Screen height is too short.")
    if args.multi:
        setup_colors(args.background)
    else:
        set_color(args.color, args.background)
    screen.bkgd(curses.color_pair(1))
    speed = SPEED_LIST[args.speed]
    if args.real:
        setup_real_fire_colors(args.background)
    cell_list = []
    run = True
    while run:
        screen.erase()
        remove_list = []
        for cell in cell_list:
            if cell.process(args.bold, args.bold_all):
                remove_list.append(cell)
        screen.refresh()
        [cell_list.remove(cell) for cell in remove_list]
        new = [Cell(screen, x + 1,
                    height, args.multi, args.fire, args.char,
                    args.base, quarter_width) for x in range(quarter_width)]
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
            quarter_width = (width - 1) // 4
        time.sleep(speed)
        if ch == -1:  # if no key is press continue the loop
            continue
        if ch != -1 and args.screensaver:
            run = False
        elif ch in [81, 113]:  # q, Q
            run = False
        elif ch == 109:  # m
            if args.multi:
                set_color(args.color, args.background)
                args.multi = False
            else:
                setup_colors(args.background)
                args.multi = True
                args.real = False
        elif ch == 99:  # c
            args.multi = False
            args.real = False
            args.color = next_color(args.color)
            set_color(args.color, args.background)
        elif ch == 67:  # C
            args.background = next_color_bg(args.background)
            if args.multi:
                setup_colors(args.background)
            else:
                set_color(args.color, args.background)
        elif ch == 102:  # f   set size of the fire
            if args.fire == "small":
                args.fire = "medium"
            elif args.fire == "medium":
                args.fire = "large"
            else:
                args.fire = "small"
        elif ch == 98:  # b
            args.bold = not args.bold
        elif ch == 66:  # B
            args.bold_all = not args.bold_all
        elif ch == 114:  # r  toggle real fire
            if args.real:
                set_color(args.color, args.background)
                args.real = False
            else:
                args.real = True
                args.multi = False
                setup_real_fire_colors(args.background)
        elif ch == 100:  # d   reset all setting to default
            args.fire = "medium"
            speed = SPEED_LIST[DEFAULT_SPEED]
            args.multi = False
            args.color = "white"
            args.background = "black"
            args.real = False
            args.bold = args.bold_all = False
            set_color(args.color, args.background)
            args.char = DEFAULT_FIRE_CHARACTER
            args.base = DEFAULT_BASE_CHARACTER
        elif ch == 104:  # h
            current = FIRE_CHARACTER_LIST.index(args.char)
            if current < len(FIRE_CHARACTER_LIST) - 1:
                args.char = FIRE_CHARACTER_LIST[current + 1]
            else:
                args.char = FIRE_CHARACTER_LIST[0]
        elif ch == 72:  # H
            current = BASE_CHARACTER_LIST.index(args.base)
            if current < len(BASE_CHARACTER_LIST) - 1:
                args.base = BASE_CHARACTER_LIST[current + 1]
            else:
                args.base = BASE_CHARACTER_LIST[0]
        elif ch == 112:  # p   pause the fire
            while True:
                ch = screen.getch()
                if ch == 112:  # p
                    break
                elif ch in [81, 113]:  # q, Q
                    run = False
                    break
        elif 48 <= ch <= 57:  # number keys 0 to 9
            speed = SPEED_LIST[int(chr(ch))]
    screen.erase()
    screen.refresh()


def display_command() -> None:
    print("tfire running commands:")
    print("Q or q   Quit")
    print("m        Toggle multi color mode")
    print("c        Cycle through the colors")
    print("C        Cycle through background colors")
    print("r        Toggle real fire color mode")
    print("f        Cycle through the 3 different fire sizes")
    print("b        Toggle bold some of the characters")
    print("B        Toggle bold all characters")
    print("h        Cycle through the different characters")
    print("H        Cycle through the different bass characters")
    print("p        Pause the fire. Use p again to unpause")
    print("d        Reset setting to default")
    print("0 - 9    Speed of the fire  0-fast  5-default  9-slow")


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
    parser.add_argument("-b", "--bold", action="store_true",
                        help="Bold some")
    parser.add_argument("-B", "--bold_all", action="store_true",
                        help="Bold all")
    parser.add_argument("-r", "--real", action="store_true",
                        help="Real fire mode. Sort of looks like a real fire.")
    parser.add_argument("--background", type=str,
                        choices=list(BG_COLORS.keys()), default="black")
    parser.add_argument("-m", "--multi", action="store_true",
                        help="Multi color mode")
    parser.add_argument("-f", "--fire", type=str,
                        choices=["small", "medium", "large"],
                        default="medium",
                        help="Set the size of the fire. default: medium")
    parser.add_argument("--char", type=str, default=DEFAULT_FIRE_CHARACTER,
                        choices=FIRE_CHARACTER_LIST,
                        help="Set the character used for the fire")
    parser.add_argument("--base", type=str, default=DEFAULT_BASE_CHARACTER,
                        choices=BASE_CHARACTER_LIST,
                        help="set the character used for the base")
    parser.add_argument("--screensaver", action="store_true",
                        help="Screensaver mode. Any key will exit.")
    parser.add_argument("--list_commands", action="store_true",
                        help="Show list of running commands than exit.")
    return parser.parse_args()


def main():
    args = argument_parser()
    if args.list_commands:
        display_command()
    else:
        try:
            curses.wrapper(curses_main, args)
        except TFireError as e:
            print(e)


if __name__ == "__main__":
    main()
