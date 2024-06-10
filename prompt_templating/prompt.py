import requests

URL = "https://www.pilou.org/ask/ai"
AUTHORIZATION_TOKEN = "yR$4NJbjaVkiWdnsJS88mxYd4EqLnaW9XQU39FdD$fTbf*4g^nXK%6vRz9Sk"

HEADERS = {
    "Authorization": f"Bearer {AUTHORIZATION_TOKEN}",
    "Content-Type": "application/json",
}

prompt_template = '''**Optimization Problem Description:**
{DESCRIPTION}

#SOME FUNDAMENTAL RULES
When you answer, do not say hello, hi or any kind of greetings. Do not introduce yourself. Do not tell what task you are doing. Just be factual and nothing more.

### Problem Verification

**Problem Identification:**
   - Check if the given description corresponds to an optimization problem. If not, respond: "The provided request does not fit with a planning problem".
   - If the optimization problem is incomplete, respond: "The described optimization problem needs further details to be solved: ..." and list the missing information.

**Information Extraction:**
   - If an optimization problem is identified, extract the following elements:
     - **Decision Variables:** Identify the decision variables.
     - **Objective Function:** Identify the objective function to be optimized.
     - **Constraints:** Identify the constraints of the problem.
     - **Data and Parameters:** Identify the necessary data and parameters.

**OptaPy Source Code Generation:**
   - Generate the complete source code to solve the problem with OptaPy.

### Example Response if the Problem is Complete:

```python
from optapy import problem_fact, planning_id

@problem_fact
class Room:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    @planning_id
    def get_id(self):
        return self.id

    def __str__(self):
        return f"Room(id={self.id}, name={self.name})"

@problem_fact
class Timeslot:
    def __init__(self, id, day_of_week, start_time, end_time):
        self.id = id
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time

    @planning_id
    def get_id(self):
        return self.id

    def __str__(self):
        return (
                f"Timeslot("
                f"id={self.id}, "
                f"day_of_week={self.day_of_week}, "
                f"start_time={self.start_time}, "
                f"end_time={self.end_time})"
        )

from optapy import planning_entity, planning_variable

@planning_entity
class Lesson:
    def __init__(self, id, subject, teacher, student_group, timeslot=None, room=None):
        self.id = id
        self.subject = subject
        self.teacher = teacher
        self.student_group = student_group
        self.timeslot = timeslot
        self.room = room

    @planning_id
    def get_id(self):
        return self.id

    @planning_variable(Timeslot, ["timeslotRange"])
    def get_timeslot(self):
        return self.timeslot

    def set_timeslot(self, new_timeslot):
        self.timeslot = new_timeslot

    @planning_variable(Room, ["roomRange"])
    def get_room(self):
        return self.room

    def set_room(self, new_room):
        self.room = new_room

    def __str__(self):
        return (
            f"Lesson("
            f"id={self.id}, "
            f"timeslot={self.timeslot}, "
            f"room={self.room}, "
            f"teacher={self.teacher}, "
            f"subject={self.subject}, "
            f"student_group={self.student_group}"
            f")"
        )

from domain import Lesson, Room
from optapy import constraint_provider, get_class
from optapy.constraint import Joiners
from optapy.score import HardSoftScore

# Constraint Factory takes Java Classes, not Python Classes
LessonClass = get_class(Lesson)
RoomClass = get_class(Room)

@constraint_provider
def define_constraints(constraint_factory):
    return [
        # Hard constraints
        room_conflict(constraint_factory),
        teacher_conflict(constraint_factory),
        student_group_conflict(constraint_factory),
        # Soft constraints are only implemented in the optapy-quickstarts code
    ]

def room_conflict(constraint_factory):
    # A room can accommodate at most one lesson at the same time.
    return constraint_factory
            .forEach(LessonClass)
            .join(LessonClass,
                [
                    # ... in the same timeslot ...
                    Joiners.equal(lambda lesson: lesson.timeslot),
                    # ... in the same room ...
                    Joiners.equal(lambda lesson: lesson.room),
                    # ... and the pair is unique (different id, no reverse pairs) ...
                    Joiners.lessThan(lambda lesson: lesson.id)
                ])
            .penalize("Room conflict", HardSoftScore.ONE_HARD)


def teacher_conflict(constraint_factory):
    # A teacher can teach at most one lesson at the same time.
    return constraint_factory
                .forEach(LessonClass)
                .join(LessonClass,
                        [
                            Joiners.equal(lambda lesson: lesson.timeslot),
                            Joiners.equal(lambda lesson: lesson.teacher),
                    Joiners.lessThan(lambda lesson: lesson.id)
                        ])
                .penalize("Teacher conflict", HardSoftScore.ONE_HARD)

def student_group_conflict(constraint_factory):
    # A student can attend at most one lesson at the same time.
    return constraint_factory
            .forEach(LessonClass)
            .join(LessonClass,
                [
                    Joiners.equal(lambda lesson: lesson.timeslot),
                    Joiners.equal(lambda lesson: lesson.student_group),
                    Joiners.lessThan(lambda lesson: lesson.id)
                ])
            .penalize("Student group conflict", HardSoftScore.ONE_HARD)

from optapy import planning_solution, planning_entity_collection_property,
                   problem_fact_collection_property,
                   value_range_provider, planning_score
from optapy.score import HardSoftScore

def format_list(a_list):
    return ',\n'.join(map(str, a_list))

@planning_solution
class TimeTable:
    def __init__(self, timeslot_list, room_list, lesson_list, score=None):
        self.timeslot_list = timeslot_list
        self.room_list = room_list
        self.lesson_list = lesson_list
        self.score = score

    @problem_fact_collection_property(Timeslot)
    @value_range_provider("timeslotRange")
    def get_timeslot_list(self):
        return self.timeslot_list

    @problem_fact_collection_property(Room)
    @value_range_provider("roomRange")
    def get_room_list(self):
        return self.room_list

    @planning_entity_collection_property(Lesson)
    def get_lesson_list(self):
        return self.lesson_list

    @planning_score(HardSoftScore)
    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score

    def __str__(self):
        return (
            f"TimeTable("
            f"timeslot_list={format_list(self.timeslot_list)},\n"
            f"room_list={format_list(self.room_list)},\n"
            f"lesson_list={format_list(self.lesson_list)},\n"
            f"score={str(self.score.toString()) if self.score is not None else 'None'}"
            f")"
        )

from datetime import time

def generate_problem():
    timeslot_list = [
        Timeslot(1, "MONDAY", time(hour=8, minute=30), time(hour=9, minute=30)),
        Timeslot(2, "MONDAY", time(hour=9, minute=30), time(hour=10, minute=30)),
        Timeslot(3, "MONDAY", time(hour=10, minute=30), time(hour=11, minute=30)),
        Timeslot(4, "MONDAY", time(hour=13, minute=30), time(hour=14, minute=30)),
        Timeslot(5, "MONDAY", time(hour=14, minute=30), time(hour=15, minute=30)),
        Timeslot(6, "TUESDAY", time(hour=8, minute=30), time(hour=9, minute=30)),
        Timeslot(7, "TUESDAY", time(hour=9, minute=30), time(hour=10, minute=30)),
        Timeslot(8, "TUESDAY", time(hour=10, minute=30), time(hour=11, minute=30)),
        Timeslot(9, "TUESDAY", time(hour=13, minute=30), time(hour=14, minute=30)),
        Timeslot(10, "TUESDAY", time(hour=14, minute=30), time(hour=15, minute=30)),
    ]
    room_list = [
        Room(1, "Room A"),
        Room(2, "Room B"),
        Room(3, "Room C")
    ]
    lesson_list = [
        Lesson(1, "Math", "A. Turing", "9th grade"),
        Lesson(2, "Math", "A. Turing", "9th grade"),
        Lesson(3, "Physics", "M. Curie", "9th grade"),
        Lesson(4, "Chemistry", "M. Curie", "9th grade"),
        Lesson(5, "Biology", "C. Darwin", "9th grade"),
        Lesson(6, "History", "I. Jones", "9th grade"),
        Lesson(7, "English", "I. Jones", "9th grade"),
        Lesson(8, "English", "I. Jones", "9th grade"),
        Lesson(9, "Spanish", "P. Cruz", "9th grade"),
        Lesson(10, "Spanish", "P. Cruz", "9th grade"),
        Lesson(11, "Math", "A. Turing", "10th grade"),
        Lesson(12, "Math", "A. Turing", "10th grade"),
        Lesson(13, "Math", "A. Turing", "10th grade"),
        Lesson(14, "Physics", "M. Curie", "10th grade"),
        Lesson(15, "Chemistry", "M. Curie", "10th grade"),
        Lesson(16, "French", "M. Curie", "10th grade"),
        Lesson(17, "Geography", "C. Darwin", "10th grade"),
        Lesson(18, "History", "I. Jones", "10th grade"),
        Lesson(19, "English", "P. Cruz", "10th grade"),
        Lesson(20, "Spanish", "P. Cruz", "10th grade"),
    ]
    lesson = lesson_list[0]
    lesson.set_timeslot(timeslot_list[0])
    lesson.set_room(room_list[0])

    return TimeTable(timeslot_list, room_list, lesson_list)
```
'''

