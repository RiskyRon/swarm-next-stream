# main.py
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect # type: ignore
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import asyncio
from swarm import Swarm, Agent # type: ignore

from tools import *
from instructions import *

app = FastAPI()

client = Swarm()

MODEL = "gpt-4o-mini"

def transfer_back_to_triage():
    """Call this function to transfer back to the triage_agent."""
    return triage_agent

def transfer_to_web_agent():
   """Call this function to transfer to the web_agent."""
   return web_agent

def transfer_to_execute_command_agent():
   """Call this function to transfer to the execute_command_agent"""
   return execute_command_agent

triage_agent = Agent(
    name="Triage Agent",
    instructions=triage_instructions,
    functions=[transfer_to_execute_command_agent, transfer_to_web_agent],
    model=MODEL,
)

web_agent = Agent(
    name="Web Agent",
    instructions=web_instructions,
    functions=[tavily_search, get_video_transcript, get_website_text_content, save_to_md, get_all_urls],
    model=MODEL,
)

execute_command_agent = Agent(
    name="Execute Command Agent",
    instructions=execute_instructions,
    functions=[execute, read_file, transfer_back_to_triage],
    model=MODEL,
)

# Append functions to agents
triage_agent.functions.extend([transfer_to_execute_command_agent, transfer_to_web_agent])
web_agent.functions.extend([transfer_back_to_triage])
execute_command_agent.functions.extend([transfer_back_to_triage])

class Message(BaseModel):
    role: str
    content: str

class ConversationRequest(BaseModel):
    messages: List[Message]

@app.post("/chat")
async def chat(request: ConversationRequest):
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    agent = triage_agent
    response = client.run(agent=agent, messages=messages)
    return {"response": response.messages[-1]["content"], "agent": response.agent.name}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    messages = []
    agent = triage_agent

    try:
        while True:
            data = await websocket.receive_text()
            messages.append({"role": "user", "content": data})

            async def stream_response():
                stream = client.run(agent=agent, messages=messages, stream=True, debug=True)
                current_agent_name = None
                for chunk in stream:
                    if isinstance(chunk, dict):
                        if 'sender' in chunk and chunk['sender'] != current_agent_name:
                            current_agent_name = chunk['sender']
                            await websocket.send_json({"type": "agent_change", "agent": current_agent_name})
                        if 'content' in chunk and chunk['content'] is not None:
                            await websocket.send_json({"type": "content", "content": chunk['content']})
                    await asyncio.sleep(0)  # Allow other tasks to run

            await stream_response()

            response = client.run(agent=agent, messages=messages)
            messages = response.messages
            agent = response.agent

            await websocket.send_json({"type": "end", "agent": agent.name})

    except WebSocketDisconnect:
        print("WebSocket disconnected")

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)