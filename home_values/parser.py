from bs4 import BeautifulSoup
# pip install beautifulsoup4


def parse(markup):
    soup = BeautifulSoup(markup, "html.parser")

    courses = soup.select(".calendar-event")

    course_info = "Course Info\n"

    for course in courses:
        if "Python" in course.h1.text:
            # this is needed at the moment because of the "invisible" text coming through
            course_info += course.h1.text + "\n"
            course_info += course.h2.text + "\n"
            course_info += "\n"

    return course_info
