import altair as alt
import blinker
import numpy as np
from sklearn.neighbors import KDTree
import streamlit as st
from annotated_text import annotated_text
import graphviz
import pandas as pd
import pymongo

from recipe_database.recipe_components.ingredient import Ingredient
from recipe_database.recipe_components.recipe import Recipe
from recipe_database.utils.build_dataset import get_dataset

st.set_page_config(layout="wide")

client = pymongo.MongoClient(st.secrets["mongo"]["host"])
db = client.recipe_analysis

@st.cache(hash_funcs={pymongo.database.Database: id, "_thread.RLock": lambda _: None, "blinker_saferef.BoundMethodWeakref": lambda _: None, blinker.base.Signal: lambda _: None, "_secrets": lambda _: None }, allow_output_mutation=False)
def get_data(recipe_id=None):
    X, categories, recipe_strings, titles, urls, ids = get_dataset(db,recipe_id=recipe_id)
    return X, categories, recipe_strings, titles, urls, ids

@st.cache()
def get_KD_tree(X):
    return KDTree(X, leaf_size=10) 

@st.cache()
def get_nearest_neighbors(tree, x, n):
    dist, ind = tree.query(x, k=n) 
    return dist, ind

@st.cache()
def get_feature_labels():
    ingredients_list = [ 'almond flour', 'flour', 'water', 'sugar', 'peanut butter', 'unsalted butter', 'oil', 'evaporated milk', 
        'sweetened condensed milk', 'buttermilk', 'milk', 'sour cream', 'heavy cream', 'half-and-half', 'juice', 
        'honey', 'syrup', 'yogurt', 'oats', 'cocoa', 'unsweetened chocolate', 'white chocolate', 'semisweet chocolate chips', 
        'canned pumpkin', 'mashed banana', 'applesauce', 'corn starch', 'corn meal', 'egg', 'molasses', 'shortening', 
        'crisco', 'shredded coconut', 'zucchini', 'carrot', 'apple', 'berries', 'raisins', 'walnut', 'pecans', 
        'pistachio', 'potato', 'cinnamon', 'allspice', 'zest', 'nutmeg', 'ginger', 'cloves', 'spice', 'vanilla', 'yeast', 
        'baking soda', 'baking powder', 'salt', 'cream of tartar', 'vinegar', 'almond extract', 'rhubarb',
        'sprinkles', 'instant coffee']
    feat_cols = ['protein_fraction', 'unsaturated_fat_fraction', 'saturated_fat_fraction', 'sugar_carbohydrates_fraction',
                        'other_carbohydrates_fraction']
    feat_cols.extend([s.replace(' ', '_') for s in ingredients_list])
    return feat_cols

@st.cache(hash_funcs={pymongo.database.Database: id, "_thread.RLock": lambda _: None, "blinker_saferef.BoundMethodWeakref": lambda _: None, blinker.base.Signal: lambda _: None, "_secrets": lambda _: None }, allow_output_mutation=False)
def parse_input_recipe(db, input_text):
    ingredients = input_text.split('\n')
    butter_count = 0
    cleaned_ingredients = []
    labeled_ingredients = []
    for ingredient in ingredients:
        cleaned_ingredient = Ingredient(ingredient.strip())
        if cleaned_ingredient.name == 'unsalted butter':
            if butter_count > 0:
                previous_ingredient = cleaned_ingredients[-1]
                if previous_ingredient['name'] in ['cream cheese', 'sugar']:
                    cleaned_ingredients.pop()
                break
            else:
                butter_count += 1
        cleaned_ingredients.append(cleaned_ingredient.get_dictionary())
        labeled_ingredients.append(cleaned_ingredient.get_labeling())
    recipe = Recipe(None, None, cleaned_ingredients, None, 'User Input')
    status, document_id, error = recipe.insert_into_mongo_db(db, replace=False)
    x, _, _, _, _, _ = get_data(document_id)
    if status == 'success':
        return labeled_ingredients, x, error
    else:
        return None, None, error

