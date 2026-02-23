"""Starting gui as standalone app"""
from Bot import Bot
from RemiGui import EnhancedFlyffBot
from remi import start

def main():
    bot = Bot()
    start(EnhancedFlyffBot, debug=False, standalone=True, width=630, height=760, userdata=(bot,))

if __name__ == "__main__":
    main()
