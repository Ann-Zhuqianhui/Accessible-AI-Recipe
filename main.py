from fastapi import FastAPI, Query
import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json


# Load API Key securely from environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Debug: Print API Key status (remove this in production)
if not api_key:
    raise ValueError("❌ Missing OpenAI API key. Set OPENAI_API_KEY in .env file.")
else:
    print("✅ OpenAI API Key Loaded Successfully")

# Initialize OpenAI client with API key
client = OpenAI()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change for security in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_recipe")
def get_recipe(
    ingredients: str,
    time_limit: int = 30, 
    preferences: str = "healthy",
    cuisines: str = "any"
):
    prompt = f"""
    You are a helpful AI chef. Generate 3 different recipe ideas **in valid JSON format**.
    
    **DO NOT** include markdown formatting (```json).
    **DO NOT** add extra text outside the JSON.

    Ingredients available: {ingredients}
    Cooking time limit: {time_limit} minutes
    Cooking preferences: {preferences} 
    Preferred cuisines: {cuisines}

    Return a JSON list of 3 objects, each containing:
    - "name" (string)
    - "ingredients" (list of strings)
    - "instructions" (list of strings)
    - "prep_time" (integer)
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}]
        )

        recipe_content = response.choices[0].message.content

        # **CLEAN RESPONSE**: Remove Markdown formatting if present
        cleaned_json = recipe_content.strip().replace("```json", "").replace("```", "").strip()

        # **VALIDATE JSON**: Ensure correct format
        recipes = json.loads(cleaned_json)

        return {"recipes": recipes}  # Wrap in a key
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format received from OpenAI"}
    except Exception as e:
        return {"error": f"OpenAI API Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)