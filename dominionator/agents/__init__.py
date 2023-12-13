from dominionator.agents.base import NO_SELECT, WAITING_INPUT, ALL_TREASURES
from dominionator.agents.base import Agent
from dominionator.agents.random import RandomAgent
from dominionator.agents.human import HumanAgent
from dominionator.agents.bigmoney import BigMoneyAgent, SmithyBigMoneyAgent
from dominionator.agents.ml import MlSmithyBigMoneyAgent, MlRandomAgent

lookup = {
    'Human': HumanAgent,
    'BigMoney': BigMoneyAgent,
    'Random': RandomAgent,
    'SmithyBigMoney': SmithyBigMoneyAgent,
    'MlSmithyBigMoney': MlSmithyBigMoneyAgent,
    'MlRandom': MlRandomAgent
}
