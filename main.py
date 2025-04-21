from courses import Courses

def main():
    courses = Courses.read_from_txt_file('courses.txt')
    courses.get_all_availability()
    courses.save_to_file()

if __name__ == '__main__':
    main()