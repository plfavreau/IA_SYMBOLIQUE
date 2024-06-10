from Class.OptaPy_Class import Lesson, TimeTable
from Class.LangChain_Class import generate_objects
from optapy import constraint_provider, solver_manager_create
from optapy.types import Joiners, HardSoftScore, SolverConfig, Duration
from ipysheet import sheet, cell
from ipywidgets import Tab
import random
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


def generate_problem(timeslot_list, room_list, lesson_list):
    lesson = lesson_list[0]
    lesson.set_timeslot(timeslot_list[0])
    lesson.set_room(room_list[0])

    return TimeTable(timeslot_list, room_list, lesson_list)

def solver(prompt):
    solver_config = SolverConfig().withEntityClasses(Lesson) \
        .withSolutionClass(TimeTable) \
        .withConstraintProviderClass(define_constraints) \
        .withTerminationSpentLimit(Duration.ofSeconds(30))
    time_slot_list, lesson_list, room_list = generate_objects(prompt)
    solution = generate_problem(time_slot_list, room_list, lesson_list)
    solution.set_student_group_and_teacher_list()

    cell_map = dict()
            
    def update_table(final_best_solution, cell_map):
        global timetable
        global solution
        solution = final_best_solution
        unassigned_lessons = []
        clear_cell_set = set()
        
        for (_, table_map) in cell_map.items():
            for (key, cell) in table_map.items():
                clear_cell_set.add(cell)
                
        for lesson in solution.lesson_list:
            if lesson.timeslot is None or lesson.room is None:
                unassigned_lessons.append((lesson, clear_cell_set))
            else:
                update_lesson_in_table(lesson, clear_cell_set, cell_map)
                
        for cell in clear_cell_set:
            cell.value = ""
            cell.style["backgroundColor"] = "white"
                
        for (table_name, table_map) in cell_map.items():
            for (key, cell) in table_map.items():
                cell.send_state()
    def update_lesson_in_table(lesson, clear_cell_set, cell_map):
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
        
    def create_table(table_name, solution, columns, name_map, cell_map):
        out = sheet(rows=len(solution.timeslot_list) + 1, columns=len(columns) + 1)
        header_color = "#22222222"
        cell(0, 0, read_only=True, background_color=header_color)

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

    by_room_table = create_table('room', solution, solution.room_list, lambda room: room.name, cell_map)
    by_teacher_table = create_table('teacher', solution, solution.teacher_list, lambda teacher: teacher, cell_map)
    by_student_group_table = create_table('student_group', solution, solution.student_group_list,
                                        lambda student_group: student_group, cell_map)

    #solver_manager.solveAndListen(0, lambda the_id: solution, on_best_solution_changed)
    solver_job = solver_manager.solve(0, solution)
    final_best_solution = solver_job.getFinalBestSolution()

    update_table(final_best_solution, cell_map)



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
    return room_markdown, teacher_markdown, student_group_markdown

