
import os
java_home = os.environ.get('JAVA_HOME', None)
if not java_home:
    java_path = 'C:\\Program Files\\OpenLogic\\jdk-11.0.22.7-hotspot\\bin'
    java_path = 'G:\\Program Files\\Java\\jre1.8.0_261\\bin'
    os.environ['JAVA_HOME'] = java_path
    print(java_path)
else:
    print("ERROR")
    print(java_home)

from fastapi import FastAPI, Request
from prompt_templating.prompt import get_problem_code
from utils import solver

app = FastAPI()

@app.get("/")
async def main(request: Request):
    data = await request.json()
    problem = data.get("text")
    answer = get_problem_code(problem)
    if not answer[0]:
        return {"error": answer[1]}
    return {"code": answer[1]}
    



if __name__ == "__main__":
    MAIN_QUERY = "In my school there are rooms 201, 202, 203. I have 3 lessons: Math, Physics, Chemistry. I have 3 timeslots: Monday 8:30-9:30, Monday 9:30-10:30, Monday 10:30-11:30. I want to assign Math to room 201, Physics to room 202, Chemistry to room 203."
    solver(MAIN_QUERY)