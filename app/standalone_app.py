"""Starting gui as standalone app"""
from Bot import Bot
from RemiGui import RemiApp
from remi import start

def main():
    bot = Bot()
    start(RemiApp, debug=False, standalone=True, width=630, height=760, userdata=(bot,))

if __name__ == "__main__":
    main()
