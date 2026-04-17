from fastapi import FastAPI
import random

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@app.get("/estado_unifila")
def get_status():
    """
        Permite obtener el estado de la unifila 1 = CLOSED, 2= OPEN, 3= HALF-OPEN 
    """
    return random.randint(1,2,3)