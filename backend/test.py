import asyncio
import websockets # type: ignore
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            message = input("Enter your message (or 'quit' to exit): ")
            if message.lower() == 'quit':
                break
            
            await websocket.send(message)
            print("Message sent. Waiting for response...")

            while True:
                response = await websocket.recv()
                data = json.loads(response)
                if data['type'] == 'agent_change':
                    print(f"Agent changed to: {data['agent']}")
                elif data['type'] == 'content':
                    print(data['content'], end='', flush=True)
                elif data['type'] == 'end':
                    print(f"\nResponse ended. Final agent: {data['agent']}")
                    break

asyncio.get_event_loop().run_until_complete(test_websocket())