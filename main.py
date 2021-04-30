from flask import Flask, render_template, request, redirect, url_for, session

import requests
import boto3

# from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

app = Flask(__name__)
app.secret_key = 'af2ea574685f5a205b976c9e4a'

counter = 0
user_flag = 0

### LOGIN PAGE ###
@app.route('/', methods=['GET', 'POST'])
def login(dynamodb=None):
	error_message = None
	error = None
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		if not dynamodb:
			dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
		
		table = dynamodb.Table('login')

		# fetch currentUser details
		currentUser_Data = fetch_userData(table, email)

		if currentUser_Data['Items']:
			for user in currentUser_Data['Items']:
				currentUserEmail = user['email']
				currentPassword = user['password']
				currentUsername = user['user_name']

				if password == currentPassword:
					session['username'] = currentUsername
					session['counter'] = 0
					session['user_flag'] = 0
					return redirect(url_for('home'))
				else:
					error_message = "ID or password is Invalid"
		else:
			error_message = "ID or password is Invalid"	
	return render_template('index.html', error=error_message)

def fetch_userData(table, email):
	response = table.query(KeyConditionExpression=Key('email').eq(email))
	return response

###REGISTRATION PAGE###
@app.route('/registration', methods=['GET', 'POST'])
def registration(dynamodb=None):
	error = None
	if request.method == 'POST':
		email = request.form['email']
		username = request.form['username']
		password = request.form['password']

		if not dynamodb:
			dynamodb = boto3.resource('dynamodb', region_name='us-east-1')	
		table = dynamodb.Table('login')

		current_UserEmail = check_email(table, email)

		current_Username = check_username(username)

		if current_UserEmail:
			error = 'UserID exists'
			return render_template('registration.html', error=error)
		else:
			table.put_item(
				Item={
						'email': email,
						'user_name': username,
						'password': password
					}
				)
			return redirect(url_for('login'))

	return render_template('registration.html', error=error)

def check_email(table, email):
	response = table.query(KeyConditionExpression=Key('email').eq(email))
	return response['Items']

### HOME PAGE ###
@app.route('/home', methods=['GET', 'POST'])
def home(dynamodb=None):
	error_message = None
	query_Results = " "
	if 'username' in session:
		currentUser = session['username']

		if not dynamodb:
			dynamodb = boto3.resource('dynamodb')

		if request.method == 'POST' and  'searchForm' in request.form:
			song_title = request.form['title']
			song_year = request.form['year']
			song_artist = request.form['artist']

			
			music_table = dynamodb.Table('music')

			if song_title and song_year and song_artist:
				query_Results = fetch_MusicInfo(music_table, song_title, song_year, song_artist)
			elif song_title and song_year:
				query_Results = fetch_TitleAndYear(music_table, song_title, song_year)
			elif song_title and song_artist:
				query_Results = fetch_TitleAndArtist(music_table, song_title, song_artist)
			elif song_year and song_artist:
				query_Results = fetch_YearAndArtist(music_table, song_year, song_artist)
			elif song_title:
				query_Results = fetch_InfoByTitle(music_table, song_title)
			elif song_year:
				query_Results = fetch_InfoByYear(music_table, song_year)
			elif song_artist:
				query_Results = fetch_InfoByArtist(music_table, song_artist)
			else:
				error_message = "NOT FOUND"	

		# if not dynamodb:
		# 	dynamodb = boto3.resource('dynamodb')	
		subscriptions_table = dynamodb.Table('subscriptions')
		my_subscriptions = fetch_UserSubscriptions(subscriptions_table, currentUser)
		artist_img = "https://s3820702-artist-images.s3.amazonaws.com/"

		if request.method == 'POST' and 'editForm' in request.form:
			remove_Subscription = subscriptions_table.delete_item(
					Key={
						'user_name': session['username'],
						'title': request.form['title']
					}
				)
			return redirect(url_for('home'))

		if request.method == 'POST' and 'addSubs' in request.form:
			add_Subscription = subscriptions_table.put_item(
				Item={
						'user_name': session['username'],
						'title': request.form['title'],
						'year': request.form['year'],
						'artist': request.form['artist']
					}
				)
			return redirect(url_for('home'))

		return render_template('home.html', error=error_message, currentUser=currentUser, subscriptions=my_subscriptions, artist_img=artist_img, searchResults=query_Results)
	return redirect(url_for('login'))

def fetch_MusicInfo(table, title, year, artist):
	response = table.scan(
		FilterExpression=Attr('title').eq(title) & Attr('year').eq(year) & Attr('artist').eq(artist)
		)
	return response['Items']

def fetch_TitleAndYear(table, title, year):
	response = table.scan(
		FilterExpression=Attr('title').eq(title) & Attr('year').eq(year)
		)
	return response['Items']

def fetch_TitleAndArtist(table, title, artist):
	response = table.scan(
		FilterExpression=Attr('title').eq(title) & Attr('artist').eq(artist)
		)
	return response['Items']

def fetch_YearAndArtist(table, year, artist):
	response = table.scan(
		FilterExpression=Attr('year').eq(year) & Attr('artist').eq(artist)
		)
	return response['Items']

def fetch_InfoByTitle(table, title):
	response = table.scan(
		FilterExpression=Attr('title').eq(title)
		)
	return response['Items']

def fetch_InfoByYear(table, year):
	response = table.scan(
		FilterExpression=Attr('year').eq(year)
		)
	return response['Items']	

def fetch_InfoByArtist(table, artist):
	response = table.scan(
		FilterExpression=Attr('artist').eq(artist)
		)
	return response['Items']

def fetch_UserSubscriptions(table, currentUser):
	response = table.query(KeyConditionExpression=Key('user_name').eq(currentUser))
	return response['Items']


### LOGOUT PAGE ###
@app.route('/logout', methods=['GET', 'POST'])
def logout():
	session.pop('username', None)
	return redirect(url_for('login'))

### APP RUN ###
if __name__ == '__main__':	
	app.run(host='0.0.0.0')
