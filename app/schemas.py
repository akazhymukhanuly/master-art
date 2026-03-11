from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class Language(StrEnum):
    RU = "ru"
    KZ = "kz"


class DeliveryType(StrEnum):
    PICKUP = "pickup"
    DELIVERY = "delivery"


class LeadCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=128)
    customer_phone: str = Field(min_length=5, max_length=64)
    language: Language = Language.RU
    service_type: str = Field(min_length=2, max_length=64)
    material: str = Field(default="banner_frontlit", min_length=2, max_length=32)
    width_cm: int = Field(gt=0, le=10000)
    height_cm: int = Field(gt=0, le=10000)
    quantity: int = Field(gt=0, le=10000)
    urgency_days: int = Field(gt=0, le=30)
    has_design: bool = False
    delivery_type: DeliveryType = DeliveryType.PICKUP
    delivery_address: str = Field(default="", max_length=512)
    notes: str = Field(default="", max_length=4000)

    @field_validator("customer_phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        normalized = value.strip().replace(" ", "")
        valid_chars = set("+0123456789()-")
        if not all(ch in valid_chars for ch in normalized):
            raise ValueError("Phone contains invalid characters")
        if sum(ch.isdigit() for ch in normalized) < 10:
            raise ValueError("Phone must include at least 10 digits")
        return normalized


class LeadRead(BaseModel):
    id: int
    source: str
    customer_name: str
    customer_phone: str
    language: Language
    service_type: str
    material: str
    width_cm: int
    height_cm: int
    quantity: int
    urgency_days: int
    has_design: bool
    delivery_type: DeliveryType
    delivery_address: str
    notes: str
    estimated_price_kzt: int
    estimate_detail: str
    ai_summary: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadListResponse(BaseModel):
    items: list[LeadRead]
    total: int
    limit: int
    offset: int


class PriceEstimateRequest(BaseModel):
    service_type: str
    material: str = "banner_frontlit"
    width_cm: int = Field(gt=0, le=10000)
    height_cm: int = Field(gt=0, le=10000)
    quantity: int = Field(gt=0, le=10000, default=1)
    urgency_days: int = Field(gt=0, le=30, default=3)
    has_design: bool = False
    delivery_type: DeliveryType = DeliveryType.PICKUP


class PriceEstimateResponse(BaseModel):
    estimated_price_kzt: int
    area_m2: float
    detail: str
    breakdown: dict[str, int]


class LeadStatsResponse(BaseModel):
    total_leads: int
    avg_check_kzt: int
    by_service: dict[str, int]


class ProposalOption(BaseModel):
    name: str
    material: str
    eta_days: int
    total_kzt: int
    benefits: list[str]


class ProposalResponse(BaseModel):
    lead_preview: str
    options: list[ProposalOption]
    recommended: str


class CreativeCopyRequest(BaseModel):
    service_type: str
    audience: str = Field(default="local business owners", min_length=2, max_length=128)
    language: Language = Language.RU


class CreativeCopyResponse(BaseModel):
    headlines: list[str]
    call_to_action: str


class IntakeParseRequest(BaseModel):
    message: str = Field(min_length=4, max_length=4000)
    language: Language = Language.RU


class ParsedBrief(BaseModel):
    summary: str
    service_type: str
    material: str
    width_cm: int
    height_cm: int
    quantity: int
    urgency_days: int
    has_design: bool
    delivery_type: DeliveryType
    delivery_address: str
    audience: str
    style_hint: str


class ConceptCard(BaseModel):
    id: str
    title: str
    angle: str
    tagline: str
    material: str
    eta_days: int
    estimated_price_kzt: int
    score: int
    why: list[str]


class ConceptsRequest(BaseModel):
    brief: ParsedBrief


class ConceptsResponse(BaseModel):
    brief: ParsedBrief
    cards: list[ConceptCard]
    recommended_id: str


class TradeoffRequest(BaseModel):
    brief: ParsedBrief
    mode: str = Field(pattern="^(cheaper|faster|premium)$")


class ConfirmDealRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=128)
    customer_phone: str = Field(min_length=5, max_length=64)
    brief: ParsedBrief
    selected_concept_id: str


class ConfirmDealResponse(BaseModel):
    lead_id: int
    message: str
