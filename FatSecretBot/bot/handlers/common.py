from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.storage import is_profile_exist
from bot.helpers.menu import change_main_menu
from bot.helpers import BotCommands

router: Router = Router()


@router.message(CommandStart())
async def start_command(message: Message, _state: FSMContext, bot: Bot) -> None:
    telegram_id = message.from_user.id
    if is_profile_exist(telegram_id):
        await change_main_menu(bot)

    kb = InlineKeyboardBuilder()
    await message.answer(
        "Привет! Я бот, который умеет рассчитывать норму калорий, а также поможет с выбором "
        "продуктов.\n\nДля начала работы введите /set_profile",
        reply_markup=kb.as_markup()
    )


@router.message(Command(BotCommands.HelpCommand.value))
async def help_command(message: Message) -> None:
    await message.answer(
        'Этот бот поможет рассчитать дневные нормы калорий и воды\nДля начала работы введите '
        '/set_profile 🆘'
    )
