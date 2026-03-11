from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Lead
from app.schemas import (
    AssistantChatRequest,
    AssistantChatResponse,
    ConfirmDealRequest,
    ConfirmDealResponse,
    ConceptsRequest,
    ConceptsResponse,
    CreativeCopyRequest,
    CreativeCopyResponse,
    IntakeParseRequest,
    LeadCreate,
    LeadListResponse,
    LeadRead,
    LeadStatsResponse,
    ParsedBrief,
    PriceEstimateRequest,
    PriceEstimateResponse,
    ProposalResponse,
    TradeoffRequest,
)
from app.security import require_internal_api_key
from app.services.ai_assistant import assistant_reply, build_lead_summary
from app.services.concepts import build_concepts, tune_tradeoff
from app.services.creative import generate_creative_copy
from app.services.intake import parse_client_intake
from app.services.pricing import calculate_estimate_kzt
from app.services.proposal import build_tiered_proposal

router = APIRouter()


@router.get("/healthz")
async def healthz(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    await db.execute(select(1))
    return {"status": "ok"}


@router.post("/assistant/chat", response_model=AssistantChatResponse)
async def assistant_chat(payload: AssistantChatRequest) -> AssistantChatResponse:
    reply = await assistant_reply(payload)
    return AssistantChatResponse(reply=reply)


@router.post("/estimate", response_model=PriceEstimateResponse)
async def estimate(payload: PriceEstimateRequest) -> PriceEstimateResponse:
    total, area_m2, detail, breakdown = calculate_estimate_kzt(
        service_type=payload.service_type,
        material=payload.material,
        width_cm=payload.width_cm,
        height_cm=payload.height_cm,
        quantity=payload.quantity,
        urgency_days=payload.urgency_days,
        has_design=payload.has_design,
        delivery_type=payload.delivery_type,
    )
    return PriceEstimateResponse(
        estimated_price_kzt=total,
        area_m2=area_m2,
        detail=detail,
        breakdown=breakdown,
    )


@router.post("/proposals", response_model=ProposalResponse)
async def proposals(payload: LeadCreate) -> ProposalResponse:
    return build_tiered_proposal(payload)


@router.post("/creative-copy", response_model=CreativeCopyResponse)
async def creative_copy(payload: CreativeCopyRequest) -> CreativeCopyResponse:
    return await generate_creative_copy(payload)


@router.post("/intake/parse", response_model=ParsedBrief)
async def intake_parse(payload: IntakeParseRequest) -> ParsedBrief:
    return await parse_client_intake(payload)


@router.post("/concepts", response_model=ConceptsResponse)
async def concepts(payload: ConceptsRequest) -> ConceptsResponse:
    return build_concepts(payload.brief)


@router.post("/tradeoff", response_model=ConceptsResponse)
async def tradeoff(payload: TradeoffRequest) -> ConceptsResponse:
    return tune_tradeoff(payload.brief, payload.mode)


@router.post(
    "/leads",
    response_model=LeadRead,
    dependencies=[Depends(require_internal_api_key)],
)
async def create_lead(payload: LeadCreate, db: AsyncSession = Depends(get_db)) -> LeadRead:
    total, _, detail, _ = calculate_estimate_kzt(
        service_type=payload.service_type,
        material=payload.material,
        width_cm=payload.width_cm,
        height_cm=payload.height_cm,
        quantity=payload.quantity,
        urgency_days=payload.urgency_days,
        has_design=payload.has_design,
        delivery_type=payload.delivery_type,
    )
    try:
        ai_summary = await build_lead_summary(payload)
    except Exception:
        ai_summary = "AI summary unavailable"

    entity = Lead(
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        language=payload.language.value,
        service_type=payload.service_type,
        material=payload.material,
        width_cm=payload.width_cm,
        height_cm=payload.height_cm,
        quantity=payload.quantity,
        urgency_days=payload.urgency_days,
        has_design=payload.has_design,
        delivery_type=payload.delivery_type.value,
        delivery_address=payload.delivery_address,
        notes=payload.notes,
        estimated_price_kzt=total,
        estimate_detail=detail,
        ai_summary=ai_summary,
    )
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return LeadRead.model_validate(entity)


@router.post("/deal/confirm", response_model=ConfirmDealResponse)
async def confirm_deal(payload: ConfirmDealRequest, db: AsyncSession = Depends(get_db)) -> ConfirmDealResponse:
    total, _, detail, _ = calculate_estimate_kzt(
        service_type=payload.brief.service_type,
        material=payload.brief.material,
        width_cm=payload.brief.width_cm,
        height_cm=payload.brief.height_cm,
        quantity=payload.brief.quantity,
        urgency_days=payload.brief.urgency_days,
        has_design=payload.brief.has_design,
        delivery_type=payload.brief.delivery_type,
    )
    lead_payload = LeadCreate(
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        language="ru",
        service_type=payload.brief.service_type,
        material=payload.brief.material,
        width_cm=payload.brief.width_cm,
        height_cm=payload.brief.height_cm,
        quantity=payload.brief.quantity,
        urgency_days=payload.brief.urgency_days,
        has_design=payload.brief.has_design,
        delivery_type=payload.brief.delivery_type,
        delivery_address=payload.brief.delivery_address,
        notes=f"selected_concept={payload.selected_concept_id}; {payload.brief.summary}",
    )
    try:
        ai_summary = await build_lead_summary(lead_payload)
    except Exception:
        ai_summary = "AI summary unavailable"

    entity = Lead(
        customer_name=lead_payload.customer_name,
        customer_phone=lead_payload.customer_phone,
        language=lead_payload.language.value,
        service_type=lead_payload.service_type,
        material=lead_payload.material,
        width_cm=lead_payload.width_cm,
        height_cm=lead_payload.height_cm,
        quantity=lead_payload.quantity,
        urgency_days=lead_payload.urgency_days,
        has_design=lead_payload.has_design,
        delivery_type=lead_payload.delivery_type.value,
        delivery_address=lead_payload.delivery_address,
        notes=lead_payload.notes,
        estimated_price_kzt=total,
        estimate_detail=detail,
        ai_summary=ai_summary,
    )
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return ConfirmDealResponse(
        lead_id=entity.id,
        message=f"Deal confirmed. Lead #{entity.id} created.",
    )


@router.get(
    "/leads",
    response_model=LeadListResponse,
    dependencies=[Depends(require_internal_api_key)],
)
async def list_leads(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> LeadListResponse:
    total_query = select(func.count(Lead.id))
    total = (await db.execute(total_query)).scalar_one()

    query = select(Lead).order_by(desc(Lead.created_at)).limit(limit).offset(offset)
    items = (await db.execute(query)).scalars().all()
    return LeadListResponse(
        items=[LeadRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/leads/{lead_id}",
    response_model=LeadRead,
    dependencies=[Depends(require_internal_api_key)],
)
async def get_lead(lead_id: int, db: AsyncSession = Depends(get_db)) -> LeadRead:
    query = select(Lead).where(Lead.id == lead_id)
    lead = (await db.execute(query)).scalar_one_or_none()
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadRead.model_validate(lead)


@router.get(
    "/stats",
    response_model=LeadStatsResponse,
    dependencies=[Depends(require_internal_api_key)],
)
async def lead_stats(db: AsyncSession = Depends(get_db)) -> LeadStatsResponse:
    total_leads = (await db.execute(select(func.count(Lead.id)))).scalar_one()
    avg_check = (await db.execute(select(func.avg(Lead.estimated_price_kzt)))).scalar_one()
    grouped = await db.execute(
        select(Lead.service_type, func.count(Lead.id)).group_by(Lead.service_type)
    )

    by_service: dict[str, int] = {}
    for service_type, count in grouped.all():
        by_service[str(service_type)] = int(count)

    return LeadStatsResponse(
        total_leads=int(total_leads),
        avg_check_kzt=int(avg_check or 0),
        by_service=by_service,
    )
