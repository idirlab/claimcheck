import ollama

def llama3_2(prompt):
    """
    Calls the Llama 3.2 model with a given prompt and returns the response.
    """
    response = ollama.chat(model='llama3.2', messages=[
      {
        'role': 'user',
        'content': prompt,
      },
    ])
    return response['message']['content']

def llama3_1(prompt):
    """
    Calls the Llama 3.1 model with a given prompt and returns the response.
    """
    response = ollama.chat(model='llama3.1:8b', messages=[
      {
        'role': 'user',
        'content': prompt,
      },
    ])
    return response['message']['content']
