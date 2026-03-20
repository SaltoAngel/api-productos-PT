from sqlmodel import create_engine, SQLModel, Session
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DB_HOST: str
    DB_PORT: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Configuración moderna para Pydantic V2
    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore"
    )

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
