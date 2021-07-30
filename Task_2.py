import requests
import json

url = 'https://api.nasa.gov/planetary/apod?api_key='
token = 'nWxdh7YgGjvEoV6JQNtlBzGwNlJBBSueMS4eT3Pr'
response = requests.get(url + token)

with open('data_2.json', 'w') as f:
    json.dump(response.json(), f)

# # Скачивание изображения дня:
# img = requests.get("https://api.nasa.gov/assets/img/general/apod.jpg")
# img_file = open('D:\Python/apod.jpg', 'wb')
# img_file.write(img.content)
# img_file.close()

print(response.headers)