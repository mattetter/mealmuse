from mealmuse.models import Recipe, Item, RecipeItem, MealPlan, Meal, Day, db
from datetime import datetime



meal_plan = {
    'days': [
        {'day': 'Wednesday', 'meals': [
            {'meal_name': 'Breakfast', 'recipe': 'Paneer Paratha'},
            {'meal_name': 'Lunch', 'recipe': 'Chana Masala'}, 
            {'meal_name': 'Dinner', 'recipe': 'Aloo Gobi'}
            ]}, 
        {'day': 'Thursday', 'meals': [
            {'meal_name': 'Breakfast', 'recipe': 'Veggie Upma'},
            {'meal_name': 'Lunch', 'recipe': 'Dal Makhani'}, 
            {'meal_name': 'Dinner', 'recipe': 'Palak Paneer'}
            ]
        }
    ]
}


recipes = {'Paneer Paratha': {
    'ingredient_list': [
        'Paneer', 'Wheat flour', 'Ghee', 'Salt', 'Water', 'Ginger', 'Green chili', 'Coriander leaves'], 
    'cooking_instructions': [
        '1. In a mixing bowl, combine wheat flour, salt, and water to make a soft dough. ', 
        '2. In a separate bowl, crumble paneer and add chopped ginger, green chili, and coriander leaves. Mix well. ', 
        '3. Take a small portion of the dough and roll it into a small circle. ', 
        '4. Place a spoonful of paneer mixture in the center of the circle and fold it in half. ', 
        '5. Roll it out gently to make a paratha. ', '6. Heat a tawa or griddle and cook the paratha on both sides using ghee. ', 
        '7. Serve hot with your favorite chutney or pickle.']
        }, 
        'Chana Masala': {'ingredient_list': ['Chickpeas', 'Onion', 'Tomato', 'Ginger-garlic paste', 'Turmeric powder', 'Red chili powder', 'Coriander powder', 'Garam masala', 'Cumin seeds', 'Oil', 'Salt', 'Water'], 'cooking_instructions': ['1. Soak the chickpeas overnight and pressure cook with water and salt until tender. ', '2. Heat oil in a pan and add cumin seeds. ', '3. Add chopped onions and sauté until golden brown. ', '4. Add ginger-garlic paste and cook for a minute. ', '5. Add chopped tomatoes and cook until soft. ', '6. Add turmeric powder, red chili powder, coriander powder, and garam masala. Mix well. ', '7. Add the cooked chickpeas and mix with the masala. ', '8. Cook for a few minutes, adding water if necessary. ', '9. Serve hot with rice or roti.']}, 'Aloo Gobi': {'ingredient_list': ['Potatoes', 'Cauliflower', 'Onion', 'Tomato', 'Garlic', 'Ginger', 'Green chili', 'Turmeric powder', 'Red chili powder', 'Garam masala', 'Cumin seeds', 'Oil', 'Salt', 'Water'], 'cooking_instructions': ['1. Heat oil in a pan and add cumin seeds. ', '2. Add chopped onions, garlic, ginger, and green chili. Sauté until onions turn golden brown. ', '3. Add chopped tomatoes and cook until soft. ', '4. Add turmeric powder, red chili powder, garam masala, and salt. Mix well. ', '5. Add diced potatoes and cauliflower florets to the pan. ', '6. Cover and cook on medium heat until the vegetables are tender. ', '7. If needed, sprinkle some water occasionally to prevent sticking. ', '8. Serve hot with rice or roti.']}, 'Veggie Upma': {'ingredient_list': [''], 'cooking_instructions': ['']}, 'Dal Makhani': {'ingredient_list': [''], 'cooking_instructions': ['']}, 'Palak Paneer': {'ingredient_list': [''], 'cooking_instructions': ['']}}

shopping_list =  ['Paneer', 'Tomato', 'Chickpeas', 'Garam masala', 'Oil', 'Coriander leaves', 'Red chili powder', 'Potatoes', 'Garlic', 'Cauliflower', 'Green chili', 'Ginger-garlic paste', 'Onion', 'Coriander powder', 'Ghee', 'Water', 'Ginger', 'Salt', 'Wheat flour', 'Turmeric powder', 'Cumin seeds']

