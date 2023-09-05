from fastapi import APIRouter, HTTPException, Depends, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Annotated
from  models.user import User, Token, TokenData  # Import User model from models
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import load_dotenv
import csv
from uuid import UUID, uuid4
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")  # Make sure you have a "templates" folder in your project directory

router = APIRouter()

SECRET_KEY = "Th1s_1s_A_Str0ng_S3cr3t_K3y_!2$4%^6&8*0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
USERS_CSV = "db/users.csv"

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Token Dependencies
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# retreive authenticated user
def get_user(username: str):
    print(username, "line 37")
    with open(USERS_CSV, "r", encoding="utf-8") as users_file:
        users = csv.DictReader(users_file)
        print(users, "line 39")
        for info in users:
            print(info["username"], "line 41")
            print(username == info["username"], 'line 43')

            if username == info["username"]:
                user_dict = info
                print(username, "line 43")
                print(User(**user_dict), "line 44")
                return User(**user_dict)
# User Authentication
def authenticate_user(username: str, password: str):
    print(password, "line 52")
    print(username, "line 47")
    print(get_user(username), "line 48")
    user = get_user(username)
    print(user, "line 50")
    hashed_password = pwd_context.hash(password)
    if not user:
        print("line 52")
        return False
    if not verify_password(password, hashed_password):
        print("line 55")
        return False
    else:
        print(user, "hash successful")
        return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Register User
# Load users from csv file and check if user with username already exist
@router.post("/register")
async def register_user(request: Request, username: str = Form(...), password: str = Form(...)):
    with open(USERS_CSV, "r", encoding="utf-8") as users_file:
        users = csv.DictReader(users_file)
        for existing_user in users:
            if existing_user['username'] == username:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    hashed_password = get_password_hash(password)


    # Generate a unique ID for the user
    user_id = str(uuid4())

    # write succesfully registered user to user csv
    with open(USERS_CSV, "a", newline="") as users_file:
        fieldnames = ["id", "username", "password"]
        csv_writer = csv.DictWriter(users_file, fieldnames=fieldnames)
        if users_file.tell() == 0:
            csv_writer.writeheader()
        csv_writer.writerow({"id": f'{user_id}', "username": f'{username}', "password": f'{hashed_password}'})

    # Render the registration success template
    return templates.TemplateResponse("users/registration_success.html", {"request": request})


# Retrieve User Token authentication
@router.post("/token", response_model=Token)
async def login_for_access_token(request: Request,form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password",headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("users/register.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("users/login.html", {"request": request})

@router.get("/users/profile", response_model=User)
async def user_profile(request: Request, current_user: Annotated[User, Depends(get_current_user)]):
    if request:
        print(request.headers, "line 155")
    else:
        print(f'no request made {request.headers} line 157')
    return templates.TemplateResponse("users/profile.html", {"request": request, "user": current_user})
