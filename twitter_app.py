from flask import Flask, render_template, redirect, request, jsonify
import pandas as pd
import jinja2
import csv

app = Flask(__name__)
app.config.from_object(__name__)
from streaming import run_streaming
from followers import  getTwitterFollowers
from tweets import get_all_tweets
from twitter_analyze import run_analysis

t_id = "hunasotak"
start_date = "2017-5-10"
end_date = "2017-5-31"
hashtag = "teamlovematters"

# ROUTES:

@app.route('/')
def index():
	return render_template('index.html.jinja',summary = summary)

@app.route('/tweets', methods = ['GET','POST'])
def tweets():
	global t_id
	t_id = request.form["t_id"]
	get_all_tweets(t_id)
	return render_template('index.html.jinja',summary = summary)

@app.route('/tweets_follower', methods = ['GET','POST'])
def tweets_follower():
	t_id_follower = request.form["t_id_follower"]
	getTwitterFollowers(t_id)
	return render_template('index.html.jinja',summary = summary)

@app.route('/processdate', methods = ['POST'])
def processdate():
	if request.method == 'POST':
		global start_date
		start_date = request.form["start"]
		global end_date
		end_date = request.form["end"]
	return render_template('index.html.jinja',summary = summary)

	return jsonify({'error': 'Missing either start date or end date'})

@app.route('/hashtag', methods = ['POST'])
def hashtag():
	global hashtag
	hashtag = request.form["hashtag"]
	run_streaming(hashtag)
	return render_template('index.html.jinja',summary = summary)

@app.route('/kickoff', methods = ['GET','POST'])
def kickoff():
	run_analysis(t_id, start_date, end_date)
	summary = pd.read_csv('%s_tweets_analysis.csv' % t_id)
	return render_template('index.html.jinja', summary = summary)

@app.route('/overview/<t_id>')
def overview(t_id):
	summary = pd.read_csv('%s_tweets_analysis.csv' % t_id)
	return render_template('overview.html.jinja', summary = summary)

if __name__ == "__main__":

	summary = pd.read_csv("lovemafrica_tweets_analysis.csv")

	app.run(host='127.0.0.1', port=54992, debug=True)