meal_plan_biggus = {'days': [{'day': 'Wednesday', 'meals': [{'meal_name': 'Breakfast', 'recipe': 'Vegetarian omelette', 'recipe_details': {'recipe': {'ingredients': [{'name': 'eggs', 'quantity': 2, 'unit': ''}, {'name': 'vegetables (e.g. bell peppers, mushrooms, spinach)', 'quantity': 1, 'unit': 'cup'}, {'name': 'cheese', 'quantity': 0.5, 'unit': 'cup'}, {'name': 'salt', 'quantity': 0.25, 'unit': 'teaspoon'}, {'name': 'pepper', 'quantity': 0.25, 'unit': 'teaspoon'}, {'name': 'olive oil', 'quantity': 2, 'unit': 'teaspoons'}], 'cooking_instructions': ['Step 1: Heat olive oil in a non-stick pan over medium heat.', 'Step 2: Sautee vegetables until softened, about 5 minutes.', 'Step 3: In a bowl, beat eggs with salt and pepper.', 'Step 4: Pour egg mixture into the pan with vegetables.', 'Step 5: Cook until the edges start to set, about 2 minutes.', 'Step 6: Sprinkle cheese over omelette.', 'Step 7: Fold omelette in half and cook for another minute, until cheese is melted.', 'Step 8: Serve hot.']}}}, {'meal_name': 'Lunch', 'recipe': 'Vegetarian pesto pasta', 'recipe_details': {'recipe': {'ingredients': [{'name': 'pasta', 'quantity': 8.0, 'unit': 'ounces'}, {'name': 'basil leaves', 'quantity': 2.0, 'unit': 'cups'}, {'name': 'pine nuts', 'quantity': 0.5, 'unit': 'cup'}, {'name': 'garlic cloves', 'quantity': 2.0, 'unit': 'cloves'}, {'name': 'Parmesan cheese', 'quantity': 0.25, 'unit': 'cup'}, {'name': 'olive oil', 'quantity': 0.75, 'unit': 'cup'}, {'name': 'salt', 'quantity': 1.0, 'unit': 'teaspoon'}, {'name': 'black pepper', 'quantity': 0.5, 'unit': 'teaspoon'}], 'cooking_instructions': ['Step 1: Cook the pasta according to package instructions until al dente. Drain and set aside.', 'Step 2: In a food processor, combine basil leaves, pine nuts, garlic cloves, Parmesan cheese, salt, and black pepper. Process until finely chopped.', 'Step 3: While the food processor is running, slowly pour in the olive oil and continue processing until the mixture forms a smooth pesto.', 'Step 4: In a large pan, heat the pesto over medium heat. Add the cooked pasta and toss until well coated.', 'Step 5: Serve hot and enjoy!']}}}, {'meal_name': 'Dinner', 'recipe': 'Eggplant Parmesan', 'recipe_details': {'recipe': {'ingredients': [{'name': 'eggplant', 'quantity': 1, 'unit': 'large'}, {'name': 'eggs', 'quantity': 2, 'unit': ''}, {'name': 'breadcrumbs', 'quantity': 1, 'unit': 'cup'}, {'name': 'Parmesan cheese', 'quantity': 1, 'unit': 'cup'}, {'name': 'mozzarella cheese', 'quantity': 2, 'unit': 'cups'}, {'name': 'marinara sauce', 'quantity': 2, 'unit': 'cups'}, {'name': 'olive oil', 'quantity': 2, 'unit': 'tablespoons'}, {'name': 'salt', 'quantity': 1, 'unit': 'teaspoon'}, {'name': 'black pepper', 'quantity': 1, 'unit': 'teaspoon'}], 'cooking_instructions': ['Step 1: Preheat the oven to 375°F (190°C).', 'Step 2: Slice the eggplant into 0.5-inch thick rounds.', 'Step 3: In a shallow dish, beat the eggs with salt and black pepper.', 'Step 4: Dip each eggplant slice into the beaten eggs, then coat with breadcrumbs.', 'Step 5: In a large skillet, heat olive oil over medium heat.', 'Step 6: Fry the coated eggplant slices in the skillet until golden brown on each side.', 'Step 7: Remove the eggplant slices from the skillet and place them on a paper towel-lined plate to absorb excess oil.', 'Step 8: In a baking dish, spread a layer of marinara sauce.', 'Step 9: Arrange a layer of fried eggplant slices on top of the sauce.', 'Step 10: Sprinkle Parmesan cheese over the eggplant slices.', 'Step 11: Repeat layers of marinara sauce, fried eggplant slices, and Parmesan cheese.', 'Step 12: Top the final layer with mozzarella cheese.', 'Step 13: Bake in the preheated oven for 25-30 minutes, or until the cheese is melted and bubbling.', 'Step 14: Let the Eggplant Parmesan cool for a few minutes before serving.', 'Step 15: Garnish with fresh basil leaves, if desired, and serve hot.']}}}]}, {'day': 'Tuesday', 'meals': [{'meal_name': 'Breakfast', 'recipe': 'Vegetarian breakfast burrito', 'recipe_details': {'recipe': {'ingredients': [{'name': 'eggs', 'quantity': 2, 'unit': 'pieces'}, {'name': 'whole wheat tortilla', 'quantity': 1, 'unit': 'piece'}, {'name': 'black beans (cooked)', 'quantity': 1, 'unit': 'cup'}, {'name': 'avocado', 'quantity': 0.5, 'unit': 'piece'}, {'name': 'tomato', 'quantity': 1, 'unit': 'piece'}, {'name': 'cheddar cheese', 'quantity': 0.5, 'unit': 'cup'}, {'name': 'salsa', 'quantity': 2, 'unit': 'tablespoons'}, {'name': 'cilantro', 'quantity': 1, 'unit': 'tablespoon'}, {'name': 'salt', 'quantity': 0.25, 'unit': 'teaspoon'}, {'name': 'pepper', 'quantity': 0.25, 'unit': 'teaspoon'}, {'name': 'olive oil', 'quantity': 1, 'unit': 'tablespoon'}], 'cooking_instructions': ['Step 1: Heat olive oil in a pan over medium heat.', 'Step 2: In a bowl, whisk the eggs with salt and pepper.', 'Step 3: Pour the whisked eggs into the pan and cook until scrambled.', 'Step 4: Warm the tortilla in a separate pan or microwave.', 'Step 5: Mash the avocado in a bowl and slice the tomato.', 'Step 6: Place the warmed tortilla on a plate and layer with black beans, scrambled eggs, avocado, tomato, cheddar cheese, salsa, and cilantro.', 'Step 7: Roll the burrito tightly and serve.', 'Step 8: Enjoy your vegetarian breakfast burrito!']}}}, {'meal_name': 'Lunch', 'recipe': 'Caprese salad', 'recipe_details': {'recipe': {'ingredients': [{'name': 'tomatoes', 'quantity': 2.0, 'unit': 'large'}, {'name': 'mozzarella cheese', 'quantity': 8.0, 'unit': 'ounces'}, {'name': 'fresh basil leaves', 'quantity': 0.5, 'unit': 'cup'}, {'name': 'extra virgin olive oil', 'quantity': 2.0, 'unit': 'tablespoons'}, {'name': 'balsamic vinegar', 'quantity': 1.0, 'unit': 'tablespoon'}, {'name': 'salt', 'quantity': 0.5, 'unit': 'teaspoon'}, {'name': 'black pepper', 'quantity': 0.25, 'unit': 'teaspoon'}], 'cooking_instructions': ['Step 1: Slice the tomatoes and mozzarella cheese into quarter inch rounds.', 'Step 2: Arrange the tomato and mozzarella slices on a platter, alternating between the two.', 'Step 3: Scatter the fresh basil leaves over the tomato and mozzarella slices.', 'Step 4: Drizzle the extra virgin olive oil and balsamic vinegar over the salad.', 'Step 5: Season with salt and black pepper to taste.', 'Step 6: Allow the salad to marinate for at least 15 minutes before serving.']}}}, {'meal_name': 'Dinner', 'recipe': 'Margherita pizza', 'recipe_details': {'recipe': {'ingredients': [{'name': 'pizza dough', 'quantity': 1.0, 'unit': 'portion'}, {'name': 'tomato sauce', 'quantity': 0.5, 'unit': 'cup'}, {'name': 'mozzarella cheese', 'quantity': 200.0, 'unit': 'grams'}, {'name': 'fresh basil', 'quantity': 10.0, 'unit': 'leaves'}, {'name': 'olive oil', 'quantity': 2.0, 'unit': 'tablespoons'}, {'name': 'salt', 'quantity': 1.0, 'unit': 'pinch'}], 'cooking_instructions': ['Step 1: Preheat the oven to 475°F (245°C).', 'Step 2: Roll out the pizza dough on a floured surface to your desired thickness.', 'Step 3: Transfer the dough to a baking sheet or pizza stone.', 'Step 4: Spread the tomato sauce evenly over the dough.', 'Step 5: Sprinkle the mozzarella cheese over the sauce.', 'Step 6: Tear the fresh basil leaves and distribute them over the cheese.', 'Step 7: Drizzle the olive oil over the pizza.', 'Step 8: Season with a pinch of salt.', 'Step 9: Bake in the preheated oven for about 12-15 minutes, or until the crust is golden and the cheese is melted and bubbly.', 'Step 10: Remove from the oven and let cool for a few minutes before slicing and serving.']}}}]}]}



