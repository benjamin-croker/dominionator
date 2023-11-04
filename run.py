import logging
import dominionator.game as dominion


def main():
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    game = dominion.Game()
    game.start_main_loop()
    logging.info(game)


if __name__ == '__main__':
    main()
