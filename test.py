# test_9router.py
import os
from openai import OpenAI


BASE_URL = "http://localhost:20128/v1"
API_KEY = "sk-9b3a49569d145b1c-xl93wy-4acc38b2"
MODEL = "ollama/glm-4.7-flash"


def main():
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "who are you?"}
        ]
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