meal_plan_output_gpt_4 = {
  "description": "This meal plan is designed for someone with a pescatarian diet following Mediterranean cuisine. A shellfish allergy is accounted for, and the plan makes use of 80% of pantry items available, suiting an intermediate level of culinary skill with equipment such as an oven, stovetop, and blender.",
  "Monday": {
    "Breakfast": {
      "recipe_name": "Mediterranean Avocado Tuna Salad",
      "cost": "affordable",
      "prep_time": 15,
      "cook_time": 15,
      "serves": 2,
      "number_of_ingredients": 7,
      "ingredients_from_pantry": ["olive oil", "garlic", "feta cheese", "canned tuna", "black pepper", "chili flakes", "salt"]
    },
    "Lunch": {
      "recipe_name": "Greek Chickpea Salad",
      "cost": "affordable",
      "prep_time": 10,
      "cook_time": 20,
      "serves": 1,
      "number_of_ingredients": 6,
      "ingredients_from_pantry": ["olive oil", "garlic", "feta cheese", "black pepper", "chickpeas", "salt"]
    },
    "Dinner": {
      "recipe_name": "Mediterranean Baked Fish with Tomatoes and Capers",
      "cost": "moderate",
      "prep_time": 25,
      "cook_time": 40,
      "serves": 4,
      "number_of_ingredients": 8,
      "ingredients_from_pantry": ["olive oil", "garlic", "black pepper", "salt", "canned tomatoes", "capers", "basil", "oregano"]
    }
  },
  "Tuesday": {
    "Breakfast": {
      "recipe_name": "Greek Yogurt with Honey and Walnuts",
      "cost": "affordable",
      "prep_time": 7,
      "cook_time": 10,
      "serves": 1,
      "number_of_ingredients": 4,
      "ingredients_from_pantry": ["honey", "walnuts", "raisins", "cinnamon"]
    },
    "Dinner": {
      "recipe_name": "Mediterranean Stuffed Peppers",
      "cost": "moderate",
      "prep_time": 30,
      "cook_time": 50,
      "serves": 3,
      "number_of_ingredients": 9,
      "ingredients_from_pantry": ["olive oil", "garlic", "feta cheese", "rice", "black beans", "salt", "black pepper", "cumin", "paprika"]
    }
  },
  "Wednesday": {
    "Breakfast": {
      "recipe_name": "Peanut Butter Banana Oatmeal",
      "cost": "affordable",
      "prep_time": 10,
      "cook_time": 15,
      "serves": 1,
      "number_of_ingredients": 6,
      "ingredients_from_pantry": ["oats", "peanut butter", "honey", "banana", "cinnamon", "almond milk"]
    },
    "Dinner": {
      "recipe_name": "Pasta with Tomato and Chickpea Sauce",
      "cost": "affordable",
      "prep_time": 20,
      "cook_time": 30,
      "serves": 2,
      "number_of_ingredients": 7,
      "ingredients_from_pantry": ["pasta", "olive oil", "canned tomatoes", "chickpeas", "salt", "black pepper", "garlic"]
    }
  }
}


