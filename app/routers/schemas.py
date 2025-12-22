from datetime import datetime
from typing import Optional

from bson import ObjectId
from fastapi import Form
from pydantic import BaseModel, EmailStr, Field, model_validator


class MongoBaseModel(BaseModel):
    """
    Base model para schemas que vêm do MongoDB.

    O MongoDB usa ObjectId como tipo padrão para _id, mas Pydantic não
    consegue serializar ObjectId para JSON. Este model_validator converte
    automaticamente ObjectId para string antes da validação.

    Ref: https://www.mongodb.com/docs/manual/reference/method/ObjectId/
    Ref: https://docs.pydantic.dev/latest/concepts/validators/#model-validators
    """

    @model_validator(mode='before')
    @classmethod
    def convert_objectid(cls, values):
        if isinstance(values, dict) and '_id' in values:
            if isinstance(values['_id'], ObjectId):
                values['_id'] = str(values['_id'])
        return values


class User(MongoBaseModel):
    """Modelo de usuário do MongoDB."""

    id: str = Field(..., alias='_id')
    profile_id: str
    name: str
    email: EmailStr
    user_type: str
    confirmed_code: bool
    created_at: datetime
    updated_at: datetime
    password: Optional[str] = None


class Profile(MongoBaseModel):
    """Modelo de perfil do MongoDB."""

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


class UserResponse(MongoBaseModel):
    """Resposta com dados do usuário."""

    id: str = Field(..., alias='_id')
    name: str
    email: EmailStr
    user_type: str
    confirmed_code: bool
    confirmation_code: str
    created_at: datetime
    updated_at: datetime
    profile_id: str


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


class UserSimplified(MongoBaseModel):
    """Modelo simplificado de usuário."""

    id: str = Field(..., alias='_id')
    name: str
    email: EmailStr
    confirmed_code: bool


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


class StatusView(BaseModel):
    user_number: str
    viewed_at: datetime


# ========================================
# Credits & Payments Schemas
# ========================================


class UserCredits(BaseModel):
    """Schema para saldo de créditos do usuário."""

    id: Optional[str] = Field(None, alias='_id')
    user_id: str
    free_credits: int = 1  # 1 imagem grátis
    paid_credits: int = 0  # Créditos comprados
    total_generated: int = 0  # Total de imagens geradas
    created_at: datetime
    updated_at: datetime

    @model_validator(mode='before')
    @classmethod
    def convert_objectid(cls, values):
        if isinstance(values, dict) and '_id' in values:
            if isinstance(values['_id'], ObjectId):
                values['_id'] = str(values['_id'])
        return values


class UserCreditsBalance(BaseModel):
    """Resposta com saldo de créditos."""

    free_credits: int
    paid_credits: int
    total_credits: int
    total_generated: int


class UseCreditsRequest(BaseModel):
    """Request para usar créditos."""

    action: str = 'generate_avatar'  # Tipo de ação que consome crédito


class UseCreditsResponse(BaseModel):
    """Resposta após usar crédito."""

    success: bool
    message: str
    remaining_credits: int


class PaymentTransaction(BaseModel):
    """Schema para transações de pagamento PIX."""

    id: Optional[str] = Field(None, alias='_id')
    user_id: str
    mp_payment_id: Optional[str] = None  # ID do Mercado Pago
    amount: float  # Valor em R$
    credits_amount: int  # Créditos a liberar
    status: str = 'pending'  # pending, approved, rejected, cancelled
    pix_qr_code: Optional[str] = None
    pix_qr_code_base64: Optional[str] = None
    pix_copy_paste: Optional[str] = None  # Código copia e cola
    expiration_date: Optional[datetime] = None
    created_at: datetime
    paid_at: Optional[datetime] = None

    @model_validator(mode='before')
    @classmethod
    def convert_objectid(cls, values):
        if isinstance(values, dict) and '_id' in values:
            if isinstance(values['_id'], ObjectId):
                values['_id'] = str(values['_id'])
        return values


class CreatePixPaymentRequest(BaseModel):
    """Request para criar pagamento PIX."""

    amount: float = Field(..., ge=1.0, description='Valor mínimo R$ 1,00')


class CreatePixPaymentResponse(BaseModel):
    """Resposta com dados do PIX gerado."""

    success: bool
    payment_id: str
    amount: float
    credits_amount: int
    qr_code: str  # URL da imagem do QR Code
    qr_code_base64: str  # QR Code em base64
    copy_paste: str  # Código copia e cola
    expiration_date: datetime


class PaymentStatusResponse(BaseModel):
    """Status de um pagamento."""

    payment_id: str
    status: str
    amount: float
    credits_amount: int
    paid_at: Optional[datetime] = None


class CreditHistoryItem(BaseModel):
    """Item do histórico de créditos."""

    type: str  # 'purchase', 'use', 'free'
    amount: int  # Quantidade de créditos
    description: str
    created_at: datetime


class CreditHistoryResponse(BaseModel):
    """Resposta com histórico de créditos."""

    items: list[CreditHistoryItem]
    total_items: int
