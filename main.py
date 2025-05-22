import os

import bcrypt
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import inspect

from ai_agent import *
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

load_dotenv()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

app = FastAPI()


class InputSchema(BaseModel):
    user_id: str = Field(..., description="User ID")
    password: str = Field(..., description="Password")
    query: str = Field(..., description="Query string")


class OutputSchema(BaseModel):
    casual_response: str = Field(..., description="Casual response to the query from AI")
    formal_response: str = Field(..., description="Formal response to the query from AI")


class LoginSchema(BaseModel):
    username: str = Field(..., description="Username"),
    password: str = Field(..., description="Password"),


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


@app.post('/generate', response_model=OutputSchema)
async def generate(input_schema: InputSchema, db: db_dependency):
    query = input_schema.query
    agent_response = run_agent(user_query=query)

    db_prompts = models.Prompts(
        user_id=input_schema.user_id,
        query=input_schema.query,
        casual_response=agent_response["casual_response"],
        formal_response=agent_response["formal_response"],
        created_at=datetime.now()
    )
    db.add(db_prompts)
    db.commit()
    db.refresh(db_prompts)

    return {"casual_response": agent_response["casual_response"],
            "formal_response": agent_response["formal_response"]}


@app.get('/history/{user_id}')
async def get_history(data: LoginSchema, db: db_dependency):
    history = db.query(models.Prompts).filter(models.Prompts.user_id == data.username).all()
    user = db.query(models.Users).filter(models.Users.username == data.username).first()
    if bcrypt.checkpw(data.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        return {"history": [object_as_dict(h) for h in history]}
    return {"history": []}


@app.post('/login')
def login(data: LoginSchema, db: db_dependency):
    user = db.query(models.Users).filter(models.Users.username == data.username).first()
    if user:
        user_info = {
            "id": user.id,
            "username": user.username,
            "password": user.hashed_password
        }
        if bcrypt.checkpw(data.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            return JSONResponse(status_code=200, content={"message": "Login successful", "user": user_info})
        else:
            return JSONResponse(status_code=401, content={"detail": "Incorrect password"})

    return JSONResponse(status_code=404, content={"detail": "User not found"})


@app.post('/signup')
def signup(data: LoginSchema, db: db_dependency):
    user = db.query(models.Users).filter(models.Users.username == data.username).first()
    if user:
        return JSONResponse(status_code=409, content={"detail": "Username already taken"})
    hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt())
    new_user = models.Users(username=data.username, hashed_password=hashed_password.decode('utf-8'))
    db.add(new_user)
    db.commit()
    return JSONResponse(status_code=200, content={"message": "Signup successful", "user": object_as_dict(new_user)})
