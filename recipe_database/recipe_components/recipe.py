import pymongo
class Recipe():
    def __init__(self, url, title, ingredients, category, website):
        self.url = url
        self.title = title
        self.ingredients = ingredients
        self.category = category
        self.website = website
    
    def get_dictionary(self):
        properties = {  
                        'url': self.url,
                        'title': self.title,
                        'ingredients': self.ingredients,
                        'category': self.category,
                        'website': self.website
                     }
        return properties
    
    def insert_into_mongo_db(self, db, replace = True):
        document = self.get_dictionary()
        try:
            if replace:
                result = db.recipes.replace_one({'url':self.url},document,upsert=True)
                inserted_id = None
                # if type(result) == pymongo.results.UpdateResult:
                #     inserted_id = None
                # else:
                #     inserted_id = db.recipes.replace_one({'url':self.url},document,upsert=True).get('inserted_id')
            else:
                inserted_id = db.recipes.insert_one(document).inserted_id
            return 'success', inserted_id, None
        except Exception as e:
            return 'error', None, str(e)