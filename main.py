from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import timedelta
from pathlib import Path
import uuid, string, random, shutil

from database import engine, Base, get_db
import models, schemas, auth

models.Base.metadata.create_all(bind=engine)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="EduXcel API")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── helpers ──────────────────────────────────────────────────────────────────

def generate_password(length=10):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def get_current_user(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise exc
    except auth.JWTError:
        raise exc
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise exc
    return user

def require_role(user: models.User, *roles):
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="Not authorized")

# ── registration ─────────────────────────────────────────────────────────────

@app.post("/register/principal", response_model=schemas.UserResponse)
def register_principal(user: schemas.UserCreate, school: schemas.SchoolCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        uid=str(uuid.uuid4()), email=user.email,
        hashed_password=auth.get_password_hash(user.password),
        display_name=user.display_name, role="principal"
    )
    db.add(new_user); db.commit(); db.refresh(new_user)
    invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    new_school = models.School(name=school.name, address=school.address, phone=school.phone, invite_code=invite_code, principal_id=new_user.id)
    db.add(new_school); db.commit(); db.refresh(new_school)
    new_user.school_id = new_school.id
    db.commit(); db.refresh(new_user)
    return new_user

@app.post("/register/parent", response_model=schemas.UserResponse)
def register_parent(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        uid=str(uuid.uuid4()), email=user.email,
        hashed_password=auth.get_password_hash(user.password),
        display_name=user.display_name, role="parent"
    )
    db.add(new_user); db.commit(); db.refresh(new_user)
    return new_user

@app.post("/register/teacher", response_model=schemas.UserResponse)
def register_teacher(data: schemas.UserCreateWithCode, db: Session = Depends(get_db)):
    school = db.query(models.School).filter(models.School.invite_code == data.invite_code.upper()).first()
    if not school:
        raise HTTPException(status_code=404, detail="Invalid school invite code")
    if db.query(models.User).filter(models.User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        uid=str(uuid.uuid4()), email=data.email,
        hashed_password=auth.get_password_hash(data.password),
        display_name=data.display_name, role="teacher", school_id=school.id
    )
    db.add(new_user); db.commit(); db.refresh(new_user)
    return new_user

@app.post("/register/student", response_model=schemas.UserResponse)
def register_student(data: schemas.UserCreateWithCode, db: Session = Depends(get_db)):
    school = db.query(models.School).filter(models.School.invite_code == data.invite_code.upper()).first()
    if not school:
        raise HTTPException(status_code=404, detail="Invalid school invite code")
    if db.query(models.User).filter(models.User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        uid=str(uuid.uuid4()), email=data.email,
        hashed_password=auth.get_password_hash(data.password),
        display_name=data.display_name, role="student", school_id=school.id
    )
    db.add(new_user); db.commit(); db.refresh(new_user)
    return new_user

