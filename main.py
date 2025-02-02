from fastapi import FastAPI, HTTPException, Query
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

@app.post("/get_recipe")
async def get_recipe(request_data: dict):
    try:
        # Extract data from JSON request
        fridge_items = request_data.get("fridgeItems", [])
        selected_tags = request_data.get("selectedTags", {})
        cooking_equipment = request_data.get("cooking_equipment", [])
        cuisines = request_data.get("cuisines", [])
        preferences = request_data.get("preferences", [])
        seasonings = request_data.get("seasonings", [])
        time_limit = request_data.get("time_limit", 40)

        # Convert selectedTags (boolean object) into a list of ingredients
        ingredients = [key for key, value in selected_tags.items() if value]

        # Debugging: Log extracted data
        print("🔹 Received Data:", request_data)
        print("🔹 Processed Ingredients:", ingredients)

        # Ensure ingredients are not empty
        if not ingredients:
            raise HTTPException(status_code=400, detail="No valid ingredients provided.")

        # Generate a prompt for OpenAI API
        prompt = f"""
        You are a helpful AI chef. Generate 3 different recipes based on the following details:
        - Ingredients: {', '.join(ingredients)}
        - Time limit: {time_limit} minutes
        - Preferences: {', '.join(preferences) if preferences else 'None'}
        - Cuisines: {', '.join(cuisines) if cuisines else 'Any'}
        - Available cooking equipment: {', '.join(cooking_equipment) if cooking_equipment else 'Any'}
        - Available seasonings: {', '.join(seasonings) if seasonings else 'Basic'}

        Provide recipes in JSON format with:
        - 'name' (recipe title)
        - 'ingredients' (list of ingredients)
        - 'instructions' (list of steps to prepare the dish)
        """
    #try:
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