from webbrowser import get
from recipe_database.recipe_components.main_ingredient import MainIngredient

from recipe_database.utils.connect import get_mongo_client

def test_main_ingredient():
    '''
    Ensure correct properties are retrieved for an ingredient
    '''
    flour = MainIngredient('flour')
    properties = flour.get_dictionary()
    assert properties['grams_in_cup'] == 125
    assert 'grams_in_ml' not in properties.keys()
    assert properties['grams_in_tsp'] == 2
    assert properties['nutrition_data']['amount'] == 1000
    nutrient_names = [nutrient['name'] for nutrient in properties['nutrition_data']['nutrition']['nutrients']]
    assert set(["Protein","Saturated Fat","Fat","Carbohydrates","Sugar"]).issubset(set(nutrient_names))
    assert len(nutrient_names) == len(set(nutrient_names))


def test_ingredient_features():
    '''
    Query MongoDB to ensure no negative values
    '''
    client = get_mongo_client(streamlit=False)
    db = client.recipe_analysis
    assert db.ingredient_features.count_documents({'grams_in_cup': {'$lt':0}}) == 0
    assert db.ingredient_features.count_documents({'grams_in_ml': {'$lt':0}}) == 0
    assert db.ingredient_features.count_documents({'grams_in_whole': {'$lt':0}}) == 0
    assert db.ingredient_features.count_documents({'other_carbohydrates_fraction': {'$lt':0}}) == 0
    assert db.ingredient_features.count_documents({'protein_fraction': {'$lt':0}}) == 0
    assert db.ingredient_features.count_documents({'saturated_fat_fraction': {'$lt':0}}) == 0
    assert db.ingredient_features.count_documents({'sugar_carbohydrates_fraction': {'$lt':0}}) == 0
    assert db.ingredient_features.count_documents({'unsaturated_fat_fraction': {'$lt':0}}) == 0
    assert db.ingredient_features.count_documents({'water_fraction': {'$lt':0}}) == 0
