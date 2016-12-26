import feedparser
import datetime

from flask import make_response
from flask import Flask
from flask import render_template
from flask import request

import json
# import urllib2
import urllib
from urllib.request import urlopen


app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
			'cnn': 'http://rss.cnn.com/rss/edition.rss',
			'fox': 'http://feeds.foxnews.com/foxnews/latest',
			'iol': 'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication':'bbc', 'city':'Riverside,US', 'currency_from':'CNY', 'currency_to':'USD'}

weather_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=28ab5b993f79f08d312759cf2a8ade4f"
currency_url = "https://openexchangerates.org//api/latest.json?app_id=5f72b684fb0c4a68aa3d438ebd940352"


@app.route("/")
def home():
	# get customized headlines, based on user input or default
	publication = get_value_with_fallback("publication")
	articles = get_news(publication)

	# get customized weather based on user input or default
	city = get_value_with_fallback("city")
	weather = get_weather(city)

	# get customized currency based on user input or default
	currency_from = get_value_with_fallback("currency_from")
	currency_to = get_value_with_fallback("currency_to")
	rate, currencies = get_rate(currency_from, currency_to)


	# return render_template("home.html", articles=articles, weather=weather, 
	# 		currency_from=currency_from, currency_to=currency_to, rate=rate, currencies=sorted(currencies))
	
	response = make_response(
		render_template(
			"home.html",
			articles=articles,
			weather=weather,
			currency_from=currency_from,
			currency_to=currency_to,
			rate=rate,
			currencies=sorted(currencies)
			)
		)

	expires = datetime.datetime.now()+datetime.timedelta(days=365)
	response.set_cookie("publication",publication,expires=expires)
	response.set_cookie("city",city,expires=expires)
	response.set_cookie("currency_from",currency_from,expires=expires)
	response.set_cookie("currency_to",currency_to,expires=expires)

	return response

def get_value_with_fallback(key):
	if request.args.get(key):
		return request.args.get(key)

	if request.cookies.get(key):
		return request.cookies.get(key)

	return DEFAULTS[key]

def get_news(query):
	if not query or query.lower() not in RSS_FEEDS:
		publication = DEFAULTS["publication"]
	else:
		publication = query.lower()
	feed = feedparser.parse(RSS_FEEDS[publication])
	return feed['entries']

def get_weather(query) :
	query = urllib.parse.quote(query)
	url = weather_url.format(query)
	data = urllib.request.urlopen(url).read().decode('utf-8')
	# str_data = data.readall().decode('utf-8')
	parsed = json.loads(data)
	weather = None
	if parsed.get("weather") :
		weather = {
					"description":parsed["weather"][0]["description"],
					"temperature":parsed["main"]["temp"],
					"city":parsed["name"],
					"country": parsed['sys']['country']
				  }
	return weather

def get_rate(frm, to) :
	all_currency = urllib.request.urlopen(currency_url).read().decode('utf-8')
	parsed = json.loads(all_currency).get('rates')
	frm_rate = parsed.get(frm.upper())
	to_rate = parsed.get(to.upper())
	return (to_rate/frm_rate, parsed.keys())

	# # first_article = feed['entries'][0]
	# return render_template("home.html", article=first_article)

	# return render_template("home.html",
 #                            title=first_article.get("title"),
 #                            published=first_article.get("published"),
 #                            summary=first_article.get("summary")
							
	# return """<html>
	#  <body>
	#   		<h1> Headlines </h1>
	#   		<b>{0}</b> <br/>
	#   		<i>{1}</i> <br/>
	#   		<p>{2}</p> <br/>
	#   </body>		
 #  </html>""".format(first_article.get("title"), first_article.get("published"), first_article.get("summary"))
  
if __name__ == '__main__':
	app.run(port=5000, debug=True)