from google import genai

client = genai.Client(api_key="AIzaSyAZgjoeoA8PwdBZ7UTGKqNqCBdm9V3Z9es")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="give a number from 1 to 10"
)
response = response.text
with open('file.txt', 'w') as file:
    file.write("")


    file.write(response)
