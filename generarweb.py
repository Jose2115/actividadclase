import boto3
import json
from decimal import Decimal

def convertir_decimal(obj):
    """Convierte Decimal a float para que json.dump no truene"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Tipo no serializable: {type(obj)}")

def crear_sitio():
    try:
        dynamo = boto3.resource('dynamodb', region_name='us-east-1')
        tabla  = dynamo.Table('actividadestados')

        # Escaneo con paginación completa
        respuesta = tabla.scan()
        items = respuesta.get('Items', [])

        while 'LastEvaluatedKey' in respuesta:
            respuesta = tabla.scan(ExclusiveStartKey=respuesta['LastEvaluatedKey'])
            items.extend(respuesta.get('Items', []))

        print(f"✅ {len(items)} estados obtenidos de DynamoDB")

        # Guardar como JSON para que index.html lo consuma
        with open("/var/www/html/datos.json", "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2, default=convertir_decimal)

        print("✅ datos.json guardado en /var/www/html/datos.json")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    crear_sitio()