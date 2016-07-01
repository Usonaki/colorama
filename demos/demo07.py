from __future__ import print_function
import fixpath
import colormania

# Demonstrate cursor relative movement: UP, DOWN, FORWARD, and BACK in colormania.CURSOR

up = colormania.Cursor.UP
down = colormania.Cursor.DOWN
forward = colormania.Cursor.FORWARD
back = colormania.Cursor.BACK

def main():
    """
    expected output:
    1a2
    aba
    3a4
    """
    colormania.init()
    print("aaa")
    print("aaa")
    print("aaa")
    print(forward() + up(2) + "b" + up() + back(2) + "1" + forward() + "2" + back(3) + down(2) + "3" + forward() + "4")


if __name__ == '__main__':
    main()
    input('Press ENTER to quit')