example_user_request_gpt4 = {
    "role": "user",
    "content": {
        "general": {
            "allergies": ["shellfish"],
            "cuisine": "Mediterranean",
            "diet": "pescatarian",
            "pantry_items": [
                "olive oil",
                "garlic",
                "feta cheese",
                "mini marshmallows"
            ],
            "pantry_usage_preference": 80,
            "calorie_range": [1700, 2100],
            "macronutrients": {
                "carbs": 45,
                "protein": 25,
                "fats": 30
            },
            "equipment": ["oven", "stovetop", "blender"],
            "culinary_skill": "intermediate",
            "budget_range": [250, 500],  # Weekly meal plan budget
            "meal_diversity": "high",
            "leftover_management": 0.5,
            "description": "please generate"
        },
        "daily": {
            "Monday": {
                "Breakfast": {
                    "time_required_range": [20, 40],
                    "serves": 2,
                    "user_request": "none"
                },
                "Lunch": {
                    "time_required_range": [20, 35],
                    "serves": 1,
                    "user_request": "none"
                },
                "Dinner": {
                    "time_required_range": [45, 75],
                    "serves": 4,
                    "user_request": "none"
                }
            },
            "Tuesday": {
                "Breakfast": {
                    "time_required_range": [15, 25],
                    "serves": 1,
                    "user_request": "none"
                },
                "Dinner": {
                    "time_required_range": [50, 90],
                    "serves": 3,
                    "user_request": "none"
                }
            },
            "Wednesday": {
                "Breakfast": {
                    "time_required_range": [18, 33],
                    "serves": 1,
                    "user_request": "none"
                },
                "Dinner": {
                    "time_required_range": [35, 60],
                    "serves": 2,
                    "user_request": "none"
                }
            }
        }
    }
}


