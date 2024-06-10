from optapy.types import SolverConfig, Duration
from ipywidgets import Tab
from ipysheet import sheet, cell, row, column
from optapy import constraint_provider, problem_fact, planning_id, planning_entity, planning_variable, solver_manager_create
import random
"""
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
"""


def pick_color(subject):
    color_list = [
        "#FF6633", "#FFB399", "#FF33FF", "#FFFF99", "#00B3E6", 
        "#E6B333", "#3366E6", "#999966", "#99FF99", "#B34D4D",
        "#80B300", "#809900", "#E6B3B3", "#6680B3", "#66991A", 
        "#FF99E6", "#CCFF1A", "#FF1A66", "#E6331A", "#33FFCC",
        "#66994D", "#B366CC", "#4D8000", "#B33300", "#CC80CC",
        "#66664D", "#991AFF", "#E666FF", "#4DB3FF", "#1AB399",
        "#E666B3", "#33991A", "#CC9999", "#B3B31A", "#00E680", 
        "#4D8066", "#809980", "#E6FF80", "#1AFF33", "#999933",
        "#FF3380", "#CCCC00", "#66E64D", "#4D80CC", "#9900B3", 
        "#E64D66", "#4DB380", "#FF4D4D", "#99E6E6", "#6666FF"
    ]
    
    if not hasattr(pick_color, "subject_color_map"):
        pick_color.subject_color_map = {}
    
    if subject not in pick_color.subject_color_map:
        pick_color.subject_color_map[subject] = random.choice(color_list)
    
    return pick_color.subject_color_map[subject]

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
    
from optapy.types import Joiners, HardSoftScore
from datetime import datetime, date, timedelta

# Trick since timedelta only works with datetime instances
today = date.today()


def within_30_minutes(lesson1, lesson2):
    between = datetime.combine(today, lesson1.timeslot.end_time) - datetime.combine(today, lesson2.timeslot.start_time)
    return timedelta(minutes=0) <= between <= timedelta(minutes=30)


@constraint_provider
def define_constraints(constraint_factory):
    return [
        # Hard constraints
        room_conflict(constraint_factory),
        teacher_conflict(constraint_factory),
        student_group_conflict(constraint_factory),
        # Soft constraints
        teacher_room_stability(constraint_factory),
        teacher_time_efficiency(constraint_factory),
        student_group_subject_variety(constraint_factory)
    ]


def room_conflict(constraint_factory):
    # A room can accommodate at most one lesson at the same time.
    return constraint_factory \
        .for_each(Lesson) \
        .join(Lesson,
              # ... in the same timeslot ...
              Joiners.equal(lambda lesson: lesson.timeslot),
              # ... in the same room ...
              Joiners.equal(lambda lesson: lesson.room),
              # form unique pairs
              Joiners.less_than(lambda lesson: lesson.id)
              ) \
        .penalize("Room conflict", HardSoftScore.ONE_HARD)


def teacher_conflict(constraint_factory):
    # A teacher can teach at most one lesson at the same time.
    return constraint_factory \
        .for_each(Lesson) \
        .join(Lesson,
              Joiners.equal(lambda lesson: lesson.timeslot),
              Joiners.equal(lambda lesson: lesson.teacher),
              Joiners.less_than(lambda lesson: lesson.id)
              ) \
        .penalize("Teacher conflict", HardSoftScore.ONE_HARD)


def student_group_conflict(constraint_factory):
    # A student can attend at most one lesson at the same time.
    return constraint_factory \
        .for_each(Lesson) \
        .join(Lesson,
              Joiners.equal(lambda lesson: lesson.timeslot),
              Joiners.equal(lambda lesson: lesson.student_group),
              Joiners.less_than(lambda lesson: lesson.id)
              ) \
        .penalize("Student group conflict", HardSoftScore.ONE_HARD)


def teacher_room_stability(constraint_factory):
    # A teacher prefers to teach in a single room.
    return constraint_factory \
        .for_each(Lesson) \
        .join(Lesson,
              Joiners.equal(lambda lesson: lesson.teacher),
              Joiners.less_than(lambda lesson: lesson.id)
              ) \
        .filter(lambda lesson1, lesson2: lesson1.room != lesson2.room) \
        .penalize("Teacher room stability", HardSoftScore.ONE_SOFT)


