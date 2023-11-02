import logging
from game import GameState


def main():
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    game_state = GameState()


if __name__ == '__main__':
    main()
