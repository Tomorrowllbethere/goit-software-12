from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi_limiter.depends import RateLimiter
from str.services.email import send_email
from str.database.db import get_db
from str.schemas import UserModel, UserResponse, TokenModel, RequestEmail
import str.repository.users as repository_users
from str.services.auth import auth_service

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()

# 
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED, description='No more than 10 requests per minute')
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Create a new user account.

    :param body: The user model containing user registration data.
    :type body: UserModel
    :param background_tasks: The background tasks dependency for sending confirmation email.
    :type background_tasks: BackgroundTasks
    :param request: The request object to get the base URL.
    :type request: Request
    :param db: The database session dependency.
    :type db: Session, optional
    :return: The created user and a success message.
    :rtype: dict
    :raises HTTPException: If an account with the given email already exists.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}

@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user and return JWT tokens.

    :param body: The OAuth2 password request form containing login credentials.
    :type body: OAuth2PasswordRequestForm
    :param db: The database session dependency.
    :type db: Session, optional
    :return: The access and refresh tokens.
    :rtype: dict
    :raises HTTPException: If the email is invalid, email is not confirmed, or the password is invalid.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm a user's email address.

    :param token: The token sent to the user's email for confirmation.
    :type token: str
    :param db: The database session dependency.
    :type db: Session, optional
    :return: A confirmation message.
    :rtype: dict
    :raises HTTPException: If the verification fails or the email is already confirmed.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Refresh JWT tokens.

    :param credentials: The HTTP authorization credentials containing the refresh token.
    :type credentials: HTTPAuthorizationCredentials
    :param db: The database session dependency.
    :type db: Session, optional
    :return: The new access and refresh tokens.
    :rtype: dict
    :raises HTTPException: If the refresh token is invalid or does not match the stored token.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    Request email confirmation.

    :param body: The request email model containing the user's email.
    :type body: RequestEmail
    :param background_tasks: The background tasks dependency for sending the confirmation email.
    :type background_tasks: BackgroundTasks
    :param request: The request object to get the base URL.
    :type request: Request
    :param db: The database session dependency.
    :type db: Session, optional
    :return: A message indicating that the confirmation email has been sent.
    :rtype: dict
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}