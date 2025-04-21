from __future__ import annotations
import jsonpickle
from typing import List
from course import Course

class Courses:
    def __init__(self, courses: List[Course]):
        self.courses = courses
    
    @staticmethod
    def read_from_txt_file(path: str) -> Courses:
        courses = []
        with open(path, 'r') as courses_file:
            for line in courses_file:
                if not line.strip():
                    continue
                elements = line.split()
                crn = int(elements[0])
                semester = elements[1]
                year = int(elements[2])
                if len(elements) > 3:
                    description = ' '.join(elements[3: ])
                else:
                    description = None
                course = Course(crn, semester, year, description)
                courses.append(course)
        return Courses(courses)
    
    def save_to_file(self, path: str = 'courses.json'):
        with open(path, 'w') as outfile:
            outfile.write(jsonpickle.encode(self, indent=4)) # type: ignore
    
    @staticmethod
    def read_from_json(path: str = 'courses.json') -> Courses:
        with open(path, 'r') as infile:
            return jsonpickle.decode(infile.read()) # type: ignore
    
    def get_all_availability(self):
        for course in self.courses:
            course.get_availability()