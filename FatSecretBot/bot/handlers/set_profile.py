from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.helpers import BotCommands
from bot.states import ProfileSave

router: Router = Router()


@router.message(Command(BotCommands.SetProfileCommand.value))
async def set_profile_command(message: Message, state: FSMContext) -> None:
    await message.reply("Введите ваш вес: ")
    await state.set_state(ProfileSave.weight)


@router.message(ProfileSave.weight)
async def process_height(message: Message, state: FSMContext) -> None:
    weight = int(message.text)
    await state.update_data(weight=weight)
    await message.reply("Введите ваш рост: ")
    await state.set_state(ProfileSave.height)


@router.message(ProfileSave.height)
async def process_height(message: Message, state: FSMContext) -> None:
    height = int(message.text)
    await state.update_data(height=height)
    await message.reply("Введите ваш возраст: ")
    await state.set_state(ProfileSave.age)


@router.message(ProfileSave.age)
async def process_age(message: Message, state: FSMContext) -> None:
    age = int(message.text)
    await state.update_data(age=age)
    await message.reply("Введите вашу активность (количество шагов в день): ")
    await state.set_state(ProfileSave.activity)


@router.message(ProfileSave.activity)
async def process_activity(message: Message, state: FSMContext) -> None:
    activity = int(message.text)
    await state.update_data(activity=activity)
    kb = InlineKeyboardBuilder()
    kb.button(text="Мужской", callback_data="male")
    kb.button(text="Женский", callback_data="female")
    await message.reply("Выберите ваш пол:", reply_markup=kb.as_markup())
    await state.set_state(ProfileSave.gender)


@router.callback_query(ProfileSave.gender)
async def process_gender(callback_query: CallbackQuery, state: FSMContext) -> None:
    gender = callback_query.data
    await state.update_data(gender=gender)
    await callback_query.message.reply("Введите ваш город: ")
    await state.set_state(ProfileSave.city)
    await callback_query.answer()


@router.message(ProfileSave.city)
async def process_city(message: Message, state: FSMContext) -> None:
    city = message.text
    await state.update_data(city=city)
    kb = InlineKeyboardBuilder()
    kb.button(text="Похудение", callback_data="lose_weight")
    kb.button(text="Удержание веса", callback_data="maintain_weight")
    kb.button(text="Набор", callback_data="gain_weight")
    await message.reply("Выберите вашу цель: ", reply_markup=kb.as_markup())
    await state.set_state(ProfileSave.diet)


@router.callback_query(ProfileSave.diet)
async def process_diet(callback_query: CallbackQuery, state: FSMContext) -> None:
    diet = callback_query.data
    data = await state.get_data()
    await state.update_data(diet=diet)
    await callback_query.answer()
    await callback_query.message.reply(
        f"Вес: {data.get('weight')} кг\nРост: {data.get('height')} см\nВозраст: {data.get('age')} "
        f"лет\nАктивность: {data.get('activity')} шагов в день\nПол: "
        f"{data.get('gender')}\nГород: {data.get('city')}\nЦель: {diet}\n"
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data="confirm")
    kb.button(text="Нет", callback_data="cancel")
    await callback_query.message.reply("Подтвердить?", reply_markup=kb.as_markup())
    await state.set_state(ProfileSave.confirmation)
