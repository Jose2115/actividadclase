import boto3

def crear_sitio():
    dynamo = boto3.resource('dynamodb', region_name='us-east-1')
    tabla = dynamo.Table('actividadestados')
    
    # "Escaneamos" la tabla para traer todo
    respuesta = tabla.scan()
    items = respuesta.get('Items', [])

    # Construimos el HTML
    html = "<html><body style='font-family: sans-serif; text-align: center;'>"
    html += "<h1>Resultados del Pipeline</h1><ul>"
    
    for i in items:
        html += f"<li>Estado: {i['EstadoID']}</li>"
        
    html += "</ul></body></html>"

    with open("index.html", "w") as f:
        f.write(html)
    print("Página index.html generada.")

if __name__ == "__main__":
    crear_sitio()