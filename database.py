from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import  os
from dotenv import load_dotenv
load_dotenv()

password=os.environ['PASSWORD']
URL_DATABASE=f"postgresql://postgres:{password}@db.tcksranmbkqttezzyccl.supabase.co:5432/postgres"
engine = create_engine(URL_DATABASE)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine,autocommit=False,autoflush=False)
