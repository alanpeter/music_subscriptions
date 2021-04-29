import boto3

def create_MusicTable(dynamodb = None):
	if not dynamodb:
		dynamodb = boto3.resource('dynamodb')
		table = dynamodb.create_table(
			TableName = 'music',
			KeySchema=[
				{

				'AttributeName': 'title',

				'KeyType': 'HASH' # Partition key

				},

				{

				'AttributeName': 'artist',

				'KeyType': 'RANGE' # Sort key

				}

			],

			AttributeDefinitions=[

				{

				'AttributeName': 'title',

				'AttributeType': 'S'

				},

				{

				'AttributeName': 'artist',

				'AttributeType': 'S'

				},

			],

			ProvisionedThroughput={

				'ReadCapacityUnits': 10,

				'WriteCapacityUnits': 10

			}

		)

		return table

if __name__ == '__main__':
	music_table = create_MusicTable()

	print("Table status:", music_table.table_status)

# title, artist, year, web_url, image_url