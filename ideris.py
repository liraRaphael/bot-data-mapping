from postman import postman

with open("ideris3.json","r") as arquivo:
    postman_collection : postman = postman("Ideris","A",arquivo.read())
    postman_collection.processar()
