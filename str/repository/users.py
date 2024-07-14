from libgravatar import Gravatar
from sqlalchemy.orm import Session

from str.database.models import User
from str.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieves a user matching the given email for a specific session.
    
    :param email: Email for find a user.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: Returns the user matching the given email.
    :rtype: User
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creating a new user.
    
    :param body: The data for create a user.
    :type body: UserModel
    :param db: The database session.
    :type db: Session
    :return: Returns a newly created user.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def confirmed_email(email: str, db: Session) -> User:
    """
    Confirm the email address of a user.

    :param email: the email address to confirm.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: This function  returns user object.
    :rtype: User
    """
    user: User = await get_user_by_email(email, db)
    if user is not None:
        user.confirmed = True
        db.commit()
    return user

async def update_token(user: User, token: str | None, db: Session) -> User:
    """
    Update a token for a user.

    :param user: the user token updating for.
    :type user: User
    :param token: the token for update, or None, if does not exist.
    :type token: str|None
    :param db: The database session.
    :type db: Session
    :return: This function  returns user object.
    :rtype: User
    """
    user.refresh_token = token
    db.commit()
    return user

async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    Update the avatar of a user.

    :param email: the email address of the user.
    :type email: str.
    :param url: the  url-address for a new avatar.
    :type url: str.
    :param db: The database session.
    :type db: Session.
    :return: The user with updated avatar.
    :rtype: User.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user