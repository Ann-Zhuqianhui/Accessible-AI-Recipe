from fastapi import FastAPI, Query
import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


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
    """
    Generates 3 recipe options based on user input.
    
    - `ingredients`: Comma-separated list of available ingredients.
    - `time_limit`: Maximum cooking time in minutes.
    - `preferences`: Cooking preferences, separated by semicolons.
    - `cuisines`: Preferred cuisine styles, separated by semicolons.
    """

    prompt = f"""
    You are a helpful AI chef. Generate 3 different recipe ideas based on the following:
    
    Ingredients available: {ingredients}
    Cooking time limit: {time_limit} minutes
    Cooking preferences: {preferences} 
    Preferred cuisines: {cuisines}

    Return the output in **valid JSON format** as a list of 3 objects. 
    For each recipe, include:
    - Name of the dish
    - List of ingredients used
    - Step-by-step cooking instructions
    - Approximate preparation time

    Keep responses clear and concise.
    Example JSON output format:
    [
        {{"name": "Stir-fried Chicken", "ingredients": ["chicken", "soy sauce", "garlic"], 
          "instructions": ["Step 1...", "Step 2..."], "prep_time": 20}},
        {{"name": "Vegetable Pasta", "ingredients": ["pasta", "tomato", "basil"], 
          "instructions": ["Step 1...", "Step 2..."], "prep_time": 25}}
    ]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}]
        )

        recipe = response.choices[0].message.content
        return {"recipe": recipe}
    
    except Exception as e:
        return {"error": f"OpenAI API Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)