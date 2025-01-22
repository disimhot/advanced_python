from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class ProfileSave(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    gender = State()
    city = State()
    diet = State()
    confirmation = State()
    status = State()

class WaterLog(StatesGroup):
    amount = State()

class FoodLog(StatesGroup):
    food = State()
    amount = State()

class WorkoutLog(StatesGroup):
    workout = State()
    minutes = State()