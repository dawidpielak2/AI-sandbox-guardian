from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os

import models
from database import get_db

from router import orchestrator
from file_manager import QUARANTINE_DIR, process_uploaded_file

app = FastAPI(title="Guardian AI - Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    content: str

class ChatRenameRequest(BaseModel):
    title: str

@app.get("/")
def read_root():
    return {"status": "Guardian AI server is running correctly!"}

@app.get("/api/chats")
def get_all_chats(db: Session = Depends(get_db)):
    return db.query(models.Conversation).order_by(models.Conversation.created_at.desc()).all()
@app.get("/api/chats/{chat_id}/messages")

def get_chat_messages(chat_id: int, db: Session = Depends(get_db)):
    return db.query(models.Message).filter(models.Message.conversation_id == chat_id).order_by(models.Message.created_at.asc()).all()
    
@app.post("/api/chats")
def create_new_chat(db: Session = Depends(get_db)):
    new_chat = models.Conversation(title="New chat session")
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

@app.put("/api/chats/{chat_id}")
def rename_chat(chat_id: int, request: ChatRenameRequest, db: Session = Depends(get_db)):
    chat = db.query(models.Conversation).filter(models.Conversation.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat.title = request.title
    db.commit()
    db.refresh(chat)
    return chat

@app.delete("/api/chats/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(models.Conversation).filter(models.Conversation.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db.delete(chat)
    db.commit()
    return {"status": "deleted"}

@app.post("/api/chats/{chat_id}/messages")
def send_message(chat_id: int, request: MessageRequest, db: Session = Depends(get_db)):
    chat = db.query(models.Conversation).filter(models.Conversation.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    user_msg = models.Message(conversation_id=chat_id, role="user", content=request.content)
    db.add(user_msg)
    db.commit()

    db_messages = db.query(models.Message).filter(models.Message.conversation_id == chat_id).all()
    chat_history = [{"role": msg.role, "content": msg.content} for msg in db_messages]

    current_file = None
    db_file = db.query(models.UploadedFile).filter(models.UploadedFile.conversation_id == chat_id).first()
    if db_file:
        current_file = {
            'name': db_file.original_name, 
            'path': db_file.safe_path, 
            'size': db_file.file_size
        }

    final_output = orchestrator(chat_history, QUARANTINE_DIR, current_file)

    ai_msg = models.Message(conversation_id=chat_id, role="assistant", content=final_output)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return ai_msg

@app.post("/api/chats/{chat_id}/upload")
def upload_file(chat_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    chat = db.query(models.Conversation).filter(models.Conversation.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(file.file.read())

    file_data = process_uploaded_file(temp_path)
    
    if file_data.get("error"):
        raise HTTPException(status_code=400, detail=file_data["error"])
    
    new_file = models.UploadedFile(
        conversation_id=chat_id,
        original_name=file_data['name'],
        safe_path=file_data['path'],
        file_size=file_data['size'],
        size_category=file_data['size_label']
    )
    db.add(new_file)
    
    system_msg = models.Message(
        conversation_id=chat_id, 
        role="system", 
        content=f"System Note: The file '{file_data['name']}' is securely loaded at '{file_data['path']}'."
    )
    db.add(system_msg)
    
    db.commit()
    return {"status": "File uploaded and processed successfully", "file_data": file_data}