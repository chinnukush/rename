import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from helper.database import jishubotz
from pyromod import listen
from config import Txt


# ✅ Buttons
ON = [
    [InlineKeyboardButton('Metadata On ✅', callback_data='metadata_1')],
    [InlineKeyboardButton('Set Custom Metadata', callback_data='custom_metadata')]
]

OFF = [
    [InlineKeyboardButton('Metadata Off ❌', callback_data='metadata_0')],
    [InlineKeyboardButton('Set Custom Metadata', callback_data='custom_metadata')]
]


# ✅ /metadata command
@Client.on_message(filters.private & filters.command('metadata'))
async def handle_metadata(bot: Client, message: Message):

    ms = await message.reply_text("**Please Wait...**")
    
    bool_metadata = await jishubotz.get_metadata(message.from_user.id)
    user_metadata = await jishubotz.get_metadata_code(message.from_user.id)

    await ms.delete()

    if bool_metadata:
        return await message.reply_text(
            f"**Your Current Metadata :-**\n\n➜ `{user_metadata}`",
            reply_markup=InlineKeyboardMarkup(ON)
        )
    else:
        return await message.reply_text(
            f"**Your Current Metadata :-**\n\n➜ `{user_metadata}`",
            reply_markup=InlineKeyboardMarkup(OFF)
        )


# ✅ Callback handler
@Client.on_callback_query(filters.regex('metadata_|custom_metadata'))
async def query_metadata(bot: Client, query: CallbackQuery):

    data = query.data

    # ✅ ON / OFF toggle
    if data.startswith('metadata_'):
        _bool = data.split('_')[1]
        user_metadata = await jishubotz.get_metadata_code(query.from_user.id)

        if _bool == "1":
            await jishubotz.set_metadata(query.from_user.id, bool_meta=False)
            await query.message.edit(
                f"**Your Current Metadata :-**\n\n➜ `{user_metadata}`",
                reply_markup=InlineKeyboardMarkup(OFF)
            )
        else:
            await jishubotz.set_metadata(query.from_user.id, bool_meta=True)
            await query.message.edit(
                f"**Your Current Metadata :-**\n\n➜ `{user_metadata}`",
                reply_markup=InlineKeyboardMarkup(ON)
            )

    # ✅ Set custom metadata
    elif data == 'custom_metadata':
        await query.message.delete()

        try:
            # Ask user for metadata
            try:
                metadata = await bot.ask(
                    query.from_user.id,
                    Txt.SEND_METADATA,
                    filters=filters.text,
                    timeout=30
                )
            except asyncio.TimeoutError:
                await bot.send_message(
                    query.from_user.id,
                    "⚠️ Request Timed Out.\n\nRestart using /metadata"
                )
                return

            # Save metadata
            ms = await bot.send_message(query.from_user.id, "**Please Wait...**")
            await jishubotz.set_metadata_code(
                query.from_user.id,
                metadata_code=metadata.text
            )

            await ms.edit("**Your Metadata Code Set Successfully ✅**")

        except Exception as e:
            print(e)
