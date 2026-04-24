import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # ← cambia tu región si es diferente
tabla    = dynamodb.Table('actividadestados')

def lambda_handler(event, context):
    try:
        # Escanea todos los items de la tabla
        respuesta = tabla.scan()
        items     = respuesta['Items']

        # Si hay más páginas (paginación automática)
        while 'LastEvaluatedKey' in respuesta:
            respuesta = tabla.scan(ExclusiveStartKey=respuesta['LastEvaluatedKey'])
            items.extend(respuesta['Items'])

        # Convierte Decimal a float (DynamoDB devuelve Decimal)
        items_serializables = json.loads(
            json.dumps(items, default=str)
        )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',       # CORS para el navegador
                'Access-Control-Allow-Methods': 'GET',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(items_serializables)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }