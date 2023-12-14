from bot_client import BotClient


async def main():
    api_id = '25593200'
    api_hash = '688f17ed59a8a648453670a206429bc5'
    bot_token = '6487529586:AAHFlS-wEb8tqnV-zefMAQF9G4I9OUzjrWE'
    bot_client = BotClient(api_id, api_hash, bot_token)
    await bot_client.start()

    connected = False
    attempts = 0
    while not connected and attempts < 5:
        try:
            await bot_client.start()
            await bot_client.run_until_disconnected()
            connected = True
        except ConnectionError as e:
            attempts += 1
            print(f"Attempt {attempts} at connecting failed: {e}")
            if attempts < 5:
                print("Попробуем переподключиться...")
                await asyncio.sleep(10)
            else:
                print("Automatic reconnection failed 5 time(s)")
                break

if __name__ == '__main__':
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Программа была прервана пользователем")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