def teacher_time_efficiency(constraint_factory):
    # A teacher prefers to teach sequential lessons and dislikes gaps between lessons.
    return constraint_factory \
        .for_each(Lesson) \
        .join(Lesson,
              Joiners.equal(lambda lesson: lesson.teacher),
              Joiners.equal(lambda lesson: lesson.timeslot.day_of_week)
              ) \
        .filter(within_30_minutes) \
        .reward("Teacher time efficiency", HardSoftScore.ONE_SOFT)


def student_group_subject_variety(constraint_factory):
    # A student group dislikes sequential lessons on the same subject.
    return constraint_factory \
        .for_each(Lesson) \
        .join(Lesson,
              Joiners.equal(lambda lesson: lesson.subject),
              Joiners.equal(lambda lesson: lesson.student_group),
              Joiners.equal(lambda lesson: lesson.timeslot.day_of_week)
              ) \
        .filter(within_30_minutes) \
        .penalize("Student group subject variety", HardSoftScore.ONE_SOFT)

from optapy import planning_solution, planning_entity_collection_property, \
    problem_fact_collection_property, \
    value_range_provider, planning_score


def format_list(a_list):
    return ',\n'.join(map(str, a_list))


@planning_solution
class TimeTable:
    def __init__(self, timeslot_list, room_list, lesson_list, score=None):
        self.timeslot_list = timeslot_list
        self.room_list = room_list
        self.lesson_list = lesson_list
        self.score = score
        
    def set_student_group_and_teacher_list(self):
        self.student_group_list = []
        self.teacher_list = []
        for lesson in self.lesson_list:
            if lesson.teacher not in self.teacher_list:
                self.teacher_list.append(lesson.teacher)
            if lesson.student_group not in self.student_group_list:
                self.student_group_list.append(lesson.student_group)

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
    

def create_time_list(answer_string: str):
    time_list = []
    for line in answer_string.split("\n"):
        if line.startswith("Timeslot"):
            time_list.append(Timeslot(int(line.split(" ")[1][1:]), line.split(" ")[2][1:], line.split(" ")[3][1:], line.split(" ")[4][1:]))
    return time_list

def create_room_list(answer_string: str):
    room_list = []
    for line in answer_string.split("\n"):
        if line.startswith("Room"):
            room_list.append(Room(int(line.split(" ")[1][1:]), line.split(" ")[2][1:]))
    return room_list

def create_lesson_list(answer_string: str):
    lesson_list = []
    for line in answer_string.split("\n"):
        if line.startswith("Lesson"):
            lesson_list.append(Lesson(int(line.split(" ")[1][1:]), line.split(" ")[2][1:], line.split(" ")[3][1:], line.split(" ")[4][1:]))
    return lesson_list

