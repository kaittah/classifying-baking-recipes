import pymongo
import requests

from recipe_database.utils.connect import get_mongo_client, get_spoonacular_key

def test_mongo_connection_1():
    client = get_mongo_client()
    client.admin.command('ping')
    assert isinstance(client, pymongo.MongoClient)

def test_mongo_connection_2():
    client = get_mongo_client(streamlit=False)
    client.admin.command('ping')
    assert isinstance(client, pymongo.MongoClient)

def test_spoonacular_connection():
    api_key = get_spoonacular_key()
    response = requests.get(f'https://api.spoonacular.com/food/jokes/random?apiKey={api_key}')
    assert response.status_code == 200
