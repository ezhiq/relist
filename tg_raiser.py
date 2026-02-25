import asyncio
import logging
import traceback

from pyrogram import Client, types
from pyrogram.errors import FloodWait

logger = logging.getLogger("kurigram_relist")
logging.basicConfig(level=logging.INFO)

async def relist_unique_gifts(api_id, api_hash, session_name="my_account", no_updates=True):
    cd = int(input("Введите КД между циклами (сек): "))
    session_name = str(input("Введите КД между циклами (сек): "))

    async with Client(session_name, api_id=api_id, api_hash=api_hash, no_updates=True) as app:
        logger.info("✅ Подключено к Telegram")

        while True:
            try:
                # Получаем все подарки в облаке (сохарнённые)
                unique_gifts = []
                async for gift in app.get_chat_gifts("me"):
                    resale = getattr(gift, "resale_parameters", None)
                    if resale and getattr(resale, "star_count", 0) > 0 and getattr(gift, "is_saved", False):
                        unique_gifts.append({
                            "owned_id": f'https://t.me/nft/{gift.name}',
                            "current_price": resale.star_count,
                            "title": getattr(gift, "title", getattr(gift, "name", "NFT без названия"))
                        })

                if not unique_gifts:
                    logger.info("ℹ️ Нет уникальных подарков на продаже")
                    await asyncio.sleep(cd)
                    continue

                logger.info(f"📊 Найдено {len(unique_gifts)} уникальных подарков")

                relisted = 0
                failed = 0

                for info in unique_gifts:
                    owned_id = info["owned_id"]
                    price = info["current_price"]

                    try:
                        # Сбросить цену на 0
                        await app.set_gift_resale_price(owned_gift_id=owned_id)
                        await asyncio.sleep(2)

                        # Выставить обратно
                        await app.set_gift_resale_price(owned_gift_id=owned_id, price=types.GiftResalePriceStar(star_count=price))
                        logger.info(f"✅ Перевыставлено {owned_id}")
                        relisted += 1
                        await asyncio.sleep(3)

                    except FloodWait as fw:
                        logger.warning(f"⏳ Flood wait {fw.x} сек")
                        await asyncio.sleep(fw.x + 1)
                        # попробуем снова
                        try:
                            await app.set_gift_resale_price(owned_gift_id=owned_id, price=types.GiftResalePriceStar(star_count=price))
                            logger.info("   ✅ После ожидания успешно")
                            relisted += 1
                        except Exception as retry_err:
                            logger.error(f"   ❌ Повторная попытка провалилась: {retry_err}")
                            failed += 1

                    except Exception as e:
                        logger.error(f"❌ Ошибка при перевыставлении {owned_id}: {e}")
                        traceback.print_exc()
                        failed += 1

                logger.info("=" * 40)
                logger.info(f"📊 Итог: Успешно: {relisted}, Провалено: {failed}")

                await asyncio.sleep(cd)

            except Exception as e:
                logger.exception("❌ Общая ошибка")
                await asyncio.sleep(cd)

async def main():
    # Вставь свои api_id/api_hash
    API_ID = 2040
    API_HASH = 'b18441a1ff607e10a989891a5462e627'
    await relist_unique_gifts(API_ID, API_HASH)

if __name__ == "__main__":
    asyncio.run(main())