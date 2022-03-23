from configparser import ConfigParser
import os

from pymongo import MongoClient
import streamlit as st

def config(section):
    filename = '.streamlit/secrets.toml'
    if os.path.isfile(filename):
        parser = ConfigParser()
        parser.read(filename)
        creds = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                creds[param[0]] = param[1]   
            return creds    
        else:
            raise Exception('No section named', section)
    else:
        raise Exception('No file named', filename)

def get_mongo_client(streamlit = True):
    if streamlit:
        client = MongoClient(st.secrets['mongo'])
    else:
        credentials = config('mongo')
        client = MongoClient(credentials['host'].replace('"','').strip())
    return client

def get_spoonacular_key():
    return config('spoonacular')['key'].replace('"','').strip()