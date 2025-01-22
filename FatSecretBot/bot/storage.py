from typing import Optional

data = dict()


def add_profile_params(
        telegram_id: int,
        params: dict
):
    data[telegram_id] = params

def is_profile_exist(telegram_id: int) -> bool:
    return telegram_id in data

def get_profile_params_by_id(telegram_id: int) -> dict:
    if telegram_id in data:
        return data[telegram_id]
    return dict()


def update_profile_params(telegram_id: int, updated_params: dict) -> None:
    if telegram_id in data:
        data[telegram_id].update(updated_params)
    else:
        raise ValueError(f"User with id {telegram_id} not found")


def delete_profile_by_id(telegram_id: int):
    if telegram_id in data:
        del data[telegram_id]
