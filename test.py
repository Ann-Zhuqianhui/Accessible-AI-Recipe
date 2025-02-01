from openai import OpenAI

api_key = "your_actual_api_key_here"
client = OpenAI(api_key=api_key)

try:
    models = client.models.list()
    print("Available models:")
    for model in models.data:
        print(model.id)
except Exception as e:
    print("OpenAI API Error:", e)