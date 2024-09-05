from fastapi import FastAPI, File, UploadFile, HTTPException
import pandas as pd
import base64
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error, errorcode
import uuid
from openai import OpenAI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/2")
def read_root():
    return {"message": "Hello2, FastAPI!"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    encoded_content = base64.b64encode(content).decode('utf-8')
    return {"filename": file.filename, "content_type": file.content_type, "content" : encoded_content}

def create_db_connection():
    try:
        connection = mysql.connector.connect(
        host = "",
        user = "",
        password = "",
        database = ""
        )
        return connection
    except Error as e:
        # Print a detailed error message
        print(f"Error connecting to the database: {e}")
        return None
    
conn = create_db_connection()

class newUser(BaseModel):
    username : str
    user_password : str

@app.post("/create_user")
async def create_user(details : newUser):
    username = details.username
    user_password = details.user_password
    user_id = str(uuid.uuid4())
    conn = create_db_connection() 
    if conn is None:
        conn = create_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()
        query = "INSERT INTO users1 (username, user_password, user_id) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, user_password, user_id))
        conn.commit()
        return {"user_id": user_id}
    except Error as e:
        print("error in user creation")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


class AuthenticateDetails(BaseModel):
    username : str
    user_password : str

@app.post("/authenticate_user")
async def authenticate_user(authdetails : AuthenticateDetails):
    username = authdetails.username
    user_password = authdetails.user_password
    conn = create_db_connection()
    if conn is None:
        conn = create_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT user_id FROM users1 WHERE username = %s and user_password = %s"
        cursor.execute(query, (username, user_password))
        result = cursor.fetchone()
        if result is None:
            print("user does not exist")
        else:
            return result
    except:
        print("error with user fetching")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


class taskDetails(BaseModel):
    user_id : str
    task_name : str
    description : str
    todo_date : str

@app.post("/taskdetails")
async def taskdetails(details : taskDetails):
    user_id = details.user_id
    task_name = details.task_name
    description = details.description
    todo_date = details.todo_date
    task_id = str(uuid.uuid4())
    conn = create_db_connection()
    if conn is None:
        conn = create_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor(dictionary=True)
        query = "INSERT INTO task(task_id, user_id, task_name, description, todo_date) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (task_id, details.user_id, details.task_name, details.description, details.todo_date))
        conn.commit()
        return {"message": "Task saved successfully"}
    except Error as e:
        print(f"Error saving task: {e}")
        raise HTTPException(status_code=500, detail="Task saving failed")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

class taskId(BaseModel):
    task_id : str

def get_suggestions(task_id : str):
    conn= create_db_connection()
    if conn is None:
        raise HTTPException(status_code = 500, detail = "Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT description from task where task_id = %s"
        cursor.execute(query, (task_id,))
        result = cursor.fetchone()
        openai.api_key = ''
        task_description = result["description"]
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-3.5-turbo" if you're using the GPT-3.5 model
            messages=[
            {"role": "system", "content": "You are an assistant that provides suggestions, advice, any amazing facts to make the task efficient for user."},
            {"role": "user", "content": f"Here is a task: '{task_description}'. Can you provide five suggestions, advice, any help you can do?"}
            ])
        suggestions = response.choices[0].message.content
        print(suggestions)
        return {"suggestions" : suggestions}

    except Error as e:
        print(f"Error saving task: {e}")
        raise HTTPException(status_code=500, detail="get description failed")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            

@app.post("/taskSuggestions")
async def taskSuggestions(task_id : taskId):
    suggestions = get_suggestions(task_id.task_id)
    return suggestions

class wishtaskdetails(BaseModel):
    
    wish_date : str
    sendto_name : str
    howi_address : str
    wish_topic : str 
    

@app.post("/wishTaskDetails")
async def wishTaskDetails(details : wishtaskdetails):
    wishtask_id = str(uuid.uuid4())
    wish_date = details.wish_date
    sendto_name = details.sendto_name
    howi_address = details.howi_address
    wish_topic = details.wish_topic
    conn = create_db_connection()
    if conn is None:
        raise HTTPException(.....................)
    try:
        cursor = conn.cursor(dictionary = True) 
        query = "INSERT INTO wishtask (wishtask_id, wish_date, sendto_name, howi_address, wish_topic) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (wishtask_id, wish_date, sendto_name, howi_address, wish_topic))
        cursor.commit()
        

#OOPS Practise
# class Car:
#     def __init__(self, make, model):
#         self.make= make
#         self.model= model
#         self.is_running = False
    
#     def start(self):
#         if not self.is_running:
#             self.is_running = True
#             return "started"
#         else:
#             return "already running"
        
#     def stop(self):
#         if self.is_running:
#             self.is_running = False
#             return "stopped"
#         else:
#             return "already stopped"


# car = Car("aluminium","audi")
# print(car.start())  # Outputs: started
# print(car.stop())

# class ElectricCar(Car):
#     def __init__(self, make,model, battery_level=100):
#         super().__init__(make,model)
#         self.battery_level=battery_level

#     def charge(self):
#         self.battery_level=100
#         return "fully charged is "
    
# elec_car = ElectricCar("alum", "audi", 75)
# print(elec_car.start())
# print(elec_car.stop())
# print(elec_car.charge())

# class Animal:
#     def speak(self):
#         raise NotImplementedError("Subclasses must implement this method")


# class Dog(Animal):
#     def speak(self):
#         return "Woof!"


# class Cat(Animal):
#     def speak(self):
#         return "Meow!"


# class Cow(Animal):
#     def speak(self):
#         return "Moo!"


# # Creating a list of different animals
# animals = [Dog(), Cat(), Cow()]

# # Demonstrating polymorphism by calling the speak method on each animal
# for animal in animals:
#     print(animal.speak())


# def inst(carname):
    
#     carname= Dog()
#     print("jack created")
#     print(carname.speak())

# inst("jack")