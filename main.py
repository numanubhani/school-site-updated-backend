from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid
import string
import random

from database import engine, Base, get_db
import models
import schemas
import auth

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="EduXcel API")

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_random_password(length=10):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for i in range(length))

def get_current_user(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except auth.JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/register/principal", response_model=schemas.UserResponse)
def register_principal(user: schemas.UserCreate, school: schemas.SchoolCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create the user
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        uid=str(uuid.uuid4()),
        email=user.email,
        hashed_password=hashed_password,
        display_name=user.display_name,
        role="principal"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create the school
    invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    new_school = models.School(
        name=school.name,
        address=school.address,
        phone=school.phone,
        invite_code=invite_code,
        principal_id=new_user.id
    )
    db.add(new_school)
    db.commit()
    db.refresh(new_school)

    # Link school to user
    new_user.school_id = new_school.id
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/register/parent", response_model=schemas.UserResponse)
def register_parent(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        uid=str(uuid.uuid4()),
        email=user.email,
        hashed_password=hashed_password,
        display_name=user.display_name,
        role="parent"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/schools/my", response_model=schemas.SchoolResponse)
def get_my_school(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.school_id:
        raise HTTPException(status_code=404, detail="No school associated with this user")
    school = db.query(models.School).filter(models.School.id == current_user.school_id).first()
    return school

# Principal routes for adding users
@app.post("/schools/my/teachers", response_model=dict)
def add_teacher(user_data: schemas.UserBase, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "principal":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    generated_password = generate_random_password()
    hashed_password = auth.get_password_hash(generated_password)
    
    new_user = models.User(
        uid=str(uuid.uuid4()),
        email=user_data.email,
        hashed_password=hashed_password,
        display_name=user_data.display_name,
        role="teacher",
        school_id=current_user.school_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"user": new_user, "generated_password": generated_password}

@app.get("/schools/my/teachers", response_model=list[schemas.UserResponse])
def get_teachers(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "principal":
        raise HTTPException(status_code=403, detail="Not authorized")
    teachers = db.query(models.User).filter(models.User.school_id == current_user.school_id, models.User.role == "teacher").all()
    return teachers

@app.post("/schools/my/students", response_model=dict)
def add_student(user_data: schemas.UserBase, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "principal":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    generated_password = generate_random_password()
    hashed_password = auth.get_password_hash(generated_password)
    
    new_user = models.User(
        uid=str(uuid.uuid4()),
        email=user_data.email,
        hashed_password=hashed_password,
        display_name=user_data.display_name,
        role="student",
        school_id=current_user.school_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"user": new_user, "generated_password": generated_password}

@app.post("/schools/my/classes", response_model=schemas.ClassResponse)
def create_class(class_data: schemas.ClassCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "principal":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_class = models.Class(
        name=class_data.name,
        school_id=current_user.school_id,
        teacher_id=class_data.teacher_id
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class

@app.get("/schools/my/classes", response_model=list[schemas.ClassResponse])
def get_classes(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    classes = db.query(models.Class).filter(models.Class.school_id == current_user.school_id).all()
    return classes

@app.get("/")
def read_root():
    return {"message": "EduXcel API is running"}
