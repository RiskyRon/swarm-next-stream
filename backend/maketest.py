import requests

def send_hello_world():
    url = "https://hook.eu2.make.com/lh4bjyea77m4h8gkv3vqc7vvm0290vwu"
    data = {"message": "Hello, World!"}
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Check if the request was successful
        print("Message sent successfully:", response.json())
    except requests.exceptions.RequestException as e:
        print("Failed to send message:", e)

# Call the function
send_hello_world()
