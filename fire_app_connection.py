import requests

url = "http://<UI_SERVER_IP>:5000/api/detection"

data = {
    "fire_level": 7.3,
    "smoke_level": 5.6
}

files = {
    "image": open("snapshot.jpg", "rb")
}

response = requests.post(url, data=data, files=files)
print(response.json())
