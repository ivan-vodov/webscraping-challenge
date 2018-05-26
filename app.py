# import necessary libraries
import json
from flask import (
    Flask,
    render_template,
    jsonify,
    request)
import scrape_mars as scrp
import pymongo

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.mission_to_mars_db
collection = db.items

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/scrape")
def scrape_mars_data():
    global db

    result_message='<div class="alert alert-success" role="alert">New data scraped successfully.</div>' 
    try:
        scrp.scrape(db)
    except BaseException as e:
        result_message='<div class="alert alert-danger" role="alert">'+str(e)+'</div>'
    
    mars_dataset = db.items.find()
    return render_template("index.html",mars_data=mars_dataset[0], result_message=result_message)


@app.route("/")
def main():
    global db
    mars_dataset = db.items.find()
    return render_template("index.html",mars_data=mars_dataset[0])


if __name__ == "__main__":
    app.run(debug=True)
