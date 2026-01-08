from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import User
from core.security import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 1. REGISTER
@router.post("/register")
async def register_user(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email")
    password = payload.get("password")
    name = payload.get("name")
    
    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    new_user = User(
        email=email,
        name=name,
        password_hash=get_password_hash(password) 
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

# 2. LOGIN (Returns Token)
@router.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Verify user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # Generate Token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(minutes=60)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 3. GET CURRENT USER (Dependency for protected routes)
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "name": current_user.name}