meal_plan_user_prompt_gpt4_v1 = {
	"role": "user",
	"content": {
		"general": {
			"allergies": ["Peanuts"],
			"cuisine": "chinese",
			"dietary restrictions": ["Vegan"],
			"pantry_items": ["popcorn", "Cabbage", "olive oil", "chicken", "falafel", "yogurt"],
			"pantry_usage_preference": "53.0 percent",
			"calorie_range": "2000-2500",
			"equipment": [],
			"culinary_skill": "Beginner",
			"budget": 400,
			"meal_diversity": "high",
			"leftover_management": "35.0 percent",
			"description": "please generate"
		},
		"daily": {
			"Thursday": {
				"time_to_cook": 60,
				"meals": {},
				"Breakfast": {
					"serves": 4,
					"user_request": "none"
				},
				"Dinner": {
					"serves": 4,
					"user_request": "none"
				},
				"Snack": {
					"serves": 4,
					"user_request": "none"
				}
			},
			"Friday": {
				"time_to_cook": 15,
				"meals": {},
				"Dinner": {
					"serves": 4,
					"user_request": "none"
				}
			},
			"Saturday": {
				"time_to_cook": 120,
				"meals": {},
				"Breakfast": {
					"serves": 4,
					"user_request": "none"
				},
				"Lunch": {
					"serves": 4,
					"user_request": "none"
				},
				"Dinner": {
					"serves": 4,
					"user_request": "none"
				},
				"Dessert": {
					"serves": 4,
					"user_request": "none"
				}
			}
		}
	}
}



meal_plan_output_gpt_4_v1 = {
   "description": "Here is a meal plan based on your preferences.",
   "days": {
      "Monday": {
         "meals": {
            "Breakfast": {
               "recipes": {
                  "Recipe 1": {
                     "name": "Omelette",
                     "cost_in_dollars": 5,
                     "time_required": 15,
                     "serves": 1,
                     "number_of_ingredients": 4,
                     "ingredients_from_pantry": ["Eggs", "Cheese", "Spinach", "Salt"]
                  }
               }
            },
            "Lunch": {
               "recipes": {
                  "Recipe 2": {
                     "name": "Chicken Salad",
                     "cost_in_dollars": 8,
                     "time_required": 20,
                     "serves": 1,
                     "number_of_ingredients": 6,
                     "ingredients_from_pantry": ["Chicken", "Lettuce", "Tomatoes", "Cucumber", "Olive Oil", "Lemon"]
                  }
               }
            },
            "Dessert": {
               "recipes": {
                  "Recipe 3": {
                     "name": "Fruit Parfait",
                     "cost_in_dollars": 3,
                     "time_required": 10,
                     "serves": 1,
                     "number_of_ingredients": 3,
                     "ingredients_from_pantry": ["Yogurt", "Granola", "Mixed Berries"]
                  }
               }
            }
         }
      },
      "Tuesday": {
         "meals": {
            "Lunch": {
               "recipes": {
                  "Recipe 4": {
                     "name": "Caprese Sandwich",
                     "cost_in_dollars": 6,
                     "time_required": 15,
                     "serves": 1,
                     "number_of_ingredients": 5,
                     "ingredients_from_pantry": ["Bread", "Mozzarella", "Tomatoes", "Basil", "Balsamic Glaze"]
                  }
               }
            },
            "Dinner": {
               "recipes": {
                  "Recipe 5": {
                     "name": "Pasta with Tomato Sauce",
                     "cost_in_dollars": 7,
                     "time_required": 30,
                     "serves": 1,
                     "number_of_ingredients": 6,
                     "ingredients_from_pantry": ["Pasta", "Tomato Sauce", "Garlic", "Onion", "Olive Oil", "Parmesan Cheese"]
                  }
               }
            }
         }
      }
   }
}

