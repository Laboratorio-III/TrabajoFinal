from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
import sqlite3
from uwuclasses import ApiManager
import os

# Definición de la configuración de autenticación JWT
class Settings(BaseModel):
    authjwt_secret_key: str = "churrito"
    authjwt_access_token_expires = 3600


app = FastAPI()

# Conexión a la base de datos SQLite
conn = sqlite3.connect('uwudatabase.db')
cursor = conn.cursor()

# Creación del objeto ApiManager
manager = ApiManager(cursor=cursor, conn=conn)

# Ruta para autenticación de usuarios
@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.post("/authentication")
async def authentication(user_data: dict, Authorize: AuthJWT = Depends()):
    response = manager.authentication(user_data=user_data)
    access_token = Authorize.create_access_token(subject=user_data['username'])
    response['access_token'] = access_token
    return response

# Ruta para agregar una tarea
@app.post("/addtask")
async def add_task(task_data: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return manager.add_task(task_data=task_data)

# Ruta para buscar una tarea
@app.post("/search")
async def search_task(task_id: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return manager.search_task(task_id=task_id)

# Ruta para eliminar una tarea


@app.post("/delete")
async def delete_task(task_id: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return manager.delete_task(task_id=task_id)

# Ruta para actualizar el estado de una tarea


@app.post("/update")
async def update_state(task_data: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return manager.update_state(task_data=task_data)

# Ruta para obtener todas las tareas de un usuario


@app.get("/tasks")
async def get_tasks(user_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return manager.get_tasks(user_id=user_id)

# Ejecución del servidor usando Uvicorn
if __name__ == "__main__":
    os.system('python -m uvicorn uwuapi:app --reload')
