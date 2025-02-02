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
        selected_tags = request_data.get("selectedTags", {})
        
        # ✅ Convert selectedTags (dict) into a list of only the `true` values
        ingredients = [key for key, value in selected_tags.items() if value]

        print("🔹 Extracted Ingredients:", ingredients)  # ✅ Debugging

        if not ingredients:
            raise HTTPException(status_code=400, detail="No valid ingredients provided.")

        # ✅ Updated Prompt to Force JSON Output
        prompt = f"""
        You are an AI chef. Generate exactly 3 different recipes using **only JSON format**.
        Each recipe should include:
        - 'name': Recipe name
        - 'ingredients': List of ingredients
        - 'instructions': List of steps to prepare the dish

        **Here are the details:**
        - Ingredients: {', '.join(ingredients)}
        - Time limit: {request_data.get("time_limit", 40)} minutes
        - Preferences: {', '.join(request_data.get("preferences", [])) if request_data.get("preferences") else 'None'}
        - Cuisines: {', '.join(request_data.get("cuisines", [])) if request_data.get("cuisines") else 'Any'}
        - Available cooking equipment: {', '.join(request_data.get("cooking_equipment", [])) if request_data.get("cooking_equipment") else 'Any'}
        - Available seasonings: {', '.join(request_data.get("seasonings", [])) if request_data.get("seasonings") else 'Basic'}

        **Return JSON only. Do not include explanations or extra text.**
        Example:
        [
          {{
            "name": "Grilled Cheese Sandwich",
            "ingredients": ["Cheese", "Bread", "Butter"],
            "instructions": ["Spread butter on bread", "Add cheese", "Grill until golden brown"]
          }},
          {{
            "name": "Tomato Soup",
            "ingredients": ["Tomatoes", "Salt", "Pepper"],
            "instructions": ["Blend tomatoes", "Add salt and pepper", "Simmer for 10 minutes"]
          }}
        ]
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