from __future__ import annotations
from typing import List
import requests
from bs4 import BeautifulSoup

class Course:
    def __init__(
            self,
            crn: int,
            semester: str,
            year: int,
            name: str
    ):
        self.crn = crn
        self.semester = semester.lower()
        self.year = year
        self.name = name
        self.url = Course.create_url(crn, semester, year)
        try:
            self.update_availability()
        except Exception as e:
            print(f'course creation error: {e}')
    
    @staticmethod
    def create_url(crn: int, semester: str, year: int) -> str:
        if semester.lower() == 'spring':
            semester_number = '02'
        elif semester.lower() == 'summer':
            semester_number = '05'
        elif semester.lower() == 'fall':
            semester_number = '08'
        else:
            raise Exception(f'Invalid semester for creating url: {semester}')
        url = 'https://oscar.gatech.edu/bprod/bwckschd.p_disp_detail_sched?'
        url += f'term_in={year}{semester_number}&crn_in={crn}'
        return url
    
    def update_availability(self):
        response = requests.get(self.url)
        if response.status_code == 503:
            raise Exception(f"Service Unavailable (503) while accessing: {self.url}")
        elif response.status_code != 200:
            raise Exception(f"HTTP {response.status_code} error while accessing: {self.url}")
        
        soup = BeautifulSoup(response.text, 'html.parser')

        availability = Course.get_seat_availability(soup)
        self.availability = availability
        waitlist_seats_available = availability['waitlist']['remaining'] > 0
        if availability['waitlist']['actual'] > 0:
            # Seats are reserved for waitlist
            seats_available = False
        else:
            # No waitlist. Seats are available if seats remain
            seats_available = availability['seats']['remaining'] > 0
        self.waitlist_seats_available = waitlist_seats_available
        self.seats_available = seats_available

        self.major_restrictions = Course.get_major_restrictions(soup)

    @staticmethod
    def get_seat_availability(soup: BeautifulSoup) -> dict[str, dict[str, int]]:
        info = {}

        summary = 'This layout table is used to present the seating numbers.'
        seat_table = soup.find('table', attrs={'summary': summary})
        rows = seat_table.find_all('tr')

        def get_numbers(row):
            cols = row.find_all('td')
            return {
                'capacity': int(cols[0].text.strip()),
                'actual': int(cols[1].text.strip()),
                'remaining': int(cols[2].text.strip())
            }
        
        info['seats'] = get_numbers(rows[1])
        info['waitlist'] = get_numbers(rows[2])

        return info
    
    @staticmethod
    def get_major_restrictions(soup: BeautifulSoup) -> List[str]:
        restrictions = []

        text = 'Must be enrolled in one of the following Majors:'
        major_line = soup.find(string=lambda s: s and text in s)
        if major_line is None:
            return []
        
        for sibling in major_line.find_all_next(string=True):
            if '\n\xa0 \xa0 \xa0' in sibling.string:
                restrictions.append(sibling.string.strip())
            else:
                break

        return restrictions

    def generate_message(self, changes) -> str | None:
        if not changes:
            return None
        message = self.name
        for key in changes:
            if 'waitlist' in key:
                message += '\n'
                # if before seats were available
                if changes[key][0]:
                    message += 'Waitlist changed from open to closed.'
                else:
                    message += 'Waitlist changed from closed to open.'
            elif 'seats' in key:
                message += '\n'
                # if before seats were available
                if changes[key][0]:
                    message += 'Seats changed from open to closed.'
                else:
                    message += 'Seats changed from closed to open.'
            else:
                message += '\n'
                message += 'Change in major restrictions:\n'
                message += f'before: {changes[key][0]}\n'
                message += f'after: {changes[key][1]}'
        return message
