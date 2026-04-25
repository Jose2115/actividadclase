import json
import boto3
from decimal import Decimal

# ⚠️ Cambia la región si es diferente a us-east-1
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
tabla    = dynamodb.Table('actividadestados')


def decimal_a_float(obj):
    """Convierte Decimal a float para que json.dumps pueda serializarlo."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    try:
        # Obtener parámetros de búsqueda opcionales desde query string
        params       = event.get('queryStringParameters') or {}
        estado_query = params.get('estado', '').strip().lower()
        min_aloj     = params.get('min_aloj')
        max_aloj     = params.get('max_aloj')
        min_transp   = params.get('min_transp')
        max_transp   = params.get('max_transp')
        min_temp     = params.get('min_temp')
        max_temp     = params.get('max_temp')
        min_hum      = params.get('min_hum')
        max_hum      = params.get('max_hum')

        # Escanear toda la tabla (con paginación automática)
        respuesta = tabla.scan()
        items     = respuesta['Items']
        while 'LastEvaluatedKey' in respuesta:
            respuesta = tabla.scan(ExclusiveStartKey=respuesta['LastEvaluatedKey'])
            items.extend(respuesta['Items'])

        # ── Filtros aplicados en Python ──────────────────────────────────────

        # Filtro por nombre de estado (búsqueda parcial, sin importar mayúsculas)
        if estado_query:
            items = [i for i in items
                     if estado_query in str(i.get('EstadoID', '')).lower()]

        # Filtro por rango de Costo_Alojamiento
        if min_aloj:
            items = [i for i in items if float(i.get('Costo_Alojamiento', 0)) >= float(min_aloj)]
        if max_aloj:
            items = [i for i in items if float(i.get('Costo_Alojamiento', 0)) <= float(max_aloj)]

        # Filtro por rango de Costo_Transporte
        if min_transp:
            items = [i for i in items if float(i.get('Costo_Transporte', 0)) >= float(min_transp)]
        if max_transp:
            items = [i for i in items if float(i.get('Costo_Transporte', 0)) <= float(max_transp)]

        # Filtro por rango de Temperatura
        if min_temp:
            items = [i for i in items if float(i.get('Temperatura', 0)) >= float(min_temp)]
        if max_temp:
            items = [i for i in items if float(i.get('Temperatura', 0)) <= float(max_temp)]

        # Filtro por rango de Humedad
        if min_hum:
            items = [i for i in items if float(i.get('Humedad', 0)) >= float(min_hum)]
        if max_hum:
            items = [i for i in items if float(i.get('Humedad', 0)) <= float(max_hum)]

        # Ordenar por EstadoID
        items.sort(key=lambda x: str(x.get('EstadoID', '')))

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin':  '*',
                'Access-Control-Allow-Methods': 'GET,OPTIONS',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(items, default=decimal_a_float)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }