import asyncio
import traceback

from telethon import TelegramClient, functions, types
from telethon.errors import RPCError

import logging
# Создаем логгеры для разных компонентов
logger = logging.getLogger("raise_tg")  # Основной логгер для модуля

async def relist_unique_gifts(client=None):

    print('Введите кд на поднятие')
    sex = int(input())
    if client is None:
        client = TelegramClient(
            session=fr"Zabwino",
            api_id=2040,
            api_hash='b18441a1ff607e10a989891a5462e627',
            system_version='iOS 16.4',
            app_version='9.7.0'
        )
        await client.start()

    try:
        while True:
            """
            Перевыставляет уникальные подарки (убирает и снова ставит на продажу)
            с сохранением цены
            """
            try:
                logger.info("✅ Подключено к Telegram")

                # Получаем текущего пользователя

                # Получаем все подарки пользователя (включая уникальные)
                all_gifts = await client(functions.payments.GetSavedStarGiftsRequest(
                    peer=types.InputPeerSelf(),
                    offset="",
                    limit=100
                ))

                if not isinstance(all_gifts, types.payments.SavedStarGifts) or not all_gifts.gifts:
                    logger.info("ℹ️ Нет подарков для перевыставления")
                    await asyncio.sleep(sex)
                    continue

                # Фильтруем только уникальные подарки, которые можно продавать
                unique_gifts_for_relist = []

                for gift in all_gifts.gifts:
                    # Проверяем, можно ли продавать этот подарок
                    if hasattr(gift.gift, 'slug'):
                        detailed = await client(functions.payments.GetUniqueStarGiftRequest(
                            slug=gift.gift.slug
                        ))

                        nft_info = {
                            'saved_id': gift.gift.gift_id,
                            'current_price': detailed.gift.resell_amount[0].amount if detailed.gift.resell_amount else 0,
                            'title': getattr(gift.gift, 'title', 'NFT без названия'),
                            'slug': getattr(gift.gift, 'slug', None),
                            'can_resell_at': getattr(gift, 'can_resell_at', 0),
                            'resell_amount': None
                        }

                        if nft_info['slug']:
                            try:
                                detailed = await client(functions.payments.GetUniqueStarGiftRequest(
                                    slug=nft_info['slug']
                                ))

                                if (hasattr(detailed, 'gift') and
                                        hasattr(detailed.gift, 'resell_amount') and
                                        detailed.gift.resell_amount):
                                    nft_info['resell_amount'] = detailed.gift.resell_amount
                                    unique_gifts_for_relist.append(nft_info)
                            except:
                                pass

                if not unique_gifts_for_relist:
                    logger.info("ℹ️ Нет уникальных подарков на продаже для перевыставления")
                    await asyncio.sleep(sex)
                    continue

                logger.info(f"📊 Найдено {len(unique_gifts_for_relist)} уникальных подарков на продаже")

                # Перевыставляем каждый подарок
                relisted_count = 0
                failed_count = 0

                for gift_info in unique_gifts_for_relist:
                    saved_id = gift_info['saved_id']
                    current_price = gift_info['current_price']
                    title = gift_info['title']

                    try:
                        # Шаг 1: Убираем с продажи (цена = 0)
                        await client(functions.payments.UpdateStarGiftPriceRequest(
                            stargift=types.InputSavedStarGiftSlug(
                                slug=gift_info['slug']
                            ),
                            resell_amount=types.StarsAmount(amount=0, nanos=0)
                        ))

                        await asyncio.sleep(2)  # Пауза между операциями

                        # Шаг 2: Снова выставляем на продажу с той же ценой
                        await client(functions.payments.UpdateStarGiftPriceRequest(
                            stargift=types.InputSavedStarGiftSlug(
                                slug=gift_info['slug']
                            ),
                            resell_amount=types.StarsAmount(amount=current_price, nanos=0)
                        ))

                        relisted_count += 1

                        # Пауза между подарками чтобы не получить flood wait
                        await asyncio.sleep(3)

                    except RPCError as e:
                        if "FLOOD_WAIT" in str(e):
                            wait_time = int(str(e).split()[-1])
                            logger.info(f"   ⏳ Flood wait {wait_time} секунд...")
                            await asyncio.sleep(wait_time + 1)

                            # Пробуем еще раз
                            try:
                                # Пропускаем снятие, если уже снято
                                await client(functions.payments.UpdateStarGiftPriceRequest(
                                    stargift=types.InputSavedStarGiftChat(
                                        peer=types.InputPeerSelf(),
                                        saved_id=saved_id
                                    ),
                                    resell_amount=types.StarsAmount(amount=current_price, nanos=0)
                                ))
                                logger.info("   ✅ Успешно перевыставлено после flood wait")
                                relisted_count += 1
                            except Exception as retry_error:
                                logger.info(f"   ❌ Ошибка при повторной попытке: {retry_error}")
                                failed_count += 1
                        else:
                            logger.info(f"   ❌ Ошибка при перевыставлении: {e}")
                            failed_count += 1

                    except Exception as e:
                        logger.info(f"   ❌ Неожиданная ошибка: {e}")
                        failed_count += 1

                logger.info("\n" + "=" * 60)
                logger.info("📊 РЕЗУЛЬТАТ ПЕРЕВЫСТАВЛЕНИЯ:")
                logger.info(f"✅ Успешно перевыставлено: {relisted_count}")
                logger.info(f"❌ Не удалось перевыставить: {failed_count}")
                if failed_count == 0 and relisted_count > 0:
                    logger.info("🎉 Все подарки успешно обновлены!")

                await asyncio.sleep(sex)

            except RPCError as e:
                logger.info(f"❌ Ошибка Telegram API: {e}")
                return
            except Exception as e:
                logger.info(f"❌ Неожиданная ошибка: {e}")
                traceback.print_exc()
                return
    except:
        raise

async def tg_raiser_main(client):
    await relist_unique_gifts(client)

async def main():
    await relist_unique_gifts()
if __name__ == '__main__':
    asyncio.run(main())