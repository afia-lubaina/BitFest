# BitFest
# API Documentation

## **Route**: `/ingredients/`  
**Method**: GET  
**Summary**: List all Ingredients  
**Sample Response**:
```json
[
  {
    "name": "Tomato",
    "quantity": 2,
    "unit": "pieces"
  },
  {
    "name": "Spaghetti",
    "quantity": 200,
    "unit": "grams"
  }
]
```

## **Route**: ` /ingredients/{name}`  
**Method**: Put  
**Summary**: Update Ingredients  
**Sample Response**:
```json
[
    {
    "name": "Garlic",
    "quantity": 5,
    "unit": "cloves"
  }
]
```

## **Route**: ` /ingredients/{name}`  
**Method**: Delete  
**Summary**: Delete Ingredients  
**Sample Response**:
```json
[
   {
  "message": "Ingredient 'Garlic' deleted successfully"
  }
]

```
## **Route**: ` /recipes/text`  
**Method**: Post  
**Summary**: Add recipe from text  
**Sample Payload**:
```json
[
     {
    "recipe": "Spaghetti Carbonara\n\nIngredients:\n- 200g spaghetti\n- 100g pancetta\n- 2 eggs\n- 50g Parmesan cheese\n- 50g Pecorino cheese\n- Salt and pepper\n\nInstructions:\n1. Cook the spaghetti according to the package instructions.\n2. Fry the pancetta in a pan until crispy.\n3. Beat the eggs and mix with the cheeses.\n4. Combine the spaghetti with pancetta, then toss with the egg mixture until creamy.\n5. Season with salt and pepper.\n\nCuisine Type: Italian\nTaste: Savory, Creamy\nPrep Time: 20 minutes\nReviews: 100"
  }
]
```
**Sample Response**:
```json
[
    {
  "message": "Recipe added successfully!"
  }
] 
```
## **Route**: ` /generate-recipe`  
**Method**: Post  
**Summary**:Generate a Recipe based on Cravings and Ingredients
**Sample Payload**:
```json
[
     {
  "craving": "Sweet",
  "cuisine_type": "Italian",
  "taste": "Sweet",
  "preparation_time": "30 minutes"
  }

]
```
**Sample Response**:
```json
[
   {
    "recipe": "Chocolate Cake\n\nIngredients:\n- 200g flour\n- 100g sugar\n- 2 eggs\n- 100g chocolate\n- 50g butter\n\nInstructions:\n1. Mix all dry ingredients together.\n2. Melt chocolate and butter, then combine with the dry ingredients.\n3. Pour into a baking pan and bake for 25 minutes.\n4. Let it cool and serve with whipped cream.\n\nCuisine Type: Italian\nTaste: Sweet\nPrep Time: 30 minutes"
  }

]
```

## **Route**: `/recipes/image`  
**Method**: Post  
**Summary**:Add image recipe
**Sample Payload**:
Multipart file
```
**Sample Response**:
```json
[
   {
  "message": "Recipe added successfully!"
  }

]
```


