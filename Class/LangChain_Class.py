from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from Class.OptaPy_Class import Room, Timeslot, Lesson
from datetime import datetime

import requests
import uuid

URL = "https://www.pilou.org/ask/ai"
AUTHORIZATION_TOKEN = "yR$4NJbjaVkiWdnsJS88mxYd4EqLnaW9XQU39FdD$fTbf*4g^nXK%6vRz9Sk"

HEADERS = {
    "Authorization": f"Bearer {AUTHORIZATION_TOKEN}",
    "Content-Type": "application/json"
}

class MistralCustom:
    def __init__(self, endpoint: str, headers: dict):
        self.endpoint = endpoint
        self.headers = headers

    def __call__(self, prompt: str) -> str:
        data = {
            "model": "mixtral",
            "prompt": prompt,
        }
        response = requests.post(self.endpoint, json=data, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("message", "no answer")
        else:
            return "Failed to get response from the server"

class Timeslot_Langchain(BaseModel):
    day_of_week: str = Field(description="Day of the week")
    start_time: str = Field(description="Start time of the timeslot with the format DD/MM/YYYY HH:MM")
    end_time: str = Field(description="End time of the timeslot with the format DD/MM/YYYY HH:MM")

class Lesson_Langchain(BaseModel):
    subject: str = Field(description="Subject of the lesson")
    teacher: str = Field(description="Teacher of the lesson")
    student_group: str = Field(description="Student group of the lesson")

class Room_Langchain(BaseModel):
    name: str = Field(description="Name of the room")

class Timeslot_List_Langchain(BaseModel):
    slots: list[Timeslot_Langchain] = Field(description="List of timeslots")

class Lesson_List_Langchain(BaseModel):
    lessons: list[Lesson_Langchain] = Field(description="List of lessons")

class Room_List_Langchain(BaseModel):
    rooms: list[Room_Langchain] = Field(description="List of rooms")

class OptimizationRequest(BaseModel):
    optimization_request: bool = Field(description="Check if the request is an optimization request")

model = MistralCustom(URL, HEADERS)

def check_optimization_request(query: str) -> bool:
    parser = JsonOutputParser(pydantic_object=OptimizationRequest)
    prompt = PromptTemplate(
        template="Check if the request is an planning optimization request.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model | parser
    return chain.invoke(query)['optimization_request']

def setup_model():
    """
    Setup the LLM model.
    """
    return ChatOpenAI(
        model="gpt-4o-2024-05-13", temperature=0, api_key='sk-proj-HoooFFr01ckgehZEDfuaT3BlbkFJ6zxlrwFkfQuYRVYCOwRQ'
    )

model = setup_model()

def generate_timeslot(query: str):
    parser = JsonOutputParser(pydantic_object=Timeslot_List_Langchain)
    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model | parser
    return chain.invoke(query)

def generate_lesson(query: str):
    parser = JsonOutputParser(pydantic_object=Lesson_List_Langchain)
    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model | parser
    return chain.invoke(query)

def generate_room(query: str):
    parser = JsonOutputParser(pydantic_object=Room_List_Langchain)
    prompt = PromptTemplate(
            template="Answer the user query.\n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
    chain = prompt | model | parser
    return chain.invoke(query)

def generate_timeslot_from_json(json_data: dict) -> Timeslot:
    start_time = datetime.strptime(json_data["start_time"], "%d/%m/%Y %H:%M").time()
    end_time = datetime.strptime(json_data["end_time"], "%d/%m/%Y %H:%M").time()
    return Timeslot(
        id = str(uuid.uuid4()),
        day_of_week = json_data["day_of_week"],
        start_time = start_time,
        end_time = end_time
    )
        
def generate_lesson_from_json(json_data: dict) -> Lesson:
    return Lesson(
        id = str(uuid.uuid4()),
        subject = json_data["subject"],
        teacher = json_data["teacher"],
        student_group = json_data["student_group"]
    )

def generate_room_from_json(json_data: dict) -> Room:
    return Room(
        id = str(uuid.uuid4()),
        name = json_data["name"]
    )


def generate_objects(MAIN_QUERY: str) -> list:
    # MAIN_QUERY = "In my school there are rooms 201, 202, 203. I have 3 lessons: Math, Physics, Chemistry. I have 3 timeslots: Monday 8:30-9:30, Monday 9:30-10:30, Monday 10:30-11:30. I want to assign Math to room 201, Physics to room 202, Chemistry to room 203."
    print("-- TIMESLOT -- ")
    query_timeslot = MAIN_QUERY
    date_of_today = datetime.now().strftime("%d/%m/%Y")
    prompt_footer = f"\n--\nIf in the query above the day of the week is not specified, you can create any type of day of the week accordingly to date of today : {date_of_today}. If the start time and end time are not specified, you can create any type of time with the format DD/MM/YYYY HH:MM between 8:00 - 12:00 and 13:00 - 19:00. Timeslots are 1 hour long each by default."
    query_timeslot = query_timeslot + prompt_footer
    timeslot_langchain = generate_timeslot(query=query_timeslot)

    timeSlotsList: list[Timeslot] = []
    first_key = next(iter(timeslot_langchain))
    for slot in timeslot_langchain[first_key]:
        timeSlotsList.append(generate_timeslot_from_json(slot))
    print(timeslot_langchain)
    
    print("LESSON")
    prompt_footer = "\n--\nIf in the query above, you don't specify the teacher and the student group, you can create any type of teacher and student group."
    query_lesson = MAIN_QUERY + prompt_footer
    lesson_langchain = generate_lesson(query=query_lesson)

    lessonsList: list[Lesson] = []
    first_key = next(iter(lesson_langchain))
    for lesson in lesson_langchain[first_key]:
        lessonsList.append(generate_lesson_from_json(lesson))

    print(lesson_langchain)
    print("ROOM")
    prompt_footer = "\n--\nIf in the query above, you don't specify the room, you can create any type of room with the name you want from 100 to 600, only if needed."
    query_room = MAIN_QUERY + prompt_footer
    room_langchain = generate_room(query=query_room)
    print(room_langchain)

    roomsList: list[Room] = []
    first_key = next(iter(room_langchain))
    for room in room_langchain[first_key]:
        roomsList.append(generate_room_from_json(room))

    return [
        timeSlotsList,
        lessonsList,
        roomsList
    ]