# ── auth ──────────────────────────────────────────────────────────────────────

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    token = auth.create_access_token(data={"sub": user.email, "role": user.role}, expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# ── school ────────────────────────────────────────────────────────────────────

@app.get("/schools/my", response_model=schemas.SchoolResponse)
def get_my_school(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.school_id:
        raise HTTPException(status_code=404, detail="No school associated with this user")
    return db.query(models.School).filter(models.School.id == current_user.school_id).first()

@app.patch("/schools/my", response_model=schemas.SchoolResponse)
def update_school(data: schemas.SchoolUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    school = db.query(models.School).filter(models.School.id == current_user.school_id).first()
    if not school: raise HTTPException(status_code=404, detail="School not found")
    if data.name is not None: school.name = data.name
    if data.address is not None: school.address = data.address
    if data.phone is not None: school.phone = data.phone
    db.commit(); db.refresh(school)
    return school

# ── principal: user management ────────────────────────────────────────────────

@app.post("/schools/my/teachers", response_model=dict)
def add_teacher(user_data: schemas.UserBase, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    pwd = generate_password()
    new_user = models.User(uid=str(uuid.uuid4()), email=user_data.email, hashed_password=auth.get_password_hash(pwd), display_name=user_data.display_name, role="teacher", school_id=current_user.school_id)
    db.add(new_user); db.commit(); db.refresh(new_user)
    return {"user": schemas.UserResponse.model_validate(new_user).model_dump(), "generated_password": pwd}

@app.get("/schools/my/teachers", response_model=list[schemas.UserResponse])
def get_teachers(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    return db.query(models.User).filter(models.User.school_id == current_user.school_id, models.User.role == "teacher").all()

@app.post("/schools/my/students", response_model=dict)
def add_student(user_data: schemas.UserBase, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    pwd = generate_password()
    new_user = models.User(uid=str(uuid.uuid4()), email=user_data.email, hashed_password=auth.get_password_hash(pwd), display_name=user_data.display_name, role="student", school_id=current_user.school_id)
    db.add(new_user); db.commit(); db.refresh(new_user)
    return {"user": schemas.UserResponse.model_validate(new_user).model_dump(), "generated_password": pwd}

@app.get("/schools/my/students", response_model=list[schemas.UserResponse])
def get_students(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    return db.query(models.User).filter(models.User.school_id == current_user.school_id, models.User.role == "student").all()

@app.delete("/schools/my/users/{user_id}", status_code=204)
def remove_user(user_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    user = db.query(models.User).filter(models.User.id == user_id, models.User.school_id == current_user.school_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user); db.commit()

@app.get("/schools/my/parents", response_model=list[schemas.UserResponse])
def get_school_parents(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    student_ids = [s.id for s in db.query(models.User).filter(models.User.school_id == current_user.school_id, models.User.role == "student").all()]
    parent_ids = list(set(l.parent_id for l in db.query(models.ParentStudent).filter(models.ParentStudent.student_id.in_(student_ids)).all()))
    return db.query(models.User).filter(models.User.id.in_(parent_ids)).all()

# ── classes ───────────────────────────────────────────────────────────────────

@app.post("/schools/my/classes", response_model=schemas.ClassResponse)
def create_class(class_data: schemas.ClassCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    new_class = models.Class(name=class_data.name, school_id=current_user.school_id, teacher_id=class_data.teacher_id)
    db.add(new_class); db.commit(); db.refresh(new_class)
    return new_class

@app.get("/schools/my/classes", response_model=list[schemas.ClassResponse])
def get_classes(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    classes = db.query(models.Class).filter(models.Class.school_id == current_user.school_id).all()
    result = []
    for c in classes:
        count = db.query(models.Enrollment).filter(models.Enrollment.class_id == c.id).count()
        result.append(schemas.ClassResponse(
            id=c.id, name=c.name, school_id=c.school_id,
            teacher_id=c.teacher_id, created_at=c.created_at, student_count=count
        ))
    return result

@app.delete("/classes/{class_id}", status_code=204)
def delete_class(class_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    cls = db.query(models.Class).filter(models.Class.id == class_id, models.Class.school_id == current_user.school_id).first()
    if not cls: raise HTTPException(status_code=404, detail="Class not found")
    db.delete(cls); db.commit()

# ── enrollment ────────────────────────────────────────────────────────────────

@app.get("/classes/{class_id}/students", response_model=list[schemas.UserResponse])
def get_class_students(class_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    enrollments = db.query(models.Enrollment).filter(models.Enrollment.class_id == class_id).all()
    student_ids = [e.student_id for e in enrollments]
    return db.query(models.User).filter(models.User.id.in_(student_ids)).all()

@app.patch("/classes/{class_id}/teacher", response_model=schemas.ClassResponse)
def update_class_teacher(class_id: int, teacher_id: Optional[int] = None, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal")
    cls = db.query(models.Class).filter(models.Class.id == class_id, models.Class.school_id == current_user.school_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    cls.teacher_id = teacher_id
    db.commit(); db.refresh(cls)
    count = db.query(models.Enrollment).filter(models.Enrollment.class_id == cls.id).count()
    return schemas.ClassResponse(id=cls.id, name=cls.name, school_id=cls.school_id, teacher_id=cls.teacher_id, created_at=cls.created_at, student_count=count)

@app.post("/classes/{class_id}/enroll/{student_id}", response_model=schemas.EnrollmentResponse)
def enroll_student(class_id: int, student_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    existing = db.query(models.Enrollment).filter(models.Enrollment.class_id == class_id, models.Enrollment.student_id == student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student already enrolled")
    enrollment = models.Enrollment(student_id=student_id, class_id=class_id)
    db.add(enrollment); db.commit(); db.refresh(enrollment)
    return enrollment

@app.delete("/classes/{class_id}/enroll/{student_id}", status_code=204)
def unenroll_student(class_id: int, student_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.class_id == class_id, models.Enrollment.student_id == student_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(enrollment); db.commit()

# ── subjects ──────────────────────────────────────────────────────────────────

@app.get("/classes/{class_id}/subjects", response_model=list[schemas.SubjectResponse])
def get_subjects(class_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Subject).filter(models.Subject.class_id == class_id).all()

@app.post("/classes/{class_id}/subjects", response_model=schemas.SubjectResponse)
def create_subject(class_id: int, data: schemas.SubjectCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    subject = models.Subject(name=data.name, description=data.description, class_id=class_id, created_by_id=current_user.id)
    db.add(subject); db.commit(); db.refresh(subject)
    return subject

@app.delete("/subjects/{subject_id}", status_code=204)
def delete_subject(subject_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(subject); db.commit()

# ── materials ─────────────────────────────────────────────────────────────────

@app.get("/subjects/{subject_id}/materials", response_model=list[schemas.MaterialResponse])
def get_materials(subject_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Material).filter(models.Material.subject_id == subject_id).all()

@app.post("/subjects/{subject_id}/materials/url", response_model=schemas.MaterialResponse)
def add_material_url(subject_id: int, data: schemas.MaterialCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    material = models.Material(title=data.title, description=data.description, material_type=data.material_type, url=data.url, subject_id=subject_id, uploaded_by_id=current_user.id)
    db.add(material); db.commit(); db.refresh(material)
    return material

@app.post("/subjects/{subject_id}/materials/upload", response_model=schemas.MaterialResponse)
async def upload_material_file(
    subject_id: int,
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_role(current_user, "principal", "teacher")
    ext = Path(file.filename).suffix.lower()
    material_type = "video" if ext in (".mp4", ".mov", ".avi", ".webm", ".mkv", ".wmv", ".m4v", ".3gp", ".ts") else "pdf" if ext == ".pdf" else "file"
    save_name = f"{uuid.uuid4()}{ext}"
    save_path = UPLOAD_DIR / save_name
    with save_path.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)
    url = f"/uploads/{save_name}"
    material = models.Material(title=title, description=description, material_type=material_type, url=url, filename=file.filename, subject_id=subject_id, uploaded_by_id=current_user.id)
    db.add(material); db.commit(); db.refresh(material)
    return material

@app.delete("/materials/{material_id}", status_code=204)
def delete_material(material_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    material = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Not found")
    if material.filename and material.url:
        p = UPLOAD_DIR / Path(material.url).name
        if p.exists():
            p.unlink()
    db.delete(material); db.commit()

@app.patch("/materials/{material_id}", response_model=schemas.MaterialResponse)
def update_material(material_id: int, data: schemas.MaterialUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "principal", "teacher")
    material = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not material: raise HTTPException(status_code=404, detail="Not found")
    if data.title is not None: material.title = data.title
    if data.description is not None: material.description = data.description
    db.commit(); db.refresh(material)
    return material

# ── teacher routes ────────────────────────────────────────────────────────────

@app.get("/teachers/my/classes", response_model=list[schemas.ClassResponse])
def teacher_get_classes(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "teacher")
    classes = db.query(models.Class).filter(models.Class.teacher_id == current_user.id).all()
    result = []
    for c in classes:
        count = db.query(models.Enrollment).filter(models.Enrollment.class_id == c.id).count()
        result.append(schemas.ClassResponse(
            id=c.id, name=c.name, school_id=c.school_id,
            teacher_id=c.teacher_id, created_at=c.created_at, student_count=count
        ))
    return result

# ── student routes ────────────────────────────────────────────────────────────

@app.get("/students/my/classes", response_model=list[schemas.ClassResponse])
def student_get_classes(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "student")
    enrollments = db.query(models.Enrollment).filter(models.Enrollment.student_id == current_user.id).all()
    class_ids = [e.class_id for e in enrollments]
    classes = db.query(models.Class).filter(models.Class.id.in_(class_ids)).all()
    result = []
    for c in classes:
        count = db.query(models.Enrollment).filter(models.Enrollment.class_id == c.id).count()
        result.append(schemas.ClassResponse(
            id=c.id, name=c.name, school_id=c.school_id,
            teacher_id=c.teacher_id, created_at=c.created_at, student_count=count
        ))
    return result

# ── parent routes ─────────────────────────────────────────────────────────────

@app.get("/parents/my/children", response_model=list[schemas.UserResponse])
def get_children(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "parent")
    links = db.query(models.ParentStudent).filter(models.ParentStudent.parent_id == current_user.id).all()
    student_ids = [l.student_id for l in links]
    return db.query(models.User).filter(models.User.id.in_(student_ids)).all()

@app.post("/parents/link-student", response_model=schemas.UserResponse)
def link_student(student_email: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "parent")
    student = db.query(models.User).filter(models.User.email == student_email, models.User.role == "student").first()
    if not student: raise HTTPException(status_code=404, detail="No student found with that email")
    existing = db.query(models.ParentStudent).filter(models.ParentStudent.parent_id == current_user.id, models.ParentStudent.student_id == student.id).first()
    if existing: raise HTTPException(status_code=400, detail="Already linked to this student")
    db.add(models.ParentStudent(parent_id=current_user.id, student_id=student.id)); db.commit()
    return student

@app.delete("/parents/unlink-student/{student_id}", status_code=204)
def unlink_student(student_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "parent")
    link = db.query(models.ParentStudent).filter(models.ParentStudent.parent_id == current_user.id, models.ParentStudent.student_id == student_id).first()
    if not link: raise HTTPException(status_code=404, detail="Not linked")
    db.delete(link); db.commit()

@app.get("/parents/student/{student_id}/classes", response_model=list[schemas.ClassResponse])
def parent_view_student_classes(student_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_role(current_user, "parent")
    link = db.query(models.ParentStudent).filter(models.ParentStudent.parent_id == current_user.id, models.ParentStudent.student_id == student_id).first()
    if not link: raise HTTPException(status_code=403, detail="Not linked to this student")
    enrollments = db.query(models.Enrollment).filter(models.Enrollment.student_id == student_id).all()
    class_ids = [e.class_id for e in enrollments]
    classes = db.query(models.Class).filter(models.Class.id.in_(class_ids)).all()
    result = []
    for c in classes:
        count = db.query(models.Enrollment).filter(models.Enrollment.class_id == c.id).count()
        result.append(schemas.ClassResponse(id=c.id, name=c.name, school_id=c.school_id, teacher_id=c.teacher_id, created_at=c.created_at, student_count=count))
    return result

# ── misc ──────────────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"message": "EduXcel API is running"}
