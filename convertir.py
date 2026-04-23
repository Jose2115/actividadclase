import boto3

def txt_a_dynamo():
    # Conexión a DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    tabla = dynamodb.Table('actividadestados')

    with open('Estados.txt', 'r') as f:
        for linea in f:
            nombre_estado = linea.strip()
            if nombre_estado:
                # El formato JSON que pide DynamoDB
                tabla.put_item(Item={
                    'EstadoID': nombre_estado,
                    'Detalles': 'Procesado por Pipeline'
                })
    print("Datos cargados exitosamente.")

if __name__ == "__main__":
    txt_a_dynamo()