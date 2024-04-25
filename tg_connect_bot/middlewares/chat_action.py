import decouple

from aiogram import BaseMiddleware, Bot
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, TelegramObject, Update, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender

from typing import Callable, Dict, Any, Awaitable


bot = Bot(token=decouple.config('BOT_TOKEN'), parse_mode='html')


class ChatActionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        long_operation_type = get_flag(data, "long_operation")

        if not long_operation_type:
            return await handler(event, data)

        async with ChatActionSender(
            bot=bot,
            action=long_operation_type,
            chat_id=event.chat.id,
            interval=2
        ):
            return await handler(event, data)


class ChatActionMiddlewareCall(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        long_operation_type = get_flag(data, "long_operation")

        if not long_operation_type:
            return await handler(event, data)

        async with ChatActionSender(
            bot=bot,
            action=long_operation_type,
            chat_id=event.message.chat.id,
            interval=2
        ):
            return await handler(event, data)