if __name__ == "__main__":

    solver_config = SolverConfig().withEntityClasses(Lesson) \
        .withSolutionClass(TimeTable) \
        .withConstraintProviderClass(define_constraints) \
        .withTerminationSpentLimit(Duration.ofSeconds(30))


    solution = generate_problem()
    solution.set_student_group_and_teacher_list()

    cell_map = dict()

    def on_best_solution_changed(best_solution):
        global timetable
        global solution
        global cell_map
        solution = best_solution
        unassigned_lessons = []
        clear_cell_set = set()
        
        for (table_name, table_map) in cell_map.items():
            for (key, cell) in table_map.items():
                clear_cell_set.add(cell)
            
    def update_table(final_best_solution):
        global timetable
        global solution
        global cell_map
        solution = final_best_solution
        unassigned_lessons = []
        clear_cell_set = set()
        
        for (table_name, table_map) in cell_map.items():
            for (key, cell) in table_map.items():
                clear_cell_set.add(cell)
                
        for lesson in solution.lesson_list:
            if lesson.timeslot is None or lesson.room is None:
                unassigned_lessons.append((lesson, clear_cell_set))
            else:
                update_lesson_in_table(lesson, clear_cell_set)
                
        for cell in clear_cell_set:
            cell.value = ""
            cell.style["backgroundColor"] = "white"
                
        for (table_name, table_map) in cell_map.items():
            for (key, cell) in table_map.items():
                cell.send_state()
    def update_lesson_in_table(lesson, clear_cell_set):
        global cell_map
        x = solution.timeslot_list.index(lesson.timeslot)
        room_column = solution.room_list.index(lesson.room)
        teacher_column = solution.teacher_list.index(lesson.teacher)
        student_group_column = solution.student_group_list.index(lesson.student_group)
        #color = pick_color(lesson.subject)

        room_cell = cell_map['room'][(x + 1, room_column + 1)]
        teacher_cell = cell_map['teacher'][(x + 1, teacher_column + 1)]
        student_group_cell = cell_map['student_group'][(x + 1, student_group_column + 1)]
        
        clear_cell_set.discard(room_cell)
        clear_cell_set.discard(teacher_cell)
        clear_cell_set.discard(student_group_cell)

        room_cell.value = f"{lesson.subject}, {lesson.teacher}, {lesson.student_group}"
        #room_cell.style["backgroundColor"] = color
        room_cell.send_state()

        teacher_cell.value = f"{lesson.room.name}, {lesson.subject}, {lesson.student_group}"
        #teacher_cell.style["backgroundColor"] = color
        teacher_cell.send_state()

        student_group_cell.value = f"{lesson.room.name}, {lesson.subject}, {lesson.teacher}"
        #student_group_cell.style["backgroundColor"] = color
        student_group_cell.send_state()
        
    def create_table(table_name, solution, columns, name_map):
        global cell_map
        out = sheet(rows=len(solution.timeslot_list) + 1, columns=len(columns) + 1)
        header_color = "#22222222"
        cell(0, 0, read_only=True, background_color=header_color)
        header_row = row(0, list(map(name_map, columns)), column_start=1, read_only=True, background_color=header_color)
        timeslot_column = column(0, list(map(lambda timeslot: timeslot.day_of_week[0:3] + " " + str(timeslot.start_time)[0:5], solution.timeslot_list)), row_start=1, read_only=True, background_color=header_color)

        table_cells = dict()
        cell_map[table_name] = table_cells
        for x in range(len(solution.timeslot_list)):
            for y in range(len(columns)):
                table_cells[(x + 1, y + 1)] = cell(x + 1, y + 1, "", read_only=True)
        return out

    def table_to_markdown(table_cells, headers, timeslots):
        # Calculate the max width of each column
        column_widths = [len(header) for header in headers]
        for x in range(1, len(timeslots) + 1):
            for y in range(len(headers)):
                cell_value = table_cells.get((x, y), "")
                if cell_value:
                    value_length = len(cell_value.value.replace('\n', ', '))
                    column_widths[y] = max(column_widths[y], value_length)
        
        def pad_cell(value, width):
            return value + ' ' * (width - len(value))
        
        # Create the markdown table with proper spacing
        markdown = "| " + " | ".join([pad_cell(headers[i], column_widths[i]) for i in range(len(headers))]) + " |\n"
        markdown += "| " + " | ".join(["-" * column_widths[i] for i in range(len(headers))]) + " |\n"
        
        for x in range(1, len(timeslots) + 1):
            row_values = [pad_cell(timeslots[x - 1].day_of_week[0:3] + " " + str(timeslots[x - 1].start_time)[0:5], column_widths[0])]
            for y in range(1, len(headers)):
                cell_value = table_cells.get((x, y), "")
                if cell_value:
                    row_values.append(pad_cell(cell_value.value.replace('\n', ', '), column_widths[y]))
                else:
                    row_values.append(pad_cell("", column_widths[y]))
            markdown += "| " + " | ".join(row_values) + " |\n"
        
        return markdown
    solver_manager = solver_manager_create(solver_config)

    by_room_table = create_table('room', solution, solution.room_list, lambda room: room.name)
    by_teacher_table = create_table('teacher', solution, solution.teacher_list, lambda teacher: teacher)
    by_student_group_table = create_table('student_group', solution, solution.student_group_list,
                                        lambda student_group: student_group)

    #solver_manager.solveAndListen(0, lambda the_id: solution, on_best_solution_changed)
    solver_job = solver_manager.solve(0, solution)
    final_best_solution = solver_job.getFinalBestSolution()

    update_table(final_best_solution)



    tab = Tab()
    tab.children = [by_room_table, by_teacher_table, by_student_group_table]

    tab.set_title(0, 'By Room')
    tab.set_title(1, 'By Teacher')
    tab.set_title(2, 'By Student Group')
    room_markdown = table_to_markdown(cell_map['room'], ['Timeslot'] + [room.name for room in solution.room_list], solution.timeslot_list)
    teacher_markdown = table_to_markdown(cell_map['teacher'], ['Timeslot'] + solution.teacher_list, solution.timeslot_list)
    student_group_markdown = table_to_markdown(cell_map['student_group'], ['Timeslot'] + solution.student_group_list, solution.timeslot_list)

    print("## By Room\n")
    print(room_markdown)
    print("\n## By Teacher\n")
    print(teacher_markdown)
    print("\n## By Student Group\n")
    print(student_group_markdown)