prompt_template_2 = '''**Optimization Problem Description:**
{DESCRIPTION}

#SOME FUNDAMENTAL RULES
When you answer, do not say hello, hi or any kind of greetings. Do not introduce yourself. Do not tell what task you are doing. Just be factual and nothing more.
IMPORTANT: IF THE PROBLEM IS NOT AN OPTIMISATION PROBLEM, DO NOT GIVE AN ANSWER TO IT. JUST SAY "The provided request does not fit with a planning problem." AND NOTHING MORE
IMPORTANT: IF THE PROBLEM IS AN OPTIMISATION PROBLEM, STRICTLY FOLLOW THE RESPONSE TEMPLATE GIVEN. DO NOT ADD ANYTHING MORE. RETURN ONLY THE generate_problem() FUNCTION

### Problem Verification

**Problem Identification:**
   - Check if the given description corresponds to an optimization problem. If not, respond: "The provided request does not fit with a planning problem".
   - If the optimization problem is incomplete, respond: "The described optimization problem needs further details to be solved: ..." and list the missing information.

**Information Extraction:**
   - If an optimization problem is identified, extract the following elements:
     - **Decision Variables:** Identify the decision variables.
     - **Objective Function:** Identify the objective function to be optimized.
     - **Constraints:** Identify the constraints of the problem.
     - **Data and Parameters:** Identify the necessary data and parameters.

**OptaPy Source Code Generation:**
   - Generate the generate_problem() function to solve the problem with OptaPy.

### Example Response if the Problem is Complete:

```python
from datetime import time

def generate_problem():
    timeslot_list = [
        Timeslot(1, "MONDAY", time(hour=8, minute=30), time(hour=9, minute=30)),
        Timeslot(2, "MONDAY", time(hour=9, minute=30), time(hour=10, minute=30)),
        Timeslot(3, "MONDAY", time(hour=10, minute=30), time(hour=11, minute=30)),
        Timeslot(4, "MONDAY", time(hour=13, minute=30), time(hour=14, minute=30)),
        Timeslot(5, "MONDAY", time(hour=14, minute=30), time(hour=15, minute=30)),
        Timeslot(6, "TUESDAY", time(hour=8, minute=30), time(hour=9, minute=30)),
        Timeslot(7, "TUESDAY", time(hour=9, minute=30), time(hour=10, minute=30)),
        Timeslot(8, "TUESDAY", time(hour=10, minute=30), time(hour=11, minute=30)),
        Timeslot(9, "TUESDAY", time(hour=13, minute=30), time(hour=14, minute=30)),
        Timeslot(10, "TUESDAY", time(hour=14, minute=30), time(hour=15, minute=30)),
    ]
    room_list = [
        Room(1, "Room A"),
        Room(2, "Room B"),
        Room(3, "Room C")
    ]
    lesson_list = [
        Lesson(1, "Math", "A. Turing", "9th grade"),
        Lesson(2, "Math", "A. Turing", "9th grade"),
        Lesson(3, "Physics", "M. Curie", "9th grade"),
        Lesson(4, "Chemistry", "M. Curie", "9th grade"),
        Lesson(5, "Biology", "C. Darwin", "9th grade"),
        Lesson(6, "History", "I. Jones", "9th grade"),
        Lesson(7, "English", "I. Jones", "9th grade"),
        Lesson(8, "English", "I. Jones", "9th grade"),
        Lesson(9, "Spanish", "P. Cruz", "9th grade"),
        Lesson(10, "Spanish", "P. Cruz", "9th grade"),
        Lesson(11, "Math", "A. Turing", "10th grade"),
        Lesson(12, "Math", "A. Turing", "10th grade"),
        Lesson(13, "Math", "A. Turing", "10th grade"),
        Lesson(14, "Physics", "M. Curie", "10th grade"),
        Lesson(15, "Chemistry", "M. Curie", "10th grade"),
        Lesson(16, "French", "M. Curie", "10th grade"),
        Lesson(17, "Geography", "C. Darwin", "10th grade"),
        Lesson(18, "History", "I. Jones", "10th grade"),
        Lesson(19, "English", "P. Cruz", "10th grade"),
        Lesson(20, "Spanish", "P. Cruz", "10th grade"),
    ]
    lesson = lesson_list[0]
    lesson.set_timeslot(timeslot_list[0])
    lesson.set_room(room_list[0])

    return TimeTable(timeslot_list, room_list, lesson_list)
```
'''


