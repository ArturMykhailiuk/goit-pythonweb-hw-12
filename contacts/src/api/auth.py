from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import UserCreate, Token, User, RequestEmail, ResetPassword
from src.services.auth import create_access_token, Hash, get_email_from_token
from src.services.users import UserService
from src.database.db import get_db
from src.services.email import send_email, send_email_for_reset_password
from src.repository.users import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.auth import Hash, get_current_moderator_user, get_current_admin_user
from src.services.auth import create_access_token
from src.services.auth import get_email_from_token


router = APIRouter(prefix="/auth", tags=["auth"])

# Реєстрація користувача
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    Register a new user.


    This endpoint checks for the uniqueness of the user's email and username,
    hashes the password, creates the user in the database, and sends a 
    verification email.

    Parameters:
    - user_data: UserCreate object containing user details.
    - background_tasks: FastAPI's BackgroundTasks for executing tasks in the background.
    - request: FastAPI Request object to access request data.
    - db: Database session dependency.

    Returns:
    - The newly created user object.

    Raises:
    - HTTPException: If the email or username is already in use.
    """
    user_service = UserService(db)

    # Check if the user with the same email already exists
    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email address is already in use",
        )

    # Check if the user with the same username already exists
    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already in use",
        )

    # Hash the password
    user_data.password = Hash().get_password_hash(user_data.password)

    # Create a new user
    new_user = await user_service.create_user(user_data)

    # Send a verification email in the background
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )

    return new_user

# Логін користувача
@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    """
    Log in a user.

    This endpoint checks if the user exists, the password is correct, and the
    user has confirmed their email address. If all checks pass, it creates an
    access token and returns it.

    Parameters:
    - form_data: OAuth2PasswordRequestForm object containing username and password.
    - db: Database session dependency.

    Returns:
    - A Token object containing the access token.

    Raises:
    - HTTPException: If the username or password is incorrect, or the email address
      is not confirmed.
    """

    # Get the user by username
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)

    # Check if the user exists and the password is correct
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if the user has confirmed their email address
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email address is not confirmed",
        )

    # Create an access token
    access_token = await create_access_token(data={"sub": user.username})

    # Return the access token
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/confirmed_email/{token}")
async def confirmed_email(
    token: str, db: Session = Depends(get_db)
) -> dict[str, str]:
    """
    Verify the user's email address.

    This endpoint is called by the verification email link. It checks if the
    token is valid and gets the email address from the token. If the user with
    the same email exists and has not confirmed their email address before, it
    updates the user's confirmed status to True.

    Parameters:
    - token: The verification token sent in the verification email.
    - db: Database session dependency.

    Returns:
    - A dictionary containing the message of the result.

    Raises:
    - HTTPException: If the token is invalid, the user does not exist, or the
      user has already confirmed their email address.
    """

    # Get the email address from the token
    email = await get_email_from_token(token)

    # Get the user by the email address
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    # Check if the user exists and has not confirmed their email address before
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}

    # Update the user's confirmed status to True
    await user_service.confirmed_email(email)

    # Return a success message
    return {"message": "Електронну пошту підтверджено"}

@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """
    Request an email verification.

    This endpoint is called when the user requests an email verification. If the
    user with the same email exists and has not confirmed their email address
    before, it sends a verification email in the background.

    Parameters:
    - body: The JSON payload containing the email address.
    - background_tasks: Background task dependency.
    - request: The request object dependency.
    - db: Database session dependency.

    Returns:
    - A dictionary containing the message of the result.

    Raises:
    - HTTPException: If the user with the same email already exists and has
      confirmed their email address before.
    """

    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    # Check if the user with the same email already exists and has confirmed their email address before
    if user and user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    if user:
        # Send a verification email in the background
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}

@router.post("/request-password-reset", response_model=dict)
async def request_password_reset(request_email: RequestEmail, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(request_email.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    token = create_access_token({"sub": user.email})
    background_tasks.add_task(send_email_for_reset_password, user.email, user.username, "http://localhost:8000", token=token)
    return {"message": "Password reset email sent"}

@router.get("/reset-password/{token}", response_model=dict)
async def verify_reset_token(token: str):
    email = await get_email_from_token(token)
    return {"message": "Token is valid", "email": email}

@router.post("/reset-password/{token}", response_model=dict)
async def reset_password(reset_password: ResetPassword, db: AsyncSession = Depends(get_db)):
    email = get_email_from_token(reset_password.token)
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.password = Hash.get_password_hash(reset_password.new_password)
    await db.commit()
    return {"message": "Password has been reset successfully"}


# Перший маршрут - доступний для всіх
@router.get("/public")
def read_public():
    return {"message": "Це публічний маршрут, доступний для всіх"}

# Другий маршрут - для модераторів та адміністраторів
@router.get("/moderator")
def read_moderator(
    current_user: User = Depends(get_current_moderator_user),
):
    return {
        "message": f"Вітаємо, {current_user.username}! Це маршрут для модераторів та адміністраторів"
    }

# Третій маршрут - тільки для адміністраторів
@router.get("/admin")
def read_admin(current_user: User = Depends(get_current_admin_user)):
    return {"message": f"Вітаємо, {current_user.username}! Це адміністративний маршрут"}



