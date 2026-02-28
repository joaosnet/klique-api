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
    free_credits: int = 1
    paid_credits: int = 0
    total_generated: int = 0
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

    action: str = 'generate_card'


class UseCreditsResponse(BaseModel):
    """Resposta após usar crédito."""

    success: bool
    message: str
    remaining_credits: int


class PaymentTransaction(BaseModel):
    """Schema para transações de pagamento PIX."""

    id: Optional[str] = Field(None, alias='_id')
    user_id: str
    mp_payment_id: Optional[str] = None
    amount: float
    credits_amount: int
    status: str = 'pending'
    pix_qr_code: Optional[str] = None
    pix_qr_code_base64: Optional[str] = None
    pix_copy_paste: Optional[str] = None
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
    credits_count: Optional[int] = Field(
        None, ge=1, description='Quantidade de créditos a comprar.'
    )


class CreatePixPaymentResponse(BaseModel):
    """Resposta com dados do PIX gerado."""

    success: bool
    payment_id: str
    amount: float
    credits_amount: int
    qr_code: str
    qr_code_base64: str
    copy_paste: str
    expiration_date: datetime


class PaymentStatusResponse(BaseModel):
    """Status de um pagamento."""

    payment_id: str
    status: str
    amount: float
    credits_amount: int
    paid_at: Optional[datetime] = None


class PaymentConfigResponse(BaseModel):
    """Configurações de pagamento."""

    min_payment_amount: float
    min_price_per_credit: float
    min_quantity: int


class CreditHistoryItem(BaseModel):
    """Item do histórico de créditos."""

    type: str
    amount: int
    description: str
    created_at: datetime


class CreditHistoryResponse(BaseModel):
    """Resposta com histórico de créditos."""

    items: list[CreditHistoryItem]
    total_items: int


# ========================================
# OmniFlash — Game Theory Engine Schemas
# ========================================


class UserPreferences(BaseModel):
    card_size_scale: float = 1.0


# --- Domains ---

class DomainCreate(BaseModel):
    name: str
    theme: str


class DomainUpdate(BaseModel):
    name: Optional[str] = None
    theme: Optional[str] = None


class Domain(MongoBaseModel):
    id: Optional[str] = Field(None, alias='_id')
    user_id: str
    name: str
    theme: str
    created_at: datetime


class DomainStats(BaseModel):
    domain_id: str
    domain_name: str
    cards_count: int
    due_today: int
    accuracy: float


class DomainWithStats(BaseModel):
    domain: Domain
    stats: DomainStats


# --- Scenario Cards ---

class ScenarioCardData(BaseModel):
    """Raw card data returned by Gemini (not yet persisted)."""
    template_type: str
    scenario_context: str
    question: str
    predicted_outcome: str
    game_theory_explanation: str
    probability_heat_score: int
    visual_prompt_idea: Optional[str] = None


class ScenarioCard(MongoBaseModel):
    id: Optional[str] = Field(None, alias='_id')
    domain_id: str
    user_id: str
    template_type: str
    scenario_context: str
    question: str
    predicted_outcome: str
    game_theory_explanation: str
    media_urls: list[str] = []
    probability_heat_score: int
    visual_prompt_idea: Optional[str] = None
    created_at: datetime


class GenerateCardRequest(BaseModel):
    domain_id: str
    context: Optional[str] = None


class SwipeAction(BaseModel):
    card_data: ScenarioCardData
    domain_id: str
    action: str  # "save" | "discard"


class SwipeResponse(BaseModel):
    success: bool
    message: str
    card_id: Optional[str] = None


# --- SRS (Spaced Repetition System) ---

class Review(MongoBaseModel):
    id: Optional[str] = Field(None, alias='_id')
    card_id: str
    user_id: str
    next_review_date: datetime
    interval: int = 1
    ease_factor: float = 2.5
    repetitions: int = 0


class SimulationLog(MongoBaseModel):
    id: Optional[str] = Field(None, alias='_id')
    user_id: str
    card_id: str
    domain_id: str
    performance_rating: int  # 0-5
    reviewed_at: datetime


class ReviewSubmitRequest(BaseModel):
    card_id: str
    performance_rating: int = Field(..., ge=0, le=5)


class ReviewSubmitResponse(BaseModel):
    success: bool
    next_review_date: datetime
    interval_days: int
    new_ease_factor: float


class DueCard(BaseModel):
    card: ScenarioCard
    review: Review


class SRSStats(BaseModel):
    total_trained: int
    streak_days: int
    cards_mastered: int
    due_today: int


# --- Oracle Analytics ---

class DashboardOverview(BaseModel):
    total_domains: int
    total_cards: int
    due_today: int
    weekly_trained: int
    streak_days: int


class RadarEntry(BaseModel):
    domain_name: str
    domain_id: str
    accuracy: float
    trained_count: int


class ActivityEntry(BaseModel):
    date: str
    count: int
    avg_rating: float
