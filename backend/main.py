# backend/main.py

import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import asyncio
from swarm import Swarm, Agent
import nest_asyncio

# Apply nest_asyncio
nest_asyncio.apply()

from tools import *
from instructions import *
from agent_descriptions import agent_descriptions  # Import shared agent descriptions

app = FastAPI()

client = Swarm()

MODEL = "gpt-4o-mini"

# Define transfer functions
def transfer_back_to_triage():
    """Call this function to transfer back to the triage_agent."""
    return triage_agent

def transfer_to_web_agent():
    """Call this function to transfer to the web_agent."""
    return web_agent

def transfer_to_code_agent():
    """Call this function to transfer to the code_agent."""
    return code_agent

def transfer_to_reasoning_agent():
    """Call this function to transfer to the reasoning_agent."""
    return reasoning_agent

def transfer_to_image_agent():
    """Call this function to transfer to the image_agent."""
    return image_agent

def transfer_to_weather_agent():
    """Call this function to transfer to the weather_agent."""
    return weather_agent

def transfer_to_make_agent():
    """Call this function to transfer to the make_agent."""
    return make_agent

def transfer_to_research_agent():
    """Call this function to transfer to the research_agent."""
    return research_agent

def transfer_to_notion_agent():
    """Call this function to transfer to the notion_agent."""
    return notion_agent

# List all transfer functions
transfer_functions = [
    transfer_to_code_agent,
    transfer_to_web_agent,
    transfer_to_reasoning_agent,
    transfer_to_image_agent,
    transfer_to_weather_agent,
    transfer_to_make_agent,
    transfer_to_research_agent,
    transfer_to_notion_agent,
    transfer_back_to_triage
]

# Function to create agents
def create_agent(name, instructions, specific_functions):
    return Agent(
        name=name,
        instructions=instructions + agent_descriptions,
        functions=specific_functions + transfer_functions,
        model=MODEL,
    )

# Create agents
triage_agent = create_agent(
    name="Triage Agent",
    instructions=triage_instructions,
    specific_functions=[]
)

web_agent = create_agent(
    name="Web Agent",
    instructions=web_instructions,
    specific_functions=[
        tavily_search,
        get_video_transcript,
        get_website_text_content,
        save_to_md,
        get_all_urls,
        generate_research_report
    ]
)

code_agent = create_agent(
    name="Code Agent",
    instructions=code_instructions,
    specific_functions=[
        execute_command,
        read_file,
        install_package,
        run_python_script
    ]
)

reasoning_agent = create_agent(
    name="Reasoning Agent",
    instructions=reasoning_instructions,
    specific_functions=[
        reason_with_o1
    ]
)

image_agent = create_agent(
    name="Image Agent",
    instructions=image_instructions,
    specific_functions=[
        analyze_image,
        generate_image
    ]
)

weather_agent = create_agent(
    name="Weather Agent",
    instructions=weather_instructions,
    specific_functions=[
        get_current_weather
    ]
)

make_agent = create_agent(
    name="Make Agent",
    instructions=make_instructions,
    specific_functions=[
        send_to_make
    ]
)

research_agent = create_agent(
    name="Research Agent",
    instructions=research_instructions,
    specific_functions=[
        fetch_report,
        run_async,
        generate_research_report
    ]
)

notion_agent = create_agent(
    name="Notion Agent",
    instructions=notion_instructions,
    specific_functions=[
        search_notion,
        create_notion_page,
        get_notion_page_content,
        update_notion_page
    ]
)

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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
