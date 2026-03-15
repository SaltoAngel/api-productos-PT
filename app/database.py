from sqlmodel import create_engine, SQLModel, Session
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()

# El motor (engine) se encarga de la comunicación con la base de datos
engine = create_engine(settings.DATABASE_URL)

# Crea todas las tablas definidas en los modelos que heredan de SQLModel
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Generador que provee una sesión de base de datos para cada petición
# Se asegura de cerrar la sesión automáticamente al terminar
def get_session():
    with Session(engine) as session:
        yield session