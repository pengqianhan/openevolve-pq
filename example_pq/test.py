from openai import OpenAI
import os
api_key = os.getenv('HASEL_API_KEY')
print(api_key)
client = OpenAI(
    api_key=api_key,
    base_url="https://lm.deepnetdiscovery.net/v1"
)

response = client.chat.completions.create(
    model="qwen3-coder",
    # reasoning_effort="low",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a python code to print 'Hello, World!'"
        }
    ]
)

print(response.choices[0].message.content)