# # test_9router.py
# import os
# from openai import OpenAI


# # BASE_URL = "http://localhost:20128/v1"
# # API_KEY = "sk-9b3a49569d145b1c-xl93wy-4acc38b2"
# # MODEL = "ollama/glm-4.7-flash"


# # def main():
# #     client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# #     response = client.chat.completions.create(
# #         model=MODEL,
# #         messages=[
# #             {"role": "user", "content": "who are you?"}
# #         ]
# #     )

# #     print(response.choices[0].message.content)


# if __name__ == "__main__":
#     main()
# Khởi tạo client kết nối
import openai

client = openai.OpenAI(
    base_url="https://api.ai-box.vn/v1",
    api_key="sk-wNKovtoUETnGGKkJzHeuAS5VaJ2rP4RnrpfEfb7oXTZW58Cn"
)

# Gửi request tới DeepSeek-V4 Pro
response = client.chat.completions.create(
    model="glm-5",
    messages=[
        {"role": "user", "content": "Hi! who are you?"}
    ]
)

print(response.choices[0].message.content)
