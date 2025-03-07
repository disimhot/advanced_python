from enum import Enum


class BotCommands(Enum):
    StartCommand = 'start'
    HelpCommand = 'help'
    StopCommand = 'stop'
    SetProfileCommand = 'set_profile'
    LogWater = 'log_water'
    LogFood = 'log_food'
    LogWorkout = 'log_workout'
    CheckProgress = 'check_progress'
    GetGraph = 'get_graph'
    GetRecommendations = 'get_recommendations'