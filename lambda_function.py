import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # ← cambia tu región si es diferente
tabla    = dynamodb.Table('actividadestados')


def decimal_a_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    try:
        params       = event.get('queryStringParameters') or {}
        estado_query = params.get('estado', '').strip()
        min_aloj     = params.get('min_aloj')
        max_aloj     = params.get('max_aloj')
        min_transp   = params.get('min_transp')
        max_transp   = params.get('max_transp')
        min_temp     = params.get('min_temp')
        max_temp     = params.get('max_temp')
        min_hum      = params.get('min_hum')
        max_hum      = params.get('max_hum')

        hay_filtros_numericos = any([min_aloj, max_aloj, min_transp, max_transp,
                                     min_temp, max_temp, min_hum, max_hum])

        # ── CASO 1: Búsqueda exacta por clave de partición (EstadoID) ────────
        # Si el usuario escribió un estado completo y sin filtros numéricos,
        # usamos get_item (más rápido y eficiente)
        if estado_query and not hay_filtros_numericos:
            respuesta = tabla.get_item(Key={'EstadoID': estado_query})
            item = respuesta.get('Item')
            if item:
                items = [item]
            else:
                # Si no coincidió exacto, hacemos scan parcial
                items = scan_con_filtros(estado_query, min_aloj, max_aloj,
                                         min_transp, max_transp,
                                         min_temp, max_temp,
                                         min_hum, max_hum)

        # ── CASO 2: Filtros numéricos o búsqueda parcial → scan con filtros ──
        else:
            items = scan_con_filtros(estado_query, min_aloj, max_aloj,
                                     min_transp, max_transp,
                                     min_temp, max_temp,
                                     min_hum, max_hum)

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


def scan_con_filtros(estado_query, min_aloj, max_aloj,
                     min_transp, max_transp,
                     min_temp, max_temp,
                     min_hum, max_hum):
    """
    Escanea la tabla aplicando FilterExpression en DynamoDB.
    Más eficiente que traer todo y filtrar en Python.
    """
    filtros = []

    # Búsqueda parcial por EstadoID (contains)
    if estado_query:
        filtros.append(Attr('EstadoID').contains(estado_query))

    # Rangos numéricos
    if min_aloj:
        filtros.append(Attr('Costo_Alojamiento').gte(Decimal(min_aloj)))
    if max_aloj:
        filtros.append(Attr('Costo_Alojamiento').lte(Decimal(max_aloj)))
    if min_transp:
        filtros.append(Attr('Costo_Transporte').gte(Decimal(min_transp)))
    if max_transp:
        filtros.append(Attr('Costo_Transporte').lte(Decimal(max_transp)))
    if min_temp:
        filtros.append(Attr('Temperatura').gte(Decimal(min_temp)))
    if max_temp:
        filtros.append(Attr('Temperatura').lte(Decimal(max_temp)))
    if min_hum:
        filtros.append(Attr('Humedad').gte(Decimal(min_hum)))
    if max_hum:
        filtros.append(Attr('Humedad').lte(Decimal(max_hum)))

    # Combinar todos los filtros con AND
    if filtros:
        expresion = filtros[0]
        for f in filtros[1:]:
            expresion = expresion & f
        kwargs = {'FilterExpression': expresion}
    else:
        kwargs = {}

    # Escanear con paginación automática
    respuesta = tabla.scan(**kwargs)
    items = respuesta['Items']
    while 'LastEvaluatedKey' in respuesta:
        respuesta = tabla.scan(ExclusiveStartKey=respuesta['LastEvaluatedKey'], **kwargs)
        items.extend(respuesta['Items'])

    return items