from fastapi import FastAPI 

app = FastAPI()

@app.get("/")
def read_root():
    return "siomon"

@app.get("/si")
def read_root():
    return "siomon"