from datetime import datetime
from typing import Optional

from bson import ObjectId
from fastapi import Form
from pydantic import BaseModel, EmailStr, Field, model_validator


class User(BaseModel):
    id: str = Field(..., alias='_id')
    profile_id: str
    name: str
    email: EmailStr
    user_type: str
    confirmed_code: bool
    created_at: datetime
    updated_at: datetime
    password: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def convert_objectid(cls, values):
        if isinstance(values, dict) and '_id' in values:
            if isinstance(values['_id'], ObjectId):
                values['_id'] = str(values['_id'])
        return values


class Profile(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    name: str
    nickname: str
    country: str
    state: str
    city: str
    district: str
    deficiency: str
    avatar_url: Optional[str] = None
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    @model_validator(mode='before')
    @classmethod
    def convert_objectid(cls, values):
        if isinstance(values, dict) and '_id' in values:
            if isinstance(values['_id'], ObjectId):
                values['_id'] = str(values['_id'])
        return values


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class LoginForm(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    success: bool
    user: dict
    token: str
    access_token: str
    token_type: str


class GoogleLoginRequest(BaseModel):
    token: str


class UserCreate(BaseModel):
    name: str = Form('João Neto')
    country: str = Form('Brasil')
    state: str = Form('SP')
    city: str = Form('São Paulo')
    district: str = Form('Centro')
    deficiency: str = Form('Nenhuma')
    avatar_url: Optional[str] = None
    email: EmailStr = Form('joao@example.com')
    password: str = Form('senha')


class UserResponse(BaseModel):
    id: str = Field(..., alias='_id')
    name: str
    email: EmailStr
    user_type: str
    confirmed_code: bool
    confirmation_code: str
    created_at: datetime
    updated_at: datetime
    profile_id: str

    @model_validator(mode='before')
    @classmethod
    def convert_objectid(cls, values):
        if isinstance(values, dict) and '_id' in values:
            if isinstance(values['_id'], ObjectId):
                values['_id'] = str(values['_id'])
        return values


class RegisterResponse(BaseModel):
    success: bool
    user: dict
    message: str
    token: str


class ValidToken(BaseModel):
    success: bool
    message: str


class ChangePasswordRequest(BaseModel):
    email: EmailStr
    password: str
    new_password: str


class DefautMessage(BaseModel):
    success: bool
    message: str


class RequestChangeEmail(BaseModel):
    email: EmailStr
    password: str
    new_email: EmailStr
    confirmation_code: Optional[str] = None


class SearchByEmailRequest(BaseModel):
    email: EmailStr


class UserSimplified(BaseModel):
    id: str = Field(..., alias='_id')
    name: str
    email: EmailStr
    confirmed_code: bool

    @model_validator(mode='before')
    @classmethod
    def convert_objectid(cls, values):
        if isinstance(values, dict) and '_id' in values:
            if isinstance(values['_id'], ObjectId):
                values['_id'] = str(values['_id'])
        return values


class verifyEmailRequest(BaseModel):
    email: EmailStr
    name: str
    google: bool


class verifyEmailResponse(BaseModel):
    success: bool
    message: str
    user: UserSimplified


class confirmCodeRequest(BaseModel):
    id: str
    confirmation_code: str


class confirmCodeResponse(BaseModel):
    success: bool
    message: str
