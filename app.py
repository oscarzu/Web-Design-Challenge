from flask import Flask, render_template, redirect
import pymongo
from pymongo import MongoClient
import scrape
import os

# Create MongoDB connection; Create database and collection if it does not exist.
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client["mars_db"]
collection = db["marsdata"]

# Create an instance of Flask app
app = Flask(__name__)

@app.route("/")
def index():
    marsinfo = db.collection.find_one()
    return render_template("index.html", marsinfo=marsinfo)


@app.route("/scrape")
def scrape():
    marsinfo = db.collection
    mars_data = scrape.scrape()
    marsinfo.update(
        {},
        mars_data,
        upsert=True
    )
    return redirect("http://127.0.0.1:5000/", code=302)


if __name__ == "__main__":
    app.run(debug=True)

