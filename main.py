from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict
import aiomysql

from urllib.parse import parse_qs,unquote

app = FastAPI()

# NECESARIO PARA LA CONEXIÓN A LA BASE DE DATOS
DATABASE_USER = "admin"
DATABASE_PASSWORD = "iker12122002"
DATABASE_HOST = "database-iot.cipkgcowlii2.us-east-1.rds.amazonaws.com"
DATABASE_NAME = "TFT_IOT"
DATABASE_TABLE = "dataSensores"

# Configuración de la conexión a la base de datos
db_config = {
    'user': DATABASE_USER,
    'password': DATABASE_PASSWORD,
    'host': DATABASE_HOST,  # Puede ser una dirección IP o un nombre de host
    'db': DATABASE_NAME
}
# Modelo de datos de entrada
class InputData(BaseModel):
    monoxido_de_carbono: float
    luz: float
    presion: float
    altitud: float
    temperatura: float
    humedad: float
class GetData(BaseModel):
    numeroRegistros: int

def parse_query_string(query_string: str) -> Dict[str, float]:
    params = parse_qs(query_string)
    parsed_data = {key: float(value[0]) for key, value in params.items()}
    return parsed_data

# Función para insertar datos en la base de datos
async def insert_data(input_data: InputData):
    connection = await aiomysql.connect(**db_config)
    async with connection.cursor() as cursor:
        try:
            insert_query = """
                INSERT INTO dataSensores (monoxido_de_carbono, luz, presion, altitud, temperatura, humedad) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            await cursor.execute(insert_query, (
                input_data.monoxido_de_carbono, 
                input_data.luz, 
                input_data.presion, 
                input_data.altitud, 
                input_data.temperatura, 
                input_data.humedad
            ))
            await connection.commit()
            return True
        except Exception as e:
            print(f"EROR: {e}")
            await connection.rollback()
            return False
        finally:
            connection.close()

# Función para obtener datos de la base de datos (últimos n registros)
async def get_data(n=1):
    connection = await aiomysql.connect(**db_config)
    async with connection.cursor() as cursor:
        try:
            select_query = f"SELECT * FROM {DATABASE_TABLE} ORDER BY timestamp DESC LIMIT {n}"
            await cursor.execute(select_query)
            data = await cursor.fetchall()
            return data
        except Exception as e:
            print(f"ERROR: {e}")
            return None
        finally:
            connection.close()

@app.post("/insertData/")
async def input_data(request: Request):
    try:
        query_string = await request.body()
        query_decode = unquote(query_string.decode())
        # Crear un diccionario de los datos decodificados
        input_dict = {kv.split('=')[0]: float(kv.split('=')[1]) for kv in query_decode.split('&')}

        # Crear un objeto InputData a partir del diccionario
        input_data = InputData(**input_dict)
        result = await insert_data(input_data)
        if result:
            return {"message": "Data inserted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Error inserting data")
    
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/getData")
async def get_data_HTTP(request: Request):
    try:
        query_string = await request.body()
        query_decode = unquote(query_string.decode())
        # Crear un diccionario de los datos decodificados
        input_dict = {kv.split('=')[0]: float(kv.split('=')[1]) for kv in query_decode.split('&')}

        # Crear un objeto GetData a partir del diccionario
        input_data = GetData(**input_dict)
        # Obtener los datos de la base de datos
        result = await get_data(input_data.numeroRegistros)
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Error retrieving data")
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))