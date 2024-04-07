from fastapi import FastAPI, HTTPException, Body, Query
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb+srv://batishabhishek07:4xThmBuNcfHbo1Q0@cluster0.zeu0tkn.mongodb.net/")
db = client["cosmocloud"]
collection = db["user"]


class Address(BaseModel):
    city: str
    country: str


class Student(BaseModel):
    name: str
    age: int
    address: Address

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}


@app.post("/students", response_model=dict,status_code=201)
async def create_student(student: Student = Body(...)):
    # Insert the student document into MongoDB
    result = collection.insert_one(student.dict())
    return {"id": str(result.inserted_id)}

@app.get("/students", response_model=dict,status_code=200)
async def list_students(country: str = Query(None), age: int = Query(None)):
    # Prepare filter based on provided query parameters
    filter_params = {}
    if country:
        filter_params["address.country"] = country
    if age:
        filter_params["age"] = {"$gte": age}

    # Fetch students based on filters
    students = list(collection.find(filter_params, {"_id": 0}))

    return {"data": students}


@app.get("/students/{id}", response_model=Student,status_code=200)
async def get_student(id: str):
    # Retrieve student from MongoDB by ID
    student = collection.find_one({"_id": ObjectId(id)})
    if student:
        student["id"] = str(student.pop("_id"))  # Change _id to id
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")


@app.patch("/students/{id}",status_code=204)
async def update_student(id: str, student: Student = Body(...)):
    # Update student in MongoDB by ID
    result = collection.update_one({"_id": ObjectId(id)}, {"$set": student.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return None


@app.delete("/students/{id}",status_code=204)
async def delete_student(id: str):
    # Delete student from MongoDB by ID
    result = collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
