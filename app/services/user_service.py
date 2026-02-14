from datetime import timedelta
from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.schemas.token import Token

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.audit_log import EntityType
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin
from app.core.audit import log_action
from app.core.config import settings



class UserService:
    def __init__(self, session: Session):
        self.session = session 

    def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.get(User, user_id)
    
    def create_user(self, user_data: UserCreate, created_by: User) -> User:
        if self.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        new_user = User(
            email=user_data.email,
            password_hash= get_password_hash(user_data.password),
            role = user_data.role
        )

        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)

        log_action(
            session=self.session,
            user_id=created_by.id,
            action="register_user",
            entity_type=EntityType.user,
            entity_id=new_user.id,
            meta={"created_email": new_user.email, "role": new_user.role.value}
        )

        return new_user
    
    def authenticate(self, credentials: UserLogin) -> Token:
        user = self.get_by_email(credentials.email)

        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"user_id": user.id, "role": user.role.value},
            expires_delta=access_token_expires
        )

        log_action(
            session=self.session,
            user_id=user.id,
            action="login",
            entity_type=EntityType.user,
            entity_id=user.id
        )

        return Token(access_token=access_token, token_type="bearer")
    
    def list_users(
            self, 
            skip: int = 0,
            limit: int = 20,
            role: Optional[UserRole] = None 
    ) -> list[User]:
        

        statement = select(User)
        if role:
            statement = statement.where(User.role == role)

        statement = statement.offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    

    def deactivate_user(self, user_id: int, deactivated_by: User) -> User:
        user = self.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.id == deactivated_by.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate yourself"
            )

        
        user.is_active = False
        self.session.add(user)
        """
        self.session.add(user) здесь не “добавляет нового пользователя”, 
        а помечает измененный объект для сохранения. После user.is_active = False объект уже есть 
        в БД, но ORM должен зафиксировать, что его нужно обновить. add() гарантирует, что при commit() 
        изменение уйдет в базу.
        """
        self.session.commit()
        self.session.refresh(user) 
        """
        заново читает объект из базы после commit. Это нужно, чтобы в 
        объекте были актуальные значения из БД (например, триггеры, default-поля, updated_at, версии, 
        события). Даже при простом is_active = False это безопасная привычка — вы гарантируете, 
        что возвращаете пользователю свежие данные, а не потенциально устаревшие из памяти ORM.
        """
        

        log_action(
            session=self.session,
            user_id=deactivated_by.id,
            action="deactivate_user",
            entity_type=EntityType.user,
            entity_id=user.id
        )

        return user
    


    
    



