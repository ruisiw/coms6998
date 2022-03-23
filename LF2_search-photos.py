import json
import boto3
import requests
from requests_aws4auth import AWS4Auth

session = boto3.Session()

def elastic_search(label):
    region = 'us-east-1'
    service = 'es'
    credentials = session.get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    host = 'https://search-photos-xxn7dfaw2j6jylhohlzkotcxji.us-east-1.es.amazonaws.com'
    index = 'photos'
    url = host + '/' + index + '/_search'
    query = {
      'query': {
        'multi_match': {
          'query': label,
          'fields': ['labels', 'x-amz-meta-customLabels']
        }
      }
    }
    headers = { "Content-Type": "application/json" }
    
    try:
        r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
        es_result = json.loads(r.text)
        print(es_result)
        es_res = es_result["hits"]["hits"]
        result = []
        for k in range(len(es_res)):
            result.append(es_res[k]['_source'])
        return result
    except Exception as axc:
        print(exc)
        return {
            'statusCode': 403,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            "isBase64Encoded": False,
            'body': json.dumps('No result from Elastic Search')
        }


def lambda_handler(event, context):
    print(event)
    
    client = session.client('lex-runtime')
    query = event['currentIntent']['slots']['Query']
    # response = client.post_text(
    #     botName = 'PhotosBot',
    #     botAlias = 'photos',
    #     userId = 'abccba',
    #     inputText = query)
    # print(response)
    
    search_res = elastic_search(query)
    print(search_res)
    
    # search_res = [{
    #     'objectKey': 'testimg.jpg',
    #     'bucket': 'b2photos',
    #     'labels': ['dogs']
    # }]
    photonames = []
    for item in search_res:
        if item['objectKey'] not in photonames:
            photonames.append(item['objectKey'])
    print(photonames)
    
    return {
        'statusCode': 200,
        'body': json.dumps(photonames)
    }
