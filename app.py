# import necessary libraries
import json
from flask import (
    Flask,
    render_template,
    jsonify,
    request)
import scrape_mars as scrp
import pymongo


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


@app.route("/scrape")
def scrape_mars_data():
    result=scrp.scrape()
    return main()


@app.route("/")
def main():
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.mission_to_mars_db
    collection = db.items
    mars_dataset = db.items.find()
    return render_template("index.html",mars_data=mars_dataset[0])


if __name__ == "__main__":
    app.run(debug=True)
