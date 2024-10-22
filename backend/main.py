# main.py
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect # type: ignore
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import asyncio
from swarm import Swarm, Agent # type: ignore
import nest_asyncio # type: ignore

# Apply nest_asyncio
nest_asyncio.apply()

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

def transfer_to_code_agent():
   """Call this function to transfer to the execute_command_agent"""
   return code_agent

triage_agent = Agent(
    name="Triage Agent",
    instructions=triage_instructions,
    functions=[transfer_to_code_agent, transfer_to_web_agent],
    model=MODEL,
)

web_agent = Agent(
    name="Web Agent",
    instructions=web_instructions,
    functions=[
        tavily_search, 
        get_video_transcript, 
        get_website_text_content, 
        save_to_md, 
        get_all_urls, 
        generate_research_report
    ],
    model=MODEL,
)

code_agent = Agent(
    name="Code Agent",
    instructions=code_instructions,
    functions=[execute_command, read_file, install_package, run_python_script, transfer_back_to_triage],
    model=MODEL,
)

# Append functions to agents
triage_agent.functions.extend([transfer_to_code_agent, transfer_to_web_agent])
web_agent.functions.extend([transfer_back_to_triage])
code_agent.functions.extend([transfer_back_to_triage])

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
    agent = triage_agent

    try:
        while True:
            data = await websocket.receive_json()
            message = data['message']
            history = data.get('history', [])

            # Convert history to the format expected by the Swarm client
            messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]
            messages.append({"role": "user", "content": message})

            async def process_stream():
                stream = client.run(agent=agent, messages=messages, stream=True, debug=True)
                current_agent_name = None
                for chunk in stream:
                    if isinstance(chunk, dict):
                        if 'sender' in chunk and chunk['sender'] != current_agent_name:
                            current_agent_name = chunk['sender']
                            await websocket.send_json({"type": "agent_change", "agent": current_agent_name})
                        if 'content' in chunk and chunk['content'] is not None:
                            await websocket.send_json({"type": "content", "content": chunk['content']})
                    await asyncio.sleep(0)

            # Create a new task for processing the stream
            await asyncio.create_task(process_stream())

            response = client.run(agent=agent, messages=messages)
            agent = response.agent

            await websocket.send_json({"type": "end", "agent": agent.name})

    except WebSocketDisconnect:
        print("WebSocket disconnected")

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)