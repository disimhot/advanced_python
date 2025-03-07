from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_training_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text="Бег", callback_data="run"),
        InlineKeyboardButton(text="Велосипед", callback_data="bike"),
        InlineKeyboardButton(text="Силовая", callback_data="strength"),
        InlineKeyboardButton(text="Плавание", callback_data="swim"),
        InlineKeyboardButton(text="Кардио", callback_data="cardio"),
        InlineKeyboardButton(text="Ходьба", callback_data="walking"),
    ]
    keyboard.add(*buttons)
    return keyboard
