import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.base import Base 

# Configuración de la base de datos de test.
DB_USER = os.getenv("DB_USER", "licium")
DB_PASSWORD = os.getenv("DB_PASSWORD", "licium_dev_password")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_TEST_NAME", "licium_test")

# Construyo la URL de conexión a la base de datos de testing
TEST_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


@pytest.fixture(scope="session")
def engine():
    """
    Aquí creo el engine de SQLAlchemy para toda la sesión de tests.
    Uso scope="session" porque no quiero crear el engine en cada test
    (sería muy lento).
    """
    return create_engine(TEST_DATABASE_URL, pool_pre_ping=True)


@pytest.fixture(scope="session")
def tables(engine):
    """
    Aquí limpio completamente el esquema public y vuelvo a crear todas las tablas.
    Esto garantiza que la base de datos de test esté limpia antes de empezar.
    """
    with engine.connect() as conn:
        # Borro el schema público completo (tablas, índices, constraints, etc.)
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
        
        # Vuelvo a crear el schema
        conn.execute(text("CREATE SCHEMA public;"))
        
        # Doy permisos (para evitar problemas de permisos en PostgreSQL)
        conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
        
        conn.commit()
    
    # Intento crear todas las tablas definidas en los modelos (Base.metadata)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # A veces, si un modelo se importa dos veces, intenta crear índices duplicados.
        # Si el error es "already exists", lo ignoro.
        if "already exists" in str(e):
            pass
        else:
            raise e

    # El yield hace que este fixture se ejecute antes de los tests
    # y luego continúe cuando los tests terminan.
    yield


@pytest.fixture()
def db_session(engine, tables):
    """
    Este fixture crea una sesión de base de datos para cada test.
    Pero lo importante es que uso una transacción que luego hago rollback,
    así cada test no ensucia la base de datos.
    """
    connection = engine.connect()
    
    # Empiezo una transacción
    transaction = connection.begin()
    
    # Creo una sesión vinculada a esa conexión
    Session = sessionmaker(bind=connection)
    session = Session()

    # Devuelvo la sesión al test
    yield session

    # Cuando el test termina, cierro todo y hago rollback
    # para que la base de datos vuelva a estar limpia.
    session.close()
    transaction.rollback()
    connection.close()