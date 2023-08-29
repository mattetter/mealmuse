# conversion_table.py

conversion_table = {
    "tsp": {
        "tbsp": 0.3333,
        "cup": 0.0208,
        "ml": 5,
        "l": 0.005,
        "g": 5,  # assuming conversion for sugar/salt-like consistency
        "oz": 0.1666,
        "teaspoon": 1,
        "tablespoon": 3,
        "teaspoons": 1
    },
    "teaspoon": {
        "tbsp": 0.3333,
        "cup": 0.0208,
        "ml": 5,
        "l": 0.005,
        "g": 5,  # assuming conversion for sugar/salt-like consistency
        "oz": 0.1666,
        "teaspoons": 1,
        "tablespoon": 3,
        "tsp": 1
    },
    "tablespoon": {
        "tsp": 0.3333,
        "cup": 0.0208,
        "ml": 5,
        "l": 0.005,
        "g": 5,  # assuming conversion for sugar/salt-like consistency
        "oz": 0.1666,
        "teaspoons": 1,
        "teaspoon": 1,
        "tbsp": 1
    },

    "tablespoons": {
        "tsp": 0.3333,
        "cup": 0.0208,
        "ml": 5,
        "l": 0.005,
        "g": 5,  # assuming conversion for sugar/salt-like consistency
        "oz": 0.1666,
        "teaspoons": 1,
        "teaspoon": 1,
        "tbsp": 1
    },

    "tbsp": {
        "tsp": 3,
        "cup": 0.0625,
        "ml": 15,
        "l": 0.015,
        "g": 15,  # assuming conversion for sugar/salt-like consistency
        "oz": 0.5,
        "teaspoons": 3,
        "teaspoon": 3,
        "tablespoon": 1

    },
    "cup": {
        "tsp": 48,
        "tbsp": 16,
        "ml": 240,
        "l": 0.24,
        "g": 240,  # assuming conversion for water-like consistency
        "oz": 8,
        "cups": 1,
        "pint": 0.5,
        "quart": 0.25,
        "gallon": 0.125

    },

    "cups": {
        "tsp": 48,
        "tbsp": 16,
        "ml": 240,
        "l": 0.24,
        "g": 240,  # assuming conversion for water-like consistency
        "oz": 8,
        "cup": 1,
        "pint": 0.5
    },
    "ml": {
        "tsp": 0.2,
        "tbsp": 0.0666,
        "cup": 0.0042,
        "l": 0.001,
        "g": 1,  # assuming conversion for water-like consistency
        "oz": 0.0333
    },
    "l": {
        "tsp": 200,
        "tbsp": 66.6666,
        "cup": 4.1666,
        "ml": 1000,
        "g": 1000,  # assuming conversion for water-like consistency
        "oz": 33.3333
    },
    "g": {
        "tsp": 0.2,
        "tbsp": 0.0666,
        "cup": 0.0042,
        "ml": 1,
        "l": 0.001,
        "oz": 0.0333
    },
    "oz": {
        "tsp": 6,
        "tbsp": 2,
        "cup": 0.125,
        "ml": 30,
        "l": 0.03,
        "g": 30  # assuming conversion for sugar/salt-like consistency
    },
    "pinch": {
        "tsp": 0.0625,
        "tbsp": 0.0208,
        "cup": 0.0013,
        "ml": 0.3125,
        "l": 0.0003,
        "g": 0.3125,  # assuming conversion for sugar/salt-like consistency
        "oz": 0.0104
    },
    "dash": {
        "tsp": 0.125,
        "tbsp": 0.0416,
        "cup": 0.0026,
        "ml": 0.625,
        "l": 0.0006,
        "g": 0.625,  # assuming conversion for sugar/salt-like consistency
        "oz": 0.0208
    },
    "smidgen": {
        "tsp": 0.03125,
        "tbsp": 0.0104,
        "cup": 0.00065,
        "ml": 0.15625,
        "l": 0.00015,
        "g": 0.15625,  # assuming conversion for sugar/salt-like consistency
        "oz": 0.0052
    },
    "drop": {
        "tsp": 0.0625,
        "tbsp": 0.0208,
        "cup": 0.0013,
        "ml": 0.3125,
        "l": 0.0003,
        "g": 0.3125,  # assuming conversion for water-like consistency
        "oz": 0.0104
    },
    "piece": {
        "tsp": 0.0625,
        "tbsp": 0.0208,
        "cup": 0.0013,
        "ml": 0.3125,
        "l": 0.0003,
        "g": 0.3125,  # assuming conversion for water-like consistency
        "oz": 0.0104
    },
    "can": {
        "cup": 2,
        "oz": 12,
        "ml": 500,
        "l": 0.5,
        "g": 500,  # assuming conversion for water-like consistency
        "pint": 1,
        "quart": 0.5,
        "gallon": 0.25
    },
    "pint": {
        "cup": 2,
        "oz": 16,
        "ml": 500,
        "l": 0.5,
        "g": 500,  # assuming conversion for water-like consistency
        "can": 1,
        "quart": 0.5,
        "gallon": 0.25
    },

    "quart": {
        "cup": 4,
        "oz": 32,
        "ml": 1000,
        "l": 1,
        "g": 1000,  # assuming conversion for water-like consistency
        "can": 2,
        "pint": 2,
        "gallon": 0.5
    },
    "gallon": {
        "cup": 16,
        "oz": 128,
        "ml": 4000,
        "l": 4,
        "g": 4000,  # assuming conversion for water-like consistency
        "can": 8,
        "pint": 8,
        "quart": 4
    },

    "can": {

        "cup": 2,
        "oz": 12,
        "ml": 500,
        "l": 0.5,
        "g": 500,  # assuming conversion for water-like consistency
        "pint": 1,
        "quart": 0.5,
        "gallon": 0.25
    },
    "pints": {
        "cup": 2,
        "oz": 16,
        "ml": 500,
        "l": 0.5,
        "g": 500,  # assuming conversion for water-like consistency
        "can": 1,
        "quart": 0.5,
        "gallon": 0.25
    },

    "quarts": {
        "cup": 4,
        "oz": 32,
        "ml": 1000,
        "l": 1,
        "g": 1000,  # assuming conversion for water-like consistency
        "can": 2,
        "pint": 2,
        "gallon": 0.5
    },

    "gallons": {    
        "cup": 16,

        "oz": 128,
        "ml": 4000,


        "l": 4,
        "g": 4000,  # assuming conversion for water-like consistency
        "can": 8,
        "pint": 8,
        "quart": 4

    },

    "pinches": {
        "tsp": 0.0625,
        "tbsp": 0.0208,
        "cup": 0.0013,
        "ml": 0.3125,
        "l": 0.0003,
        "g": 0.3125,  # assuming conversion for sugar/salt-like consistency
        "oz": 0.0104
    },

    "dashes": {
        "tsp": 0.125,
        "tbsp": 0.0416,
        "cup": 0.0026,
        "ml": 0.625,
        "l": 0.0006,
        "g": 0.625,  # assuming conversion for sugar/salt-like consistency
        "oz": 0.0208
    },

    "smidgens": {
        "tsp": 0.03125,
        "tbsp": 0.0104,
        "cup": 0.00065,
        "ml": 0.15625,
        "l": 0.00015,
        "g": 0.15625,  # assuming conversion for sugar/salt-like consistency
        "oz": 0.0052
    },

    "drops": {
        "tsp": 0.0625,
        "tbsp": 0.0208,
        "cup": 0.0013,
        "ml": 0.3125,
        "l": 0.0003,
        "g": 0.3125,  # assuming conversion for water-like consistency
        "oz": 0.0104
    },

    "pieces": {
        "tsp": 0.0625,
        "tbsp": 0.0208,
        "cup": 0.0013,
        "ml": 0.3125,
        "l": 0.0003,
        "g": 0.3125,  # assuming conversion for water-like consistency
        "oz": 0.0104
    },

    "cans": {
        "cup": 2,
        "oz": 12,
        "ml": 500,
        "l": 0.5,
        "g": 500,  # assuming conversion for water-like consistency
        "pint": 1,
        "quart": 0.5,
        "gallon": 0.25
    },

    "pints": {
        "cup": 2,
        "oz": 16,
        "ml": 500,
        "l": 0.5,
        "g": 500,  # assuming conversion for water-like consistency
        "can": 1,
        "quart": 0.5,
        "gallon": 0.25
    },

    

    # ... add more as needed
}
