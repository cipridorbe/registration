from __future__ import annotations
import jsonpickle
from typing import List, Dict
from copy import deepcopy
from course import Course
from time import sleep

class Courses:
    def __init__(self, courses: List[Course]):
        self.courses = courses
    
    @staticmethod
    def read_from_txt_file(path: str, sleep_time=0.5) -> Courses:
        courses = []
        with open(path, 'r') as courses_file:
            for line in courses_file:
                if not line.strip():
                    continue
                elements = line.split()
                crn = int(elements[0])
                semester = elements[1]
                year = int(elements[2])
                name = ' '.join(elements[3: ])
                course = Course(crn, semester, year, name)
                sleep(sleep_time)
                courses.append(course)
        return Courses(courses)
    
    def update_tracked_courses(self, path: str, sleep_time=0.5):
        crns = []
        # Add new
        with open(path, 'r') as courses_file:
            for line in courses_file:
                if not line.strip():
                    continue
                elements = line.split()
                crn = int(elements[0])
                crns.append(crn)
                if self.find_course(crn) is None:
                    semester = elements[1]
                    year = int(elements[2])
                    name = ' '.join(elements[3: ])
                    course = Course(crn, semester, year, name)
                    sleep(sleep_time)
                    self.courses.append(course)
        # Remove old
        for course in self.courses:
            if course.crn not in crns:
                self.courses.remove(course)



    def save_to_file(self, path: str = 'courses.json'):
        with open(path, 'w') as outfile:
            outfile.write(jsonpickle.encode(self, indent=4)) # type: ignore
    
    @staticmethod
    def read_from_json(path: str = 'courses.json') -> Courses:
        with open(path, 'r') as infile:
            return jsonpickle.decode(infile.read()) # type: ignore
    
    def update_all_availability(self, return_changes=True, sleep_time=0.5) -> Dict | None:
        changes = {}
        for course in self.courses:
            changes[course.crn] = {}
            prev = deepcopy(course)
            try:
                course.update_availability()
                sleep(sleep_time)
            except Exception as e:
                print(e)
                continue

            if not return_changes:
                continue

            if prev.waitlist_seats_available != course.waitlist_seats_available:
                changes[course.crn]['waitlist_seats_available'] = (
                    prev.waitlist_seats_available,
                    course.waitlist_seats_available
                )
            
            if prev.seats_available == course.seats_available:
                changes[course.crn]['seats_available'] = (
                    prev.seats_available,
                    course.seats_available
                )
            
            if prev.major_restrictions != course.major_restrictions:
                changes[course.crn]['major_restrictions'] = (
                    prev.major_restrictions,
                    course.major_restrictions
                )
        if return_changes:
            return changes
        else:
            return None
    
    def find_course(self, crn: int) -> Course | None:
        for course in self.courses:
            if course.crn == crn:
                return course
        return None
