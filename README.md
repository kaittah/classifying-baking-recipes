# classifying-baking-recipes
Have you ever wondered if your cupcake recipe is really a muffin recipe in disguise? This project aims to show the relationship between a user-input recipe and other recipes for baked goods. 

There is a hosted Streamlit app here: https://share.streamlit.io/kaittah/classifying-baking-recipes

## Data Collection
Over 1000 recipes and 60 common ingredients for baked goods are entered into a MongoDB database to build the dataset. 
<code>collect_ingredients.py</code> uses Spoonacular's API to find unit conversions from cups and other units to grams as well as the nutritional breakdown of common ingredients.
<code>collect_recipes.py</code> scrapes recipes from three websites to collect recipes. The recipes' categories are set using the search parameters. For example, if a recipe is found in the bread category of a website of by searching for bread recipes, it is classified as bread. 

## Classifying User Input
<code>streamlit_app.py</code> contains the main app. A user inputs a recipe, the recipe undergoes parsing and standardization, and the function in <code>build_dataset.py</code> constructs an array giving the recipe's overall fraction by weight of protein, sugar, other carbohydrates, unsaturated fat, saturated fat, water, and 61 common baking ingredients. A matrix of of this information is constructed using data in MongoDB so that the user input may be compared against over 1000 others. The 3 nearest neighbors are found and displayed in the app along with charts comparing the nutrient and ingredient breakdowns of the user input and its nearest neighbor. If a recipe has 2 or more neighbors that are in the same recipe category, then the recipe will be classified as that recipe category. Otherwise, classification is inconclusive.

![Streamlit-Interface](https://github.com/kaittah/classifying-baking-recipes/blob/master/images/screenshot.png?raw=true)

## Configuration
Install requirements using <code>pipenv install</code>. Save a file called <code>secrets.toml</code> in the folder called .streamlit. The secrets file requires the following information:
````
[mongo]
host = "<connection_string>"
[spoonacular]
key = "<api-key>"
````
## Tests
The tests folder contains tests that are intended for pytest. The types of tests are as follows:
1. Test convert to grams - Using given ingredient information, assess that the conversion from a unit to grams is correct.
2. Test nutrients breakdown - Using given ingredient information, assess that the grams of each macro-nutrient are correctly calculated from the overall ingredient weight and nutrient fractions.
3. Test mongo connection - Pings the MongoDB database
4. Test spoonacular connection - Asserts that a status code of 200 results when calling the Spoonacular API
5. Test ingredient - Assesses that a string containing the amount, unit, and name of an ingredient is successfully broken down into its three parts
6. Test standardize ingredient - Assesses that the ingredient amount, unit, and name are properly cleaned up, handling different formats of fractions and units
7. Test main ingredient - Assesses that Spoonacular gives the correct information about an ingredient
8. Test ingredient features - Checks MongoDB data to ensure no fractions are negative
9. Test url scraping - Assesses that webscraping succeeds in retreiving recipe urls from a page
10. Test recipe scraping - Assesses that given a url, the correct ingredients are scraped
