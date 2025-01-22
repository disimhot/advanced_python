from aiogram import Router

from . import common, set_profile, info_profile


def get_routers() -> list[Router]:
    return [
        common.router,
        set_profile.router,
        info_profile.router
    ]