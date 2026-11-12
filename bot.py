import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # ከ BotFather ያገኙትን ቶከን እዚህ ያስገቡ
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("ሰላም! የደብረ ገሊላ እማማ የሰንበት ትምህርት ቤት የቲኬት ማረጋገጫ ቦት ነው።")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())