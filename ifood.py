from postman import postman

with open("ifood.json","r") as arquivo:
    postman_collection : postman = postman("Ifood","b",arquivo.read())
    postman_collection.collection
    postman_collection.processar()
