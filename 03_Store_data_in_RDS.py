!pip install psycopg2-binary
import pandas as pd

from sqlalchemy import create_engine
engine = create_engine("postgresql+psycopg2://postgres:kingdiamond@database-1.cricm4dcssbs.us-east-2.rds.amazonaws.com/postgres", echo=True)


dataset = pd.read_csv("20220228_hotels.csv")[["name","description","score","address","latitude","longitude","short_url"]]



from sqlalchemy import Table, Column, Integer, String, Float, MetaData, ForeignKey

meta = MetaData()

# Define table "Hotels"
Hotels = Table(
    'hotels', meta, 
    Column('id', Integer, primary_key = True), 
    Column('name', String), 
    Column('description', String), 
    Column('score', Float),
    Column('address', String),
    Column('latitude', String),
    Column('longitude', String),
    Column('short_url', String)
)
meta.create_all(engine)

dataset.to_sql(
    "Hotels",
    engine
)