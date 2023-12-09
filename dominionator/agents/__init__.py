from dominionator.agents.base import NO_SELECT, WAITING_INPUT, ALL_TREASURES
from dominionator.agents.base import Agent
from dominionator.agents.human import HumanAgent
from dominionator.agents.bigmoney import BigMoneyAgent, SmithyBigMoneyAgent
from dominionator.agents.ml import MlSmithyBigMoneyAgent

lookup = {
    'Human': HumanAgent,
    'BigMoney': BigMoneyAgent,
    'SmithyBigMoney': SmithyBigMoneyAgent,
    'MlSmithyBigMoney': MlSmithyBigMoneyAgent
}
