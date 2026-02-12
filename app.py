from fastapi import FastAPI
import uvicorn
from scripts.config import Service

app = FastAPI()


if __name__ == '__main__':
    uvicorn.run("main:app", host=Service.host, port=Service.port)

