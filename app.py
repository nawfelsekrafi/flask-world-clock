from flask import Flask, request, render_template
import requests
import logging
import time
from elasticsearch import Elasticsearch

app = Flask(__name__)

app.logger.setLevel(logging.INFO)
handler = logging.FileHandler('app.log')
app.logger.addHandler(handler)

es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])  # Update with your Elasticsearch host and port

@app.route("/")
def home():

    return render_template("home.html")

@app.route("/search", methods=["POST"])
def search():
    start_time = time.time()
    print(start_time);  
    # Get the search query
    query = request.form["q"]

    # Pass the search query to the Nominatim API to get a location
    location = requests.get(
        "https://nominatim.openstreetmap.org/search",
        {"q": query, "format": "json", "limit": "1"},
    ).json()

    # If a location is found, pass the coordinate to the Time API to get the current time
    if location:
        coordinate = [location[0]["lat"], location[0]["lon"]]

        response = requests.get(
            "https://timeapi.io/api/Time/current/coordinate",
            {"latitude": coordinate[0], "longitude": coordinate[1]},
        )
        duration = time.time() - start_time

        es.index(index='flask-logs', body={
            'query': query,
            'duration': duration,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'status': 'success'
        })

        app.logger.info('Search took %s seconds', duration)
        return render_template("success.html", location=location[0], time=response.json())

    # If a location is NOT found, return the error page
    else:
        duration = time.time() - start_time
        es.index(index='flask-logs', body={
            'query': query,
            'duration': duration,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'status': 'fail'
        })
        app.logger.info('Search took %s seconds', duration)
        return render_template("fail.html")
