from sqlalchemy import create_engine


def test_postgres_driver_is_importable():
    # create_engine inaingiza dereva mara moja, kwa hiyo inashika
    # mabadiliko kama SQLAlchemy 2.1 kutaka psycopg badala ya psycopg2
    engine = create_engine("postgresql://u:p@localhost:5432/db")
    assert engine.dialect.driver