def get_problem_code(problem):
    prompt = prompt_template_2.replace("{DESCRIPTION}", problem)

    data = {
        "model": "mixtral",
        "prompt": prompt,
    }

    response = requests.post(url=URL, headers=HEADERS, json=data)
    message = response.json()['message']

    # Good answer of an optimisation problem
    if "```python" in message:
        start_pos = message.find("```python") + len("```python")
        end_pos = message.find("```", start_pos)

        # Extract the code block
        extracted_code = message[start_pos:end_pos].strip()

        return True, extracted_code

    return False, message.split(".")[0]


PROBLEM = '''We have two projects (P1 & P2) with dependent tasks and limited resources. 
Each task has a specific duration and required resources. We need to schedule these tasks to minimize the total completion time.
Tasks:
- P1: Task A (3 days, 2 developers), Task B (2 days, 1 developer, depends on A), Task C (4 days, 1 developer).
- P2: Task D (5 days, 3 developers), Task E (2 days, 2 developers, depends on D).
Available resources: 3 developers.'''

PROBLEM_2 = '''In my school there are rooms 201, 202, 203. 
I have 3 lessons: Math, Physics, Chemistry. 
I have 3 timeslots: Monday 8:30-9:30, Monday 9:30-10:30, Monday 10:30-11:30. 
I want to assign Math to room 201, Physics to room 202, Chemistry to room 203.'''

FALSE_PROBLEM = '''How many people were on the Titanic ?'''
FALSE_PROBLEM_2 = '''Give me the recipe of the pudding'''
FALSE_PROBLEM_3 = '''Tell me something funny'''

answer = get_problem_code(FALSE_PROBLEM_3)
print(answer[1])
