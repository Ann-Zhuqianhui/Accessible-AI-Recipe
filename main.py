from fastapi import FastAPI, Query
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load API Key securely from environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Debug: Print API Key status (remove this in production)
if not api_key:
    raise ValueError("❌ Missing OpenAI API key. Set OPENAI_API_KEY in .env file.")
else:
    print("✅ OpenAI API Key Loaded Successfully")

# Initialize OpenAI client with API key
client = OpenAI(api_key=api_key, organization="org-axVHaWzyi569paNmo7pAjw7z")

app = FastAPI()

@app.get("/get_recipe")
def get_recipe(ingredients: str, time_limit: int, style: str = "healthy"):
    prompt = f"Give me a {style} recipe using {ingredients} that can be cooked in {time_limit} minutes."

    try:
        response = client.chat.completions.create(
            model="gpt-4.0",  # Change to "gpt-3.5-turbo" if needed
            messages=[{"role": "system", "content": prompt}]
        )

        recipe = response.choices[0].message.content
        return {"recipe": recipe}
    
    except Exception as e:
        return {"error": f"OpenAI API Error: {str(e)}"}
