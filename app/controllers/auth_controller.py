from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..entities.user import UserCreate, Token, User, UserResponse
from ..services.auth_service import AuthService
from ..dependencies import get_db
from ..config.security import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_auth_service(db=Depends(get_db)) -> AuthService:
    return AuthService(db)

def get_current_user(token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service)) -> User:
    return auth_service.get_current_user(token)

@router.post("/register", response_model=dict)
def register(user: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    """Register a new user."""
    try:
        auth_service.register_user(user)
        return {"message": "User registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(get_auth_service)):
    """Login and get access token."""
    access_token = auth_service.login_user(form_data)
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active
    )