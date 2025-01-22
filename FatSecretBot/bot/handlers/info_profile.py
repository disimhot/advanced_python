from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.helpers import BotCommands
from bot.states import ProfileSave, WaterLog, FoodLog, WorkoutLog
from bot.storage import add_profile_params, get_profile_params_by_id, update_profile_params
from bot.helpers import Person, Food
from bot.helpers.menu import change_main_menu
from bot.keyboards.trainings import get_training_kb

router: Router = Router()
food_searcher = Food()


@router.callback_query(ProfileSave.confirmation)
async def process_confirmation(callback_query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    status = callback_query.data
    if status == "confirm":
        await callback_query.answer("Подожите, бот рассчитывает норму калорий...")
        await state.update_data(status=status)

        data = await state.get_data()
        person = Person(**data)
        calorie_goal = person.count_daily_calorie_rate()
        water_goal = await person.count_daily_water_rate()
        data['logged_calories'] = [calorie_goal]
        data['logged_water'] = [water_goal]
        data['water_goal'] = water_goal
        data['calorie_goal'] = calorie_goal
        add_profile_params(callback_query.from_user.id, data)
        await callback_query.message.reply(
            f"Ваша норма калорий: {calorie_goal} ккал\nВаша норма воды: {water_goal} мл")
        await change_main_menu(bot)
        await state.clear()
    elif status == "cancel":
        print('NO')

@router.message(Command(BotCommands.LogWater.value))
async def log_water(message: Message, state: FSMContext) -> None:
    await message.reply("Введите количество выпитой воды: ")
    await state.set_state(WaterLog.amount)


@router.message(WaterLog.amount)
async def process_water_amount(message: Message, state: FSMContext) -> None:
    water_amount = int(message.text)
    await state.update_data(water_amount=water_amount)
    await message.answer("Подожите, бот рассчитывает оставшуюся норму воды...")
    person_data = get_profile_params_by_id(message.from_user.id)
    water_goal = person_data.get('water_goal')
    logged_water = person_data.get('logged_water')
    water_goal -= water_amount
    logged_water.append(water_goal)
    data = {
        'water_goal': water_goal,
        'logged_water': logged_water
    }

    update_profile_params(message.from_user.id, data)

    await state.clear()
    await message.answer(
        f"Выпито: {water_amount} мл\nОсталось выпить воды: "
        f"{water_goal if water_goal >= 0 else 0} мл")


@router.message(Command(BotCommands.LogFood.value))
async def log_food(message: Message, state: FSMContext) -> None:
    await message.reply("Введите название продукта: ")
    await state.set_state(FoodLog.food)


@router.message(FoodLog.food)
async def process_food_name(message: Message, state: FSMContext) -> None:
    food_name = message.text
    await state.update_data(food_name=food_name)
    await message.reply("Введите количество в граммах: ")
    await state.set_state(FoodLog.amount)


@router.message(FoodLog.amount)
async def process_food_amount(message: Message, state: FSMContext) -> None:
    food_amount = int(message.text)
    await state.update_data(amount=food_amount)
    state_data = await state.get_data()
    await message.answer("Подожите, бот рассчитывает калории...")
    person_data = get_profile_params_by_id(message.from_user.id)
    calorie_goal = person_data.get('calorie_goal')
    logged_calories = person_data.get('logged_calories')
    nutritional_info = await food_searcher.fetch_fatsecret_data(**state_data)
    calories, fat, carbs, protein = nutritional_info.values()
    logged_cal = calories * food_amount // 100
    new_calorie_goal = calorie_goal - logged_cal
    logged_calories.append(new_calorie_goal)
    data = {
        'calorie_goal': new_calorie_goal,
        'logged_calories': logged_calories
    }
    update_profile_params(message.from_user.id, data)

    await state.clear()
    await message.answer(
        f"Потреблено: {logged_cal} ккал\nОсталось потребить: "
        f"{new_calorie_goal if new_calorie_goal >= 0 else 0} ккал")


@router.message(Command(BotCommands.LogWorkout.value))
async def log_workout(message: Message, state: FSMContext) -> None:
    data = get_profile_params_by_id(message.from_user.id)
    await message.answer(
        "Пожалуйста, выберите тренировку ниже:",
        reply_markup=get_training_kb()
    )

