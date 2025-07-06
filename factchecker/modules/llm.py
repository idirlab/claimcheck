import openai
import os
import ollama
import base64

def prompt_gpt(prompt, model='o4-mini-2025-04-16'):
    openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    client = openai.OpenAI(api_key=openai.api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def prompt_ollama(prompt, model='qwen3:4b', think=True):
    messages = []
    if not think:
        messages.append({'role': 'system', 'content': '/no_think'})
    messages.append({
        'role': 'user',
         'content': prompt,
    })

    response = ollama.chat(model=model, messages=messages)

    output = response['message']['content']

    if '<think>' in output[:20]:
        output = output.split('</think>')[-1]
        
    return output

