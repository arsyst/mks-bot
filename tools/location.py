import aiohttp  # модуль aiohttp устанавливается как зависимость от модуля aiogram


async def get_location():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://api.open-notify.org/iss-now.json') as resp:
            obj = await resp.json()

    return float(obj['iss_position']['latitude']), float(obj['iss_position']['latitude'])