meal_plan_output_gpt_4_v2 = {
   "description": "Meal plan tailored to Italian cuisine preferences",
   "days": {
       "Tuesday": {
           "Breakfast": {
               "recipe": {
                   "name": "Italian Breakfast Frittata",
                   "cost_in_dollars": 10,
                   "time_required": 30,
                   "serves": 2,
                   "number_of_ingredients": 8,
                   "ingredients_from_pantry": ["Eggs", "Milk", "Cheese"]
               }
           },
           "Lunch": {
               "recipe": {
                   "name": "Caprese Panini",
                   "cost_in_dollars": 15,
                   "time_required": 30,
                   "serves": 2,
                   "number_of_ingredients": 7,
                   "ingredients_from_pantry": ["Bread", "Tomatoes", "Mozzarella", "Basil"]
               }
           },
           "Dinner": {
               "recipe": {
                   "name": "Spaghetti Bolognese",
                   "cost_in_dollars": 20,
                   "time_required": 30,
                   "serves": 2,
                   "number_of_ingredients": 10,
                   "ingredients_from_pantry": ["Spaghetti", "Ground Beef", "Onion", "Garlic", "Tomato Sauce"]
               }
           }
       },
       "Wednesday": {
           "Breakfast": {
               "recipe": {
                   "name": "Israeli Shakshuka",
                   "cost_in_dollars": 12,
                   "time_required": 30,
                   "serves": 2,
                   "number_of_ingredients": 7,
                   "ingredients_from_pantry": ["Eggs", "Tomatoes", "Onion", "Garlic"]
               }
           },
           "Lunch": {
               "recipe": {
                   "name": "Margherita Pizza",
                   "cost_in_dollars": 18,
                   "time_required": 30,
                   "serves": 2,
                   "number_of_ingredients": 7,
                   "ingredients_from_pantry": ["Pizza Dough", "Tomato Sauce", "Mozzarella", "Basil"]
               }
           },
           "Dinner": {
               "recipe": {
                   "name": "Kung Pao Chicken",
                   "cost_in_dollars": 25,
                   "time_required": 30,
                   "serves": 2,
                   "number_of_ingredients": 11,
                   "ingredients_from_pantry": ["Chicken", "Bell Peppers", "Peanuts", "Soy Sauce", "Rice"]
               }
           }
       }
   }
}


Italian_Breakfast_Frittata ={
  "recipe": {
    "ingredients": [
      {"name": "Eggs", "quantity": 6.0, "unit": "unit"},
      {"name": "Milk", "quantity": 0.25, "unit": "cup"},
      {"name": "Cheese", "quantity": 0.5, "unit": "cup"},
      {"name": "Salt", "quantity": 0.5, "unit": "teaspoon"},
      {"name": "Black Pepper", "quantity": 0.25, "unit": "teaspoon"},
      {"name": "Spinach", "quantity": 2.0, "unit": "cups"},
      {"name": "Tomatoes", "quantity": 2.0, "unit": "medium"},
      {"name": "Olive Oil", "quantity": 2.0, "unit": "tablespoons"}
    ],
    "cooking_instructions": [
      "Step 1: Preheat the oven to 375°F (190°C).",
      "Step 2: In a mixing bowl, whisk together the eggs, milk, salt, and black pepper.",
      "Step 3: Heat the olive oil in an oven-safe skillet over medium heat.",
      "Step 4: Add the spinach and tomatoes to the skillet and cook until the spinach wilts and the tomatoes soften.",
      "Step 5: Pour the egg mixture over the vegetables in the skillet.",
      "Step 6: Sprinkle the cheese evenly over the top.",
      "Step 7: Transfer the skillet to the preheated oven and bake for about 15 minutes or until the frittata is set in the center.",
      "Step 8: Remove the skillet from the oven and let the frittata cool for a few minutes before slicing and serving."
    ]
  }
}

Caprese_Panini ={
"recipe": {
  "ingredients": [
    {"name": "Bread", "quantity": 4, "unit": "slices"},
    {"name": "Tomatoes", "quantity": 2, "unit": "large"},
    {"name": "Mozzarella", "quantity": 6, "unit": "ounces"},
    {"name": "Basil", "quantity": 1, "unit": "cup"},
    {"name": "Olive Oil", "quantity": 2, "unit": "tablespoons"},
    {"name": "Salt", "quantity": 0.5, "unit": "teaspoon"},
    {"name": "Black Pepper", "quantity": 0.25, "unit": "teaspoon"}
  ],
  "cooking_instructions": [
    "Step 1: Preheat a panini press or a skillet over medium heat.",
    "Step 2: Slice the tomatoes and mozzarella.",
    "Step 3: Arrange the bread slices on a clean surface.",
    "Step 4: Drizzle 1 tablespoon of olive oil on one side of each bread slice.",
    "Step 5: Place the tomatoes and mozzarella on half of the bread slices.",
    "Step 6: Season with salt and black pepper.",
    "Step 7: Add the basil leaves.",
    "Step 8: Place the remaining bread slices on top to create sandwiches.",
    "Step 9: Brush the top of each sandwich with the remaining tablespoon of olive oil.",
    "Step 10: Transfer the sandwiches to the panini press or skillet.",
    "Step 11: Cook until the bread is toasted and the cheese is melted, about 3-4 minutes per side.",
    "Step 12: Remove the sandwiches from the press or skillet and let them cool slightly.",
    "Step 13: Cut each sandwich in half diagonally and serve warm."
  ]
}
}

Spaghetti_Bolognese ={
"recipe": {
"ingredients": [
{"name": "Spaghetti", "quantity": 200, "unit": "g"},
{"name": "Ground Beef", "quantity": 250, "unit": "g"},
{"name": "Onion", "quantity": 1, "unit": ""},
{"name": "Garlic", "quantity": 2, "unit": "cloves"},
{"name": "Tomato Sauce", "quantity": 400, "unit": "g"},
{"name": "Olive Oil", "quantity": 1, "unit": "tbsp"},
{"name": "Salt", "quantity": 1, "unit": "tsp"},
{"name": "Pepper", "quantity": 1, "unit": "tsp"},
{"name": "Parmesan Cheese", "quantity": 50, "unit": "g"},
{"name": "Fresh Basil", "quantity": 10, "unit": "leaves"}
],
"cooking_instructions": [
"Step 1: Cook the spaghetti according to the package instructions. Drain and set aside.",
"Step 2: In a large pan, heat the olive oil over medium heat. Add the onion and garlic, and cook until softened.",
"Step 3: Add the ground beef to the pan and cook until browned. Season with salt and pepper.",
"Step 4: Stir in the tomato sauce and simmer for 10 minutes.",
"Step 5: Add the cooked spaghetti to the pan and toss to coat in the sauce. Cook for an additional 2-3 minutes until heated through.",
"Step 6: Serve the spaghetti bolognese topped with Parmesan cheese and fresh basil leaves."
]
}
}


Israeli_Shakshuka = {
  "recipe": {
    "ingredients": [
      {"name": "Eggs", "quantity": 4, "unit": "units"},
      {"name": "Tomatoes", "quantity": 4, "unit": "medium"},
      {"name": "Onion", "quantity": 1, "unit": "medium"},
      {"name": "Garlic", "quantity": 2, "unit": "cloves"},
      {"name": "Olive oil", "quantity": 2, "unit": "tablespoons"},
      {"name": "Cumin", "quantity": 1, "unit": "teaspoon"},
      {"name": "Paprika", "quantity": 1, "unit": "teaspoon"}
    ],
    "cooking_instructions": [
      "Step 1: Heat olive oil in a large skillet over medium heat.",
      "Step 2: Add the chopped onion and sauté for 5 minutes, until softened.",
      "Step 3: Add the minced garlic, cumin, and paprika to the skillet. Cook for an additional 1 minute, stirring constantly.",
      "Step 4: Add the chopped tomatoes to the skillet and simmer for 10 minutes, until slightly thickened.",
      "Step 5: Make small wells in the tomato mixture and crack the eggs into the wells. Cover the skillet and cook for 5-7 minutes, until the eggs are cooked to your liking.",
      "Step 6: Serve the shakshuka hot, garnished with parsley or cilantro if desired."
    ]
  }
}


Margherita_Pizza ={
  "recipe": {
    "ingredients": [
      {"name": "Pizza Dough", "quantity": 1, "unit": "batch"},
      {"name": "Tomato Sauce", "quantity": 0.5, "unit": "cup"},
      {"name": "Mozzarella", "quantity": 1, "unit": "cup"},
      {"name": "Basil", "quantity": 0.5, "unit": "cup"},
      {"name": "Salt", "quantity": 0.5, "unit": "teaspoon"},
      {"name": "Olive Oil", "quantity": 1, "unit": "tablespoon"},
      {"name": "Garlic Powder", "quantity": 0.5, "unit": "teaspoon"}
    ],
    "cooking_instructions": [
      "Step 1: Preheat the oven to 450°F (230°C).",
      "Step 2: Roll out the pizza dough into a thin round shape.",
      "Step 3: Place the rolled-out dough onto a baking sheet.",
      "Step 4: Spread the tomato sauce evenly over the dough.",
      "Step 5: Sprinkle half of the mozzarella cheese over the sauce.",
      "Step 6: Tear the basil leaves into small pieces and sprinkle them over the cheese.",
      "Step 7: Sprinkle the remaining mozzarella cheese over the basil.",
      "Step 8: Season with salt and garlic powder.",
      "Step 9: Drizzle olive oil over the top.",
      "Step 10: Bake in the preheated oven for about 12-15 minutes or until the cheese is melted and bubbly.",
      "Step 11: Remove from the oven and let it cool for a few minutes before slicing.",
      "Step 12: Serve hot and enjoy!"
    ]
  }
}


Kung_Pao_Chicken = {
  "recipe": {
    "ingredients": [
      {"name": "Chicken", "quantity": 0.5, "unit": "lbs"},
      {"name": "Bell Peppers", "quantity": 1, "unit": "piece"},
      {"name": "Peanuts", "quantity": 0.25, "unit": "cup"},
      {"name": "Soy Sauce", "quantity": 2, "unit": "tbsp"},
      {"name": "Rice", "quantity": 1, "unit": "cup"}
    ],
    "cooking_instructions": [
      "Step 1: Cook the rice according to the package instructions.",
      "Step 2: In a large skillet, heat oil over medium-high heat.",
      "Step 3: Add the chicken to the skillet and cook until browned and cooked through.",
      "Step 4: Remove the chicken from the skillet and set aside.",
      "Step 5: In the same skillet, add the bell peppers and sauté until slightly tender.",
      "Step 6: Add the peanuts and cook for another minute.",
      "Step 7: Add the cooked chicken back to the skillet.",
      "Step 8: Pour in the soy sauce and stir to coat everything evenly.",
      "Step 9: Cook for another 2-3 minutes until heated through.",
      "Step 10: Serve the Kung Pao Chicken over the cooked rice."
    ]
  }
}

def get_recipe(recipe_name):
    if recipe_name == "Italian Breakfast Frittata":
        return Italian_Breakfast_Frittata
    elif recipe_name == "Caprese Panini":
        return Caprese_Panini
    elif recipe_name == "Spaghetti Bolognese":
        return Spaghetti_Bolognese
    elif recipe_name == "Israeli Shakshuka":
        return Israeli_Shakshuka
    elif recipe_name == "Margherita Pizza":
        return Margherita_Pizza
    elif recipe_name == "Kung Pao Chicken":
        return Kung_Pao_Chicken
    else:
        return None
    

def add_meal_plan_to_database(user):
    # create a meal plan object in the database with associated datetime, budget and cuisine
    meal_plan = MealPlan(user_id=user.id, budget=150, cuisine_requests="Italian", date_created=datetime.now())
    db.session.add(meal_plan)
    db.session.commit()
    # Add two days to the meal plan with datetime jan 7 and jan 8
    day1 = Day(name="Tuesday", date=datetime.now(), meal_plan_id=meal_plan.id)
    day2 = Day(name="Wednesday", date=datetime.now(), meal_plan_id=meal_plan.id)
    # associate the days with the meal plan
    meal_plan.days.append(day1)
    meal_plan.days.append(day2)
    db.session.commit()
    # Add a meal to each day
    meal1 = Meal(name="Breakfast", day_id=day1.id)
    # Add number of people and prep time and cuisine to the meal
    meal1.num_people = 2
    meal1.prep_time = 30
    meal1.cuisine = "Italian"

    meal2 = Meal(name="Lunch", day_id=day1.id)
    meal2.num_people = 2
    meal2.prep_time = 30
    meal2.cuisine = "Italian"

    meal3 = Meal(name="Dinner", day_id=day1.id)
    meal3.num_people = 2
    meal3.prep_time = 30
    meal3.cuisine = "Italian"

    meal4 = Meal(name="Breakfast", day_id=day2.id)
    meal4.num_people = 2
    meal4.prep_time = 30
    meal4.cuisine = "Israeli"

    meal5 = Meal(name="Lunch", day_id=day2.id)
    meal5.num_people = 2
    meal5.prep_time = 30
    meal5.cuisine = "Italian"

    meal6 = Meal(name="Dinner", day_id=day2.id)
    meal6.num_people = 2
    meal6.prep_time = 30
    meal6.cuisine = "Chinese"

    db.session.add(meal1)
    db.session.add(meal2)
    db.session.add(meal3)
    db.session.add(meal4)
    db.session.add(meal5)
    db.session.add(meal6)
    db.session.commit()

    return meal_plan

