import logging
import json
import sys
import datetime as dt
import os
import dominionator.game as dominion
import dominionator.statlog as dlog


def main():
    if len(sys.argv) != 2:
        print("Usage: python run.py config")
        sys.exit(1)

    with open(sys.argv[1]) as fp:
        game_config = json.load(fp)

    logging.basicConfig(
        format='%(levelname)s:%(message)s', level=game_config['log_level']
    )
    stat_log = dlog.StatLog(
        filename=os.path.join('logs', dt.datetime.now().isoformat())
    )

    for i in range(game_config['n_games']):
        game = dominion.Game(
            stat_log=stat_log, game_index=i,
            **game_config['game']
        )
        game.start_main_loop()
    stat_log.write()


if __name__ == '__main__':
    main()