def analyze_input():
    neighbor_count = 3
    labeled_ingredients, x, error = parse_input_recipe(db, st.session_state.recipe_input)
    feature_labels = get_feature_labels()
    feature_df = pd.DataFrame(x, columns=feature_labels)
    if error:
        st.write(error)
    else:
        X, categories, recipe_strings, titles, urls, ids = get_data()
        tree = get_KD_tree(X)
        try:
            dist, ind = get_nearest_neighbors(tree, x, neighbor_count)
        except:
            dist, ind = None, None
        if isinstance(ind, np.ndarray) and len(ind)>0:
            graph = graphviz.Digraph(node_attr={'shape':'egg', 'height':'1.5'})
            closest_neighbors_text = []
            category_counter = {}
            for index in ind[0]:
                category_counter[categories[index]] = category_counter.get(categories[index],0) + 1
                nearest_neighbor_title = f"{categories[index]}"
                graph.edge('User Input Recipe', nearest_neighbor_title)
                closest_neighbors_text.append(f'''{titles[index]}\n{urls[index]}\n\n{recipe_strings[index]}''')
            x_closest, _, _, _, _, _ = get_data(ids[ind[0][0]])
            features_of_closest = pd.DataFrame(x_closest, columns=feature_labels)
            classification = 'The type of recipe could not be determined.'
            for key, count in category_counter.items():
                if count >= neighbor_count/2:
                    classification = 'This is a recipe for a ' + key
            classification_slot.text(classification)
        else:
            graph = None
            features_of_closest = None
            closest_neighbors_text = None
    return feature_df, graph, labeled_ingredients, features_of_closest, closest_neighbors_text


col1, col2, col3 = st.columns(3)
submitted = False

with col1:
    with st.form('recipe_form'):
        classification_slot = st.empty()
        st.text_area('Enter a Recipe', height=350,value="""
        2 cups all-purpose flour
        ¾ teaspoon baking soda
        ½ teaspoon salt
        3 medium bananas, mashed
        ½ cup creamy peanut butter
        ½ cup granulated sugar
        ½ cup light brown sugar
        ⅓ cup buttermilk
        ¼ cup vegetable oil
        2 eggs
        2 teaspoons vanilla extract
        1 cup semisweet chocolate chips""", key='recipe_input')
        submitted = st.form_submit_button("Submit")

if submitted:

    feature_df, graph, labeled_ingredients, features_of_closest, closest_neighbors_text = analyze_input()
    with col1:
        for ingredient_label in labeled_ingredients:
                    if ingredient_label and len(ingredient_label)> 0:
                        annotated_text(
                            *ingredient_label
                        )
    with col2:
        st.write('Nutrition breakdown (fraction by weight)')
        nutrition_data = feature_df.iloc[:,:5].transpose().reset_index()
        nutrition_data.columns = ['nutrient', 'fraction']
        nutrition_data_closest = features_of_closest.iloc[:,:5].transpose().reset_index()
        nutrition_data_closest.columns = ['nutrient', 'fraction']
        nutrition_data['recipe'] = 'User Input Recipe'
        nutrition_data_closest['recipe'] = 'Nearest Neighbor'
        bars = alt.Chart(pd.concat([nutrition_data, nutrition_data_closest])).mark_bar(opacity=0.7).encode(
            x=alt.X('fraction', stack=None),
            y=alt.Y('nutrient'),
            color='recipe'
        )
        text = bars.mark_text(
            align='left',
            baseline='middle',
            dx=3
        )
        st.altair_chart(bars)

        st.write('Ingredient breakdown (fraction by weight)')
        ingredient_data = feature_df.iloc[:,5:].transpose().reset_index()
        ingredient_data.columns = ['ingredient', 'fraction']
        ingredient_data_closest = features_of_closest.iloc[:,5:].transpose().reset_index()
        ingredient_data_closest.columns = ['ingredient', 'fraction']
        ingredient_data['recipe'] = 'User Input Recipe'
        ingredient_data_closest['recipe'] = 'Nearest Neighbor'
        ingred_bars = alt.Chart(pd.concat([ingredient_data, ingredient_data_closest])).mark_bar(opacity=0.7).encode(
            x=alt.X('fraction', stack=None),
            y=alt.Y(
                    'ingredient',
                    sort=alt.EncodingSortField(
                        field='fraction',
                        order='descending'
                    )
                ),
            color='recipe'
        ).configure_axisX(orient='top')
        ingred_text = ingred_bars.mark_text(
            align='left',
            baseline='middle',
            dx=3 
        )
        st.altair_chart(ingred_bars)

    with col3:
        if graph:
            st.graphviz_chart(graph, use_container_width=True)
        else:
            st.write('No similar recipes')
        for i, neighbor_text in enumerate(closest_neighbors_text):
            st.write(f'*Nearest Neighbor {i+1}*')
            st.write(f'{neighbor_text}')