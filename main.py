from fastapi import FastAPI # Framework
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Tea(BaseModel):
    id: int
    name: str
    origin: str
    
teas : List[Tea] = []

# Decorators is basically superpowers our functions
@app.get("/") # Decorators 1
def read_root():
    return {"message": "Welcome to the Tea API!"}


@app.get("/teas")
def get_teas():
    return teas

@app.post("/teas")
def add_tea(tea: Tea):
    teas.append(tea)
    return {"message": "Tea added successfully!", "teaAdded": tea}

@app.put("teas/{tea_id}")
def update_tea(tea_id: int, updated_tea: Tea):
    for index, tea in enumerate(teas):
        if tea.id == tea_id:
            teas[index] = updated_tea
            return {"message": "Tea updated successfully!", "updatedTea": updated_tea}
    return {"error": "Tea not found!"}


@app.delete("/teas/{tea_id}")
def delete_tea(tea_id: int):
    for index, tea in enumerate(teas):
        if tea.id == tea_id:
            delete_tea = teas.pop(index)
            return {"message": "Tea deleted successfully!", "deletedTea": delete_tea}
    return {"error": "Tea not found!"}