# Duravoke

A (experimental) mini durable execution library, with an extreme focus on simplicity.

## Install

via pip: `pip install duravoke`

via uv: `uv add duravoke`

## What is Durable Execution?

While there are already [great answers to this question](https://temporal.io/blog/what-is-durable-execution), the simplest definition is this:

> Durable execution means your code can crash, restart, and still finish exactly once.

As long as you wrap your critical methods with `duravoke`, you can rest assured that you can keep calling them until they eventually succeed, after which subsequent calls will be idempotent.

## Design Principles

While durable execution is a core feature of many workflow execution frameworks *(e.g. [Temporal](https://temporal.io/blog/what-is-durable-execution), [LangGraph](https://docs.langchain.com/oss/python/langgraph/durable-execution), [Inngest](https://www.inngest.com/uses/durable-workflows?ref=nav), etc.)*, they also come with a lot of extra baggage: specific database requirements, multiple required microservices, paywall gated features, and steep learning curves.

That baggage, while in many ways is necessary for mature software, is overkill in a world being infiltrated with vibe-coded micro SaaS applications. This type of software needs something simpler to setup and easy to understand.

## Demo

Here is a toy snippet to set the stage of a codebase that needs to run some very error prone process.

In this case, we need to send emails to 10 users, but our `send_email` method is *very* flaky. It has a 50% probability of just crashing our server entirely 🔥

```python3
import asyncio
import time
import random

async def send_email(user_id: int):
    if random.random() > 0.5:
        print("crash 🔥")
        quit()

    curr_time = round(time.time())
    return f"Sent email to user_id: {user_id} at {curr_time}"

async def send_emails(user_ids: list[int]):
    for user_id in user_ids:
        email_output = await send_email(user_id)
        print(email_output)
    print("finished 😎")


asyncio.run(send_emails(list(range(10))))
```

Math tells us that the above code has a ~0.1% chance of ever printing `"finished 😎"`.

In other words, you would need to run it 1024 times to ever have a chance of seeing it print `"finished 😎"`.

Now, just add the `@duravoke.duravoke` decorator to both methods.

```python3
# hello_durable_flaky.py
import asyncio
import time
import random
from duravoke import Duravoke, PersistedKKV, JSONSerializer

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
        print(email_output)
    print("finished 😎")


asyncio.run(email_users(list(range(10))))
```

Now, while the above code still has a high chance of failure, subsequent reruns of it will pick up from where it left off.

The below logs show an example of running `python hello_durable_flaky.py` 3 times.


<table>
  <thead>
    <tr>
      <th><img alt="Run 1 (blue)" src="https://img.shields.io/badge/Run%201-blue?style=flat-square" /></th>
      <th><img alt="Run 2 (green)" src="https://img.shields.io/badge/Run%202-green?style=flat-square" /></th>
      <th><img alt="Run 3 (purple)" src="https://img.shields.io/badge/Run%203%20(all%20emails%20sent)-purple?style=flat-square" /></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Sent email to user_id: 0 at <img alt="1769848541 (blue)" src="https://img.shields.io/badge/1769848541-blue?style=flat-square" /></td>
      <td>Sent email to user_id: 0 at <img alt="1769848541 (blue)" src="https://img.shields.io/badge/1769848541-blue?style=flat-square" /></td>
      <td>Sent email to user_id: 0 at <img alt="1769848541 (blue)" src="https://img.shields.io/badge/1769848541-blue?style=flat-square" /></td>
    </tr>
    <tr>
      <td>Sent email to user_id: 1 at <img alt="1769848541 (blue)" src="https://img.shields.io/badge/1769848541-blue?style=flat-square" /></td>
      <td>Sent email to user_id: 1 at <img alt="1769848541 (blue)" src="https://img.shields.io/badge/1769848541-blue?style=flat-square" /></td>
      <td>Sent email to user_id: 1 at <img alt="1769848541 (blue)" src="https://img.shields.io/badge/1769848541-blue?style=flat-square" /></td>
    </tr>
    <tr>
      <td>Sent email to user_id: 2 at <img alt="1769848541 (blue)" src="https://img.shields.io/badge/1769848541-blue?style=flat-square" /></td>
      <td>Sent email to user_id: 2 at <img alt="1769848541 (blue)" src="https://img.shields.io/badge/1769848541-blue?style=flat-square" /></td>
      <td>Sent email to user_id: 2 at <img alt="1769848541 (blue)" src="https://img.shields.io/badge/1769848541-blue?style=flat-square" /></td>
    </tr>
    <tr>
      <td>Sent email to user_id: 3 at <img alt="1769848541 (blue)" src="https://img.shields.io/badge/1769848541-blue?style=flat-square" /></td>
      <td>Sent email to user_id: 3 at <img alt="1769848541 (blue)" src="https://img.shields.io/badge/1769848541-blue?style=flat-square" /></td>
      <td>Sent email to user_id: 3 at <img alt="1769848541 (blue)" src="https://img.shields.io/badge/1769848541-blue?style=flat-square" /></td>
    </tr>
    <tr>
      <td>crash 🔥</td>
      <td>Sent email to user_id: 4 at <img alt="1769848547 (green)" src="https://img.shields.io/badge/1769848547-green?style=flat-square" /></td>
      <td>Sent email to user_id: 4 at <img alt="1769848547 (green)" src="https://img.shields.io/badge/1769848547-green?style=flat-square" /></td>
    </tr>
    <tr>
      <td>&nbsp;</td>
      <td>Sent email to user_id: 5 at <img alt="1769848547 (green)" src="https://img.shields.io/badge/1769848547-green?style=flat-square" /></td>
      <td>Sent email to user_id: 5 at <img alt="1769848547 (green)" src="https://img.shields.io/badge/1769848547-green?style=flat-square" /></td>
    </tr>
    <tr>
      <td>&nbsp;</td>
      <td>Sent email to user_id: 6 at <img alt="1769848547 (green)" src="https://img.shields.io/badge/1769848547-green?style=flat-square" /></td>
      <td>Sent email to user_id: 6 at <img alt="1769848547 (green)" src="https://img.shields.io/badge/1769848547-green?style=flat-square" /></td>
    </tr>
    <tr>
      <td>&nbsp;</td>
      <td>crash 🔥</td>
      <td>Sent email to user_id: 7 at <img alt="1769848552 (purple)" src="https://img.shields.io/badge/1769848552-purple?style=flat-square" /></td>
    </tr>
    <tr>
      <td>&nbsp;</td>
      <td>&nbsp;</td>
      <td>Sent email to user_id: 8 at <img alt="1769848552 (purple)" src="https://img.shields.io/badge/1769848552-purple?style=flat-square" /></td>
    </tr>
    <tr>
      <td>&nbsp;</td>
      <td>&nbsp;</td>
      <td>Sent email to user_id: 9 at <img alt="1769848552 (purple)" src="https://img.shields.io/badge/1769848552-purple?style=flat-square" /></td>
    </tr>
    <tr>
      <td>&nbsp;</td>
      <td>&nbsp;</td>
      <td>finished 😎</td>
    </tr>
  </tbody>
</table>


Note how when a email was sent to a user in one run, it logs a timestamp. In subsequent runs, that **same timestamp** is logged. The user isn't sent a duplicate email.

Each run of [`hello_durable_flaky.py`](./examples/hello_durable_flaky.py) becomes idempotent based on the last run. Moreover, this idempotency is completely abstracted away for you the developer. All you need to do is add the `@duravoke.duravoke` decorators.

## How do I use this IRL?

Ok great, now you can feasibly finish sending all 10 users an email without having to worry about:

* Running the script 1024 times (durable execution)
* Sending duplicate emails (idempotency)

But you still need a way to call the `email_users` method until it finishes the entire user list. And that is the part that `duravoke` is unopinionated on. You can just keep a list of tasks to execute in a database or a queue, and a cron job for reading those tasks, and calling your `@durovoke.duravoke` decorated method with the task's parameters.

There are great libraries for managing tasks queues, such as [`celery`](https://docs.celeryq.dev/) or [`bullmq`](https://bullmq.io/).
