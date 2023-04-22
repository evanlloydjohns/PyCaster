from enum import Enum


class GameState(Enum):
    """
    Used to determine what state the game is in
    """

    GAME = 0
    PAUSE_MENU = 1
    START_MENU = 2