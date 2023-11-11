import csv


class StatLog(object):
    def __init__(self, filename: str):
        self._filename = filename
        self._keys = ['game_i', 'turn_i', 'player', 'measure', 'value']
        self.log_items = []

    def add_item(self, game_i: int, turn_i: int, player: str, measure: str, value):
        self.log_items += [
            {
                "game_i": game_i,
                "turn_i": turn_i,
                "player": player,
                "measure": measure,
                "value": value
            }
        ]

    def add_items_from_turnstats(self, game_i: int, turn_i: int, player: str, turnstats: dict):
        for measure, value in turnstats.items():
            if value is not None:
                self.add_item(game_i, turn_i, player, measure, value)

    def write(self):
        with open(self._filename, 'w') as fp:
            writer = csv.DictWriter(fp, fieldnames=self._keys)
            writer.writeheader()
            writer.writerows(self.log_items)
