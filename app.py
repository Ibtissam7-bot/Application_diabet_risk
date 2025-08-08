# app.py

from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, delete # Importe delete pour la suppression
from sqlalchemy.exc import IntegrityError
import secrets
from joblib import load # Utilise joblib.load au lieu de pickle.load
import numpy as np # Pour pr\u00E9parer les donn\u00E9es pour le mod\u00E8le ML

from database import engine, SessionLocal, get_db, metadata # Importe metadata et engine
from models import doctors, patients, predictions # Importe les objets Table d\u00E9finis
from auth import hash_password, verify_password

# Cr\u00E9e toutes les tables d\u00E9finies dans metadata
metadata.create_all(engine)

app = FastAPI()

# Configuration des templates Jinja2
templates = Jinja2Templates(directory="templates")

# Configuration des fichiers statiques (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Cl\u00E9 secr\u00E8te pour les sessions (\u00E0 g\u00E9n\u00E9rer de mani\u00E8re s\u00E9curis\u00E9e en production)
SECRET_KEY = secrets.token_hex(32)

# Charger le mod\u00E8le de Machine Learning au d\u00E9marrage de l'application
# Assurez-vous que 'diabetes_model.pkl' est \u00E0 la racine de votre projet DiabetoWeb
try:
    with open('diabetes_model.pkl', 'rb') as f:
        ml_model = load(f) # Utilise joblib.load
    print("Mod\u00E8le de Machine Learning charg\u00E9 avec succ\u00E8s.")
except FileNotFoundError:
    print("Erreur: Le fichier 'diabetes_model.pkl' n'a pas \u00E9t\u00E9 trouv\u00E9.")
    ml_model = None # Le mod\u00E8le sera None si le fichier n'est pas trouv\u00E9
except Exception as e:
    print(f"Erreur lors du chargement du mod\u00E8le ML: {e}")
    ml_model = None


# D\u00E9pendance pour obtenir l'utilisateur (m\u00E9decin) actuellement connect\u00E9
async def get_current_doctor_core(request: Request, db: Session = Depends(get_db)):
    doctor_id = request.cookies.get("doctor_id")
    if doctor_id:
        # Utilisation de SQLAlchemy Core pour s\u00E9lectionner le m\u00E9decin
        stmt = select(doctors).where(doctors.c.id == int(doctor_id))
        result = db.execute(stmt).first() # 'db' est utilis\u00E9 ici
        if result:
            # Retourne le Row object, tu peux acc\u00E9der aux colonnes via ._asdict() ou par attribut
            return result._asdict() # Convertit le Row en dictionnaire pour un acc\u00E8s facile
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Non authentifie",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Redirige l'utilisateur vers la page de connexion par d\u00E9faut.
    """
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request, error_message: str = None):
    """
    Affiche le formulaire de connexion.
    """
    return templates.TemplateResponse("login.html", {"request": request, "error_message": error_message})

@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """
    Gere la soumission du formulaire de connexion.
    Verifie les identifiants et redirige vers la page d'accueil ou affiche un message d'erreur.
    """
    # Importe la fonction ici pour eviter les problemes de dependance circulaire
    from auth import verify_password 

    # Utilisation de SQLAlchemy Core pour selectionner le medecin par nom d'utilisateur
    stmt = select(doctors).where(doctors.c.username == username)
    doctor_row = db.execute(stmt).first()

    if not doctor_row or not verify_password(password, doctor_row.password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error_message": "Nom d'utilisateur ou mot de passe incorrect."},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="doctor_id", value=str(doctor_row.id), httponly=True, secure=False, max_age=3600) # Cookie de session 1 heure
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request, error_message: str = None):
    """
    Affiche le formulaire d'inscription.
    """
    return templates.TemplateResponse("register.html", {"request": request, "error_message": error_message})

@app.post("/register", response_class=HTMLResponse)
async def register_submit(request: Request,
                          username: str = Form(...),
                          email: str = Form(...),
                          password: str = Form(...),
                          confirm_password: str = Form(...),
                          db: Session = Depends(get_db)):
    """
    Gere la soumission du formulaire d'inscription.
    Cree un nouveau compte medecin si les informations sont valides.
    """
    # Importe la fonction ici pour eviter les problemes de dependance circulaire
    from auth import hash_password 

    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_message": "Les mots de passe ne correspondent pas."},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    hashed_pwd = hash_password(password)

    # Utilisation de SQLAlchemy Core pour inserer un nouveau medecin
    insert_stmt = insert(doctors).values(
        username=username,
        email=email,
        password=hashed_pwd
    )

    try:
        db.execute(insert_stmt)
        db.commit()
        # Rediriger vers la page de connexion apres une inscription reussie
        return RedirectResponse(url="/login?message=inscription_reussie", status_code=status.HTTP_302_FOUND)
    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_message": "Ce nom d'utilisateur ou e-mail existe d\u00E9j\u00E0."},
            status_code=status.HTTP_409_CONFLICT
        )

@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request, current_doctor: dict = Depends(get_current_doctor_core)):
    """
    Page d'accueil apr\u00E8s authentification reussie.
    """
    # current_doctor est maintenant un dictionnaire 
    return templates.TemplateResponse("home.html", {"request": request, "doctor": current_doctor})

@app.post("/logout")
async def logout(request: Request):
    """
    D\u00E9connecte l'utilisateur en supprimant le cookie de session.
    """
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("doctor_id")
    return response

# --- Routes de gestion des patients ---

@app.get("/add_patient", response_class=HTMLResponse)
async def add_patient_form(request: Request,
                           current_doctor: dict = Depends(get_current_doctor_core),
                           success_message: str = None,
                           error_message: str = None):
    """
    Affiche le formulaire d'ajout de patient.
    """
    return templates.TemplateResponse(
        "add_patient.html",
        {"request": request, "doctor": current_doctor, "success_message": success_message, "error_message": error_message}
    )

@app.post("/add_patient", response_class=HTMLResponse)
async def add_patient_submit(request: Request,
                             current_doctor: dict = Depends(get_current_doctor_core),
                             name: str = Form(...),
                             age: int = Form(...),
                             sex: str = Form(...),
                             glucose: float = Form(...),
                             bmi: float = Form(...),
                             pedigree: float = Form(...),
                             db: Session = Depends(get_db)): # 'db' est d\u00E9fini ici
    """
    G\u00E8re la soumission du formulaire d'ajout de patient.
    Stocke les donn\u00E9es dans la base de donn\u00E9es et effectue la pr\u00E9diction.
    """
    if ml_model is None:
        return templates.TemplateResponse(
            "add_patient.html",
            {"request": request, "doctor": current_doctor, "error_message": "Le mod\u00E8le de pr\u00E9diction n'a pas pu \u00EAtre charg\u00E9. Impossible d'ajouter le patient."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Pr\u00E9parer les donn\u00E9es pour le mod\u00E8le de ML avec les caract\u00E9ristiques sp\u00E9cifi\u00E9es:
    # ["Glucose", "BMI", "Age", "DiabetesPedigreeFunction"]
    features = np.array([[glucose, bmi, age, pedigree]])

    # Effectuer la pr\u00E9diction
    prediction_result = ml_model.predict(features)[0] # [0] pour obtenir la valeur unique

    # Interpr\u00E9ter le r\u00E9sultat
    diabetes_status = 1 if prediction_result == 1 else 0 # 1 = diab\u00E9tique, 0 = non diab\u00E9tique

    # Ins\u00E9rer le patient dans la base de donn\u00E9es
    insert_patient_stmt = insert(patients).values(
        doctor_id=current_doctor["id"], # Utilise l'ID du m\u00E9decin connect\u00E9
        name=name,
        age=age,
        sex=sex,
        glucose=glucose,
        bmi=bmi,
        pedigree=pedigree,
        result=diabetes_status # Stocke le r\u00E9sultat de la pr\u00E9diction
    )

    try:
        db.execute(insert_patient_stmt)
        db.commit()

        success_message = f"Patient '{name}' ajout\u00E9 avec succ\u00E8s. Pr\u00E9diction: {'Diab\u00E9tique' if diabetes_status == 1 else 'Non diab\u00E9tique'}."
        return templates.TemplateResponse(
            "add_patient.html",
            {"request": request, "doctor": current_doctor, "success_message": success_message},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        db.rollback()
        error_message = f"Erreur lors de l'ajout du patient: {e}"
        return templates.TemplateResponse(
            "add_patient.html",
            {"request": request, "doctor": current_doctor, "error_message": error_message},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@app.get("/patients", response_class=HTMLResponse)
async def patients_list(request: Request,
                        current_doctor: dict = Depends(get_current_doctor_core),
                        success_message: str = None,
                        error_message: str = None,
                        sort_by: str = "created_at", # Param\u00E8tre pour le tri
                        order: str = "desc", # Ordre de tri (asc/desc)
                        db: Session = Depends(get_db)): # 'db' est d\u00E9fini ici
    """
    Affiche la liste des patients du m\u00E9decin connect\u00E9.
    """
    doctor_id = current_doctor["id"]

    # S\u00E9lectionne tous les patients du m\u00E9decin connect\u00E9
    stmt = select(patients).where(patients.c.doctor_id == doctor_id)
    
    # Ex\u00E9cute la requ\u00EAte
    result = db.execute(stmt).fetchall()
    
    # Convertit les Row objects en listes de dictionnaires pour Jinja2
    # et pour faciliter le tri en Python (si n\u00E9cessaire)
    all_patients = [patient._asdict() for patient in result]

    # Tri des patients en Python (car orderBy() est \u00E0 \u00E9viter pour les index manquants)
    if sort_by in ["name", "age", "glucose", "bmi", "pedigree", "result", "created_at"]:
        reverse_sort = (order == "desc")
        all_patients.sort(key=lambda p: p[sort_by] if p[sort_by] is not None else (float('-inf') if reverse_sort else float('inf')), reverse=reverse_sort)
        
    # Calcul de la statistique : % de patients diab\u00E9tiques
    total_patients = len(all_patients)
    diabetic_patients = sum(1 for p in all_patients if p['result'] == 0)
    diabetic_percentage = (diabetic_patients / total_patients * 100) if total_patients > 0 else 0

    return templates.TemplateResponse(
        "patients.html",
        {
            "request": request,
            "doctor": current_doctor,
            "patients": all_patients,
            "diabetic_percentage": diabetic_percentage,
            "success_message": success_message,
            "error_message": error_message
        }
    )

@app.post("/delete_patient/{patient_id}")
async def delete_patient(request: Request,
                         patient_id: int,
                         current_doctor: dict = Depends(get_current_doctor_core),
                         db: Session = Depends(get_db)): # 'db' est d\u00E9fini ici
    """
    Supprime un patient sp\u00E9cifique.
    """
    doctor_id = current_doctor["id"]

    # V\u00E9rifier si le patient existe et appartient bien au m\u00E9decin connect\u00E9
    stmt_select = select(patients).where(patients.c.id == patient_id, patients.c.doctor_id == doctor_id)
    patient_to_delete = db.execute(stmt_select).first()

    if not patient_to_delete:
        # Si le patient n'est pas trouv\u00E9 ou n'appartient pas au m\u00E9decin, rediriger avec une erreur
        return RedirectResponse(url="/patients?error_message=Patient non trouv\u00E9 ou vous n'\u00EAtes pas autoris\u00E9 \u00E0 le supprimer.", status_code=status.HTTP_302_FOUND)
    
    # Supprimer les pr\u00E9dictions associ\u00E9es \u00E0 ce patient (si la table predictions est utilis\u00E9e)
    # delete_predictions_stmt = delete(predictions).where(predictions.c.patient_id == patient_id)
    # db.execute(delete_predictions_stmt)

    # Supprimer le patient
    delete_patient_stmt = delete(patients).where(patients.c.id == patient_id)
    
    try:
        db.execute(delete_patient_stmt)
        db.commit()
        return RedirectResponse(url="/patients?success_message=Patient supprim\u00E9 avec succ\u00E8s.", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        db.rollback()
        return RedirectResponse(url=f"/patients?error_message=Erreur lors de la suppression du patient: {e}", status_code=status.HTTP_302_FOUND)

