from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from database import metadata # Importe l'objet metadata que nous avons défini dans database.py

# Définition de la table 'doctors' (inchangée)
doctors = Table(
    "doctors",
    metadata,
    Column("id", Integer, primary_key=True, unique=True, autoincrement=True),
    Column("username", String(255), unique=True, nullable=False),
    Column("email", String(255), unique=True, nullable=False),
    Column("password", String(255), nullable=False), # Le mot de passe haché
    Column("created_at", DateTime(timezone=True), server_default=func.now())
)

# Définition de la table 'patients' (bloodpressure retiré)
patients = Table(
    "patients",
    metadata,
    Column("id", Integer, primary_key=True, unique=True, autoincrement=True),
    Column("doctor_id", Integer, ForeignKey("doctors.id"), nullable=False), # Clé étrangère vers doctors
    Column("name", String(255), nullable=False),
    Column("age", Integer),
    Column("sex", String(10)), # 'M', 'F', 'Autre'
    Column("glucose", Integer),
    Column("bmi", Float), # IMC peut être un nombre décimal
    Column("pedigree", Float), # Fonction pedigree peut être un nombre décimal
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("result", Integer, nullable=True) # 0 = non diabétique, 1 = diabétique
)

# Définition de la table 'predictions' (inchangée)
predictions = Table(
    "predictions",
    metadata,
    Column("id", Integer, primary_key=True, unique=True, autoincrement=True),
    Column("patient_id", Integer, ForeignKey("patients.id"), nullable=False), # Clé étrangère vers patients
    Column("result", Integer, nullable=False), # Le résultat de la prédiction (0 ou 1)
    Column("created_at", DateTime(timezone=True), server_default=func.now())
)
