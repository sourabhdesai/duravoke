import asyncio
import time
import random
from src.duravoke import Duravoke
from src.kv import PersistedKKV
from src.serializer import JSONSerializer

kv = PersistedKKV("./duravoke_state.json")
duravoke = Duravoke(kv, JSONSerializer())

@duravoke.duravoke
async def send_email(user_id: int):
    if random.random() > 0.5:
        # Our Email API has a 50% chance of failing :(
        print("crash 🔥")
        quit()

    curr_time = round(time.time())
    return f"Sent email to user_id: {user_id} at {curr_time}"

@duravoke.duravoke
async def email_users(user_ids: list[int]):
    for user_id in user_ids:
        email_output = await send_email(user_id)
        print(f"{email_output}")
    print("finished 😎")


asyncio.run(email_users(list(range(10))))
