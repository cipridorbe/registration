import os
from dotenv import load_dotenv
import asyncio
from courses import Courses
from telegram import Bot
from users import Users
from time import sleep

async def main():
    load_dotenv()
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    bot = Bot(token)
    users = Users()
    courses = Courses.read_from_txt_file('courses.txt')

    iters = 10000
    for i in range(iters):
        # Re-read users and courses.txt every 25 iterations
        if i % 25 == 0:
            users = Users()
            courses.update_tracked_courses('courses.txt')
        changes = courses.update_all_availability()
        users.notify_changes(courses, changes, bot)

    sleep(5)

    changes = courses.update_all_availability()
    await users.notify_changes(courses, changes, bot)

    courses.save_to_file()

if __name__ == '__main__':
    asyncio.run(main())