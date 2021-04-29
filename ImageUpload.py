import json
import boto3
import requests

s3 = boto3.resource('s3')

def image_Download(music_info):
	for image in music_info['songs']:
		img_url = image['img_url']
		artist = img_url.split('/')[::-1][0]

		fetch_image = requests.get(img_url, stream=True)
		image_obj = fetch_image.raw
		req_data = image_obj.read()
		s3.Bucket('s3820702-artist-images').put_object(Key=artist, Body=req_data)
		print("Adding music:", img_url, artist)	


if __name__ == '__main__':
	with open("a2.json") as json_file:
		music_info = json.load(json_file)
	image_Download(music_info)	