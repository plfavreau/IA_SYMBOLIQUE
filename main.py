from fastapi import FastAPI, Request  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402
from Class.LangChain_Class import check_optimization_request  # noqa: E402
from utils import solver  # noqa: E402

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
async def main(request: Request):
    data = await request.json()
    problem = data.get("text")

    if not check_optimization_request(problem):
        return {"error": "The provided request is not a planning optimization problem."}

    answer = solver(problem)
    if not answer:
        return {"error": "No answer"}
    else:
        return JSONResponse(content=answer)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)