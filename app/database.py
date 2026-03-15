from sqlmodel import create_engine, SQLModel, Session
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    db_host: str
    db_port: str
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # Configuración moderna para Pydantic V2
    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore"
    )

settings = Settings()

# El motor (engine) se encarga de la comunicación con la base de datos
engine = create_engine(settings.database_url)

# Crea todas las tablas definidas en los modelos que heredan de SQLModel
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Generador que provee una sesión de base de datos para cada petición
# Se asegura de cerrar la sesión automáticamente al terminar
def get_session():
    with Session(engine) as session:
        yield session