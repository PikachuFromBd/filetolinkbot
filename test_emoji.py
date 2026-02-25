from pyrogram import Client, enums
import asyncio

app = Client("test_emoji", api_id=21857455, api_hash="3f89f195e4e28c09bff128f55b358426", bot_token="7863139740:AAFiEtiViInkBXLox68LRr9ICaCYy33QfPg")

async def main():
    async with app:
        text = '<b>Hello!</b>\nHere is a premium emoji: <tg-emoji emoji-id="5368324170671202286">👋</tg-emoji>\n<i>Test custom emoji</i>'
        await app.send_message(
            chat_id=6129625814,
            text=text,
            parse_mode=enums.ParseMode.HTML
        )
        print("OK sent!")

app.run(main())
