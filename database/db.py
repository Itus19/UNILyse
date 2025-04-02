from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    faculte = Column(String)
    semestre = Column(String)
    cursus = Column(String)
    credits = Column(Integer)
    nom = Column(String)
    globale = Column(Float)
    travail = Column(Integer)
    difficulte = Column(Integer)
    interet = Column(Integer)

engine = create_engine("sqlite:///unilyse.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
