"""Starting gui as browser page"""
from Bot import Bot
from RemiGui import RemiApp
from remi import start

def main():
    bot = Bot()
    start(RemiApp, debug=False, address='0.0.0.0', port=8081, start_browser=True, multiple_instance=True, userdata=(bot,))

if __name__ == "__main__":
    main()
