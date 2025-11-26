"""Foreground Vision Farm

Farm approach: Using OpenCV it will track the name of the mob.
Currently it's aiming to all lv 150 mobs in Neo Cascada, but it can be extended.
"""
from Bot import Bot
# from Gui import Gui
from RemiGui import MyApp
from utils.helpers import print_logo
from remi import start

# Instances
# gui = Gui("DarkAmber")
# app = MyApp()
bot = Bot()


def main():
    # gui.init()
    # gui.loop(bot)
    # gui.close()
    start(MyApp, debug=True, address='0.0.0.0', port=8081, start_browser=True, multiple_instance=True, userdata=(bot,))
    # start(MyApp, debug=True, standalone=True, userdata=(Bot,))

if __name__ == "__main__":
    print_logo("Flyff FVF")
    main()