import boto3
import json
import logging
from decimal import Decimal
logger = logging.getLogger()
logger.setLevel (logging. INFO)
dynamodbTableName = 'product-inventory'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

#All the methods for severless api 
getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'


#All the paths for api 
healthPath = '/health'
productpath='/product'
productspath = '/products'


#main function where we are getting httpmethod and path according to that , calling the respective function
def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event["path"]
    if httpMethod =="GET" and path == healthPath:
        health_response = "Hii from server less api created by akram"
        response= build_response(200,health_response)
    elif httpMethod == getMethod and path == productpath:
        response = getProduct(event ['queryStringParameters']['productId'])
    elif httpMethod == getMethod and path == productspath:
        response = getProducts()
    elif httpMethod == postMethod and path == productpath:
        response = saveProduct(json.loads(event ['body' ]))
    elif httpMethod == patchMethod and path == productpath:
        requestBody = json.loads(event [ 'body'])
        response = modifyProduct(requestBody['productId'], requestBody['updateKey'], requestBody['updateValue'])
    elif httpMethod == deleteMethod and path == productpath:
        requestBody = json.loads(event ['body' ])
        response = deleteProduct(requestBody ['productId'])
    else:
       response = build_response (404, 'Not Found')
    return response



def getProduct(productId):

    try:
        response = table.get_item(
        Key={
                
            'productId': productId
            }
        )
        if 'Item' in response:
         return build_response (200, response['Item'])
        else:
         return build_response (404, {'Message': 'ProductId: %s not found' % productId})
    except:
     logger.exception ('Product is not available with the given product Id')


def getProducts():
    try:
        response = table.scan()
        result = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Items'])
            body = {
            'products': result
            }
        return build_response(200, body)
    except:
      logger.exception('Database is empty or there is some error while fetching the database.')
    


def saveProduct(requestBody):
    try:
        table.put_item(Item=requestBody)
        body = {
        'Operation': 'SAVE',
        'Message': 'SUCCESS',
        'Item': requestBody
        }
        return build_response (200, body)
    except:
     logger.exception ('Error while saving the product')

#added the item exists explicitely
def saveProduct(requestBody):
    try:
        # Check if item already exists
        response = table.get_item(Key={'productId': requestBody['productId']})
        if 'Item' in response:
            return build_response(400, {'Message': 'Item already exists in the database'})

        # Save the item
        table.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return build_response(200, body)
    except:
        logger.exception('Error while saving the product')

def modifyProduct (productId, updateKey, updateValue):
    try:
        response = table.update_item(
        Key={
        'productId': productId
        },
        UpdateExpression='set %s = :value' % updateKey,
        ExpressionAttributeValues={
        ':value': updateValue
        },
        ReturnValues='UPDATED_NEW'
        )
        body = {
        'Operation': 'UPDATE',
        'Message': 'SUCCESS',
        'UpdatedAttrebutes': response
        }
        return build_response (200, body)
    except:
      logger.exception ('Unable to update the product with given productId.')
                    
                    
                  
def deleteProduct (productId):
    try:
        response = table.delete_item(
        Key={
        'productId': productId 
        },
        ReturnValues='ALL_OLD'
        )
        body = {
        'Operation': 'DELETE',
        'Message': 'SUCCESS',
        'deletedItem': response
        }
        return build_response (200, body)
    except:
     logger.exception ('Error , While deleting the product !')


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Check if it's an int or a float
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        # Let the base class default method raise the TypeError
        return super(DecimalEncoder, self).default(obj)

def build_response(status_code, body=None):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }