from courses import Courses
from course import Course
from pathlib import Path

class Users:
    def __init__(self, path_to_dir: str = 'users/'):
        folder = Path(path_to_dir)
        users = []
        for user_file_path in folder.glob('*.txt'):
            with open(user_file_path, 'r') as user_file:
                chat_id = user_file.readline().strip()
                crns = []
                for line in user_file:
                    line = line.strip()
                    if line:
                        crns.append(int(line))
                users.append({
                    'chat_id': chat_id,
                    'crns': crns
                })
        self.users = users

    async def notify_changes(self, courses: Courses, changes, bot):
        for crn in changes:
            if not changes[crn]:
                continue
            course = courses.find_course(crn)
            if course is None:
                continue
            message = course.generate_message(changes[crn])
            for user in self.users:
                if crn in user['crns']:
                    await bot.send_message(chat_id=user['chat_id'], text=message)

            