# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData # Nous aurons besoin de MetaData ici ou dans models.py

# Paramètres de connexion à la base de données
db_host = "localhost"
db_port = 5432
db_user = "postgres"
db_password = "azerty" 
db_name = "diabetoweb" 

# Construction de l'URL de connexion

db_URL= f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
# Créer le moteur de la base de données
engine = create_engine(db_URL)

# Créer une session locale pour interagir avec la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MetaData est nécessaire pour définir les tables avec SQLAlchemy Core
metadata = MetaData()
#Ce pattern assure une gestion propre de la connexion à la base de données : ouverture, utilisation, puis fermeture automatique.
# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
