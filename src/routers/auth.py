from fastapi import APIRouter
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from database import SessionLocal
from typing import Annotated,Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Path
from starlette import status
from fastapi.security import OAuth2PasswordRequestFormStrict,OAuth2PasswordBearer
from datetime import timedelta,timezone,datetime
from jose import jwt,JWTError

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_context = CryptContext(schemes=['bcrypt'])
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

# openssl rand -hex 32
SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'

class CreateUserRequest(BaseModel):
    user_name:str
    email:str
    first_name:str
    last_name:str
    password:str
    role:str

class Token(BaseModel):
    access_token:str
    token_type:str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def authenticated_users(username:str,password:str,db:db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    # might get conversion waring : Column[str]
    if not bcrypt_context.verify(password,str(user.hashed_password)):
        return False
    return user

def create_access_token(username:str,user_id:int,role:str,expires_delta:timedelta):
    # Create payload with username,user_id and role
    encode = {'sub':username,'user_id':user_id,'role':role}
    # Set JWT expiry time
    expires = datetime.now(timezone.utc)+expires_delta
    encode.update({'exp': expires})
    # Encode and return JWT token
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependency to get current authenticated user from JWT token
async def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    try:
        # Decode JWT token
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        # Extract username and user_id from payload
        username:Optional[str] = payload.get('sub')
        user_id:Optional[int] = payload.get('user_id')
        user_role:Optional[str] = payload.get('role')
        # Validate that both username and user_id exist
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {"username":username,"user_id":user_id,"user_role":user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')

@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency,
                      create_user_request:CreateUserRequest):
    # Create user model instance with hashed password
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.user_name,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        is_active=True
    )
    db.add(create_user_model)
    db.commit()


@router.get("/",status_code=status.HTTP_200_OK)
async def get_all_users(db:db_dependency):
    users = db.query(Users).all()
    if users is None:
        raise HTTPException(status_code=404, detail="No user found")
    return users

# Login endpoint that returns JWT access token
@router.post("/token")
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestFormStrict,Depends()],
                                 db:db_dependency):
    # Authenticate user with username and password
    user = authenticated_users(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    # Create access token with 20 minute expiration
    # user.id is passed here and encoded as 'user_id' in the JWT
    user_name = str(user.username)
    user_id   = int(user.id)
    user_role = str(user.role)
    token = create_access_token(user_name,user_id,user_role,timedelta(minutes=20))
    # Return token in OAuth2 format
    return {'access_token': token, 'token_type': 'bearer'}