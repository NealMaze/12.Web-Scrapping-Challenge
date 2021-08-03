from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
from scrapper import scrape

urls = ["https://mars.nasa.gov/news/",
        "https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html",
        "https://space-facts.com/mars/",
        "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"]

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_db"
mongo = PyMongo(ap)

@app.route("/")

def index():
    tab = mongo.db.articles.find_one()
    ret = render_template("index.html", mars = tab)
    return ret

@app.route("/scrapper")

def scrapper():
    mars_data = scrape(urls)
    mongo.db.articles.update({}, mars_data, upsert = True)
    ret = redirect("/", code = 302)
    return ret

if __name__ == "__main__": app.run()