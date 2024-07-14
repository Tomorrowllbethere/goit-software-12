from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from str.database.db import get_db
from str.database.models import User
import str.repository.users as repository_users
from str.services.auth import auth_service
from str.conf.config import settings
from str.schemas import UserDb

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve the currently authenticated user's information.

    :param current_user: The current authenticated user.
    :type current_user: User
    :return: The current user's information.
    :rtype: UserDb
    """
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    Update the avatar of the currently authenticated user.

    :param file: The uploaded file containing the new avatar image.
    :type file: UploadFile
    :param current_user: The current authenticated user.
    :type current_user: User
    :param db: The database session dependency.
    :type db: Session, optional
    :return: The updated user with the new avatar URL.
    :rtype: UserDb
    """
    cloudinary.config(
        cloud_name=settings['cloudinary_name'],
        api_key=settings['cloudinary_api_key'],
        api_secret=settings['cloudinary_api_secret'],
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
