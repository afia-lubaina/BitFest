from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from .database import get_db,create_db_and_tables
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from .tables import Ingredient
import google.generativeai as genai
import requests
from io import BytesIO
from PyPDF2 import PdfReader
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from pathlib import Path
from PIL import Image
import pytesseract

class IngredientCreate(BaseModel):
    name: str
    quantity: float
    unit: str

# File path for storing recipes
RECIPE_FILE = "my_fav_recipes.txt"


app = FastAPI()

# Initialize the database (create tables if not already created)
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    if not os.path.exists(RECIPE_FILE):
        with open(RECIPE_FILE, "w", encoding="utf-8") as file:
            file.write("")  # Create an empty file

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI recipe app!"}


@app.post("/ingredients/")
def create_ingredient(ingredient: IngredientCreate, db: Session = Depends(get_db)):
    new_ingredient = Ingredient(name=ingredient.name, quantity=ingredient.quantity, unit=ingredient.unit)
    try:
        db.add(new_ingredient)
        db.commit()
        db.refresh(new_ingredient)
        return new_ingredient
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ingredient already exists")

@app.get("/ingredients/", response_model=List[IngredientCreate])
def list_ingredients(db: Session = Depends(get_db)):
    return db.query(Ingredient).all()

@app.put("/ingredients/{name}")
def update_ingredient_by_name(
    name: str, 
    ingredient: IngredientCreate, 
    db: Session = Depends(get_db)
):
    db_ingredient = db.query(Ingredient).filter(Ingredient.name == name).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    
    db_ingredient.name = ingredient.name
    db_ingredient.quantity = ingredient.quantity
    db_ingredient.unit = ingredient.unit
    db.commit()
    return {"message": f"Ingredient '{name}' updated successfully"}

@app.delete("/ingredients/{name}")
def delete_ingredient_by_name(name: str, db: Session = Depends(get_db)):
    db_ingredient = db.query(Ingredient).filter(Ingredient.name == name).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    
    db.delete(db_ingredient)
    db.commit()
    return {"message": f"Ingredient '{name}' deleted successfully"}


class RecipeText(BaseModel):
    recipe: str

@app.post("/recipes/text")
def add_recipe_from_text(recipe_data: RecipeText):
    save_recipe_to_file(recipe_data.recipe)
    return {"message": "Recipe added successfully!"}

def save_recipe_to_file(recipe: str):
    try:
        with open(RECIPE_FILE, "a", encoding="utf-8") as file:
            file.write(recipe + "\n\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing to file: {str(e)}")

env_path = Path(__file__).parent / ".env"  # Adjust the path as necessary
load_dotenv(dotenv_path=env_path)
GEMINI_API_KEY=os.getenv("GOOGLE_GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY) 
model = genai.GenerativeModel("gemini-pro")

@app.post("/generate-recipe")
async def generate_recipe(
    craving: str | None = Form(None),
    cuisine_type: str | None = Form(None),
    taste: str | None = Form(None),
    preparation_time: str | None = Form(None),
    db: Session = Depends(get_db)  # Use database session to fetch ingredients
):
    # Fetch available ingredients from the database
    ingredients = db.query(Ingredient).all()
    if not ingredients:
        raise HTTPException(status_code=400, detail="No ingredients available in the database")

    # Convert ingredients to a list of strings
    available_ingredients = [f"{ingredient.quantity} {ingredient.unit} of {ingredient.name}" for ingredient in ingredients]

    # Read the RECIPE_FILE contents
    try:
        with open(RECIPE_FILE, "r", encoding="utf-8") as file:
            stored_recipes = file.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Recipe file not found")

    # Combine available ingredients and stored recipes into a prompt
    prompt = f"""
    You are a recipe assistant. Based on the following ingredients, stored recipes, and user preferences, suggest maximum 3 recipes:

    Available Ingredients:
    {', '.join(available_ingredients)}

    Stored Recipes:
    {stored_recipes}

    User Preferences:
    - Craving: {craving or "none"}
    - Cuisine Type: {cuisine_type or "any"}
    - Taste: {taste or "any"}
    - Preparation time {preparation_time or "any"}

    Provide a detailed recipe including:
    - Recipe name
    - Ingredients (from available items)
    - Step-by-step instructions
    - Cuisine type (if applicable)
    - Taste profile (if applicable)
    - Preparation time
     
    If no user preferences matches for given user preferences, first write that nothing matched with preferences but you can suggest some and then just select based on ingredients and stored recipes.
    """

    # Generate recipe using the AI model
    response = model.generate_content(prompt)

    # Process the AI response
    if response.text:
        return {"recipe": response.text}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate recipe")


@app.post("/recipes/image")
def add_recipe_from_image(image: UploadFile = File(...)):
    # Extract text from the uploaded image
    recipe_text = extract_text_from_image(image)
    if not recipe_text:
        raise HTTPException(status_code=400, detail="No text found in the image")
    
    # Save the extracted text as a recipe
    save_recipe_to_file(recipe_text)
    return {"message": "Recipe added successfully from image!", "recipe": recipe_text}

def extract_text_from_image(image_file: UploadFile) -> str:
    try:
        # Load the image file
        image = Image.open(image_file.file)
        # Perform OCR to extract text
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")