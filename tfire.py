import curses
import random
import time

WHITE = [15, 255, 252, 250, 248, 246, 244, 242, 240, 238, 237]


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
        if self.y <= self.height - 4 and self.brightness < 11:
            self.brightness += 1
        self.y -= 1
        self.screen.addstr(
            self.y,
            self.x,
            self.char,
            curses.color_pair(self.brightness))
        return False


def set_color() -> None:
    if curses.COLORS < 255:
        for i in range(len(WHITE)):
            curses.init_pair(i + 1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    else:
        for i, c in enumerate(WHITE):
            curses.init_pair(i + 1, c, curses.COLOR_BLACK)


def curses_main(screen):
    curses.curs_set(0)  # Set the cursor to off.
    screen.timeout(0)  # Turn blocking off for screen.getch().
    height = curses.LINES
    width = curses.COLS
    set_color()
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
        time.sleep(0.02)


def main():
    curses.wrapper(curses_main)


if __name__ == "__main__":
    main()
