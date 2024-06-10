
import os
java_home = os.environ.get('JAVA_HOME', None)
if not java_home:
    java_path = 'C:\\Program Files\\OpenLogic\\jdk-11.0.22.7-hotspot\\bin'
    java_path = 'G:\\Program Files\\Java\\jre1.8.0_261\\bin'
    java_path = "C:\\Users\\Pilou\\.Neo4jDesktop\\distributions\\java\\zulu11.66.19-ca-jdk11.0.20.1\\bin"
    os.environ['JAVA_HOME'] = java_path
    print(java_path)
else:
    print("ERROR")
    print(java_home)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from utils import solver
from Class.LangChain_Class import check_optimization_request

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.post("/")
async def main(request: Request):
    data = await request.json()
    problem = data.get("text")

    if not check_optimization_request(problem):
        return {"error": "The provided request is not a planning optimization problem"}

    answer = solver(problem)
    if not answer:
        return {"error": "No answer"}
    else:
        room_markdown, teacher_markdown, student_group_markdown = answer
        return {"room_markdown": room_markdown, "teacher_markdown": teacher_markdown, "student_group_markdown": student_group_markdown}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    #MAIN_QUERY = "In my school there are rooms 201, 202, 203. I have 3 lessons: Math, Physics, Chemistry. I have 3 timeslots: Monday 8:30-9:30, Monday 9:30-10:30, Monday 10:30-11:30. I want to assign Math to room 201, Physics to room 202, Chemistry to room 203."
    #solver(MAIN_QUERY)