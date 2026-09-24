from groq import Groq

client = Groq(api_key="APIKEYQUITADA")

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": "Hola Groq, ¿Cuál es el último día del que tienes información?"}
    ]
)

print(response.choices[0].message.content)
