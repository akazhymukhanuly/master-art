from app.schemas import ConceptCard, ConceptsResponse, DeliveryType, ParsedBrief
from app.services.pricing import calculate_estimate_kzt


def _build_card(
    card_id: str,
    title: str,
    angle: str,
    tagline: str,
    brief: ParsedBrief,
    material: str,
    eta_days: int,
    has_design: bool,
    delivery_type: DeliveryType,
    score: int,
    why: list[str],
) -> ConceptCard:
    total, _, _, _ = calculate_estimate_kzt(
        service_type=brief.service_type,
        material=material,
        width_cm=brief.width_cm,
        height_cm=brief.height_cm,
        quantity=brief.quantity,
        urgency_days=eta_days,
        has_design=has_design,
        delivery_type=delivery_type,
    )
    return ConceptCard(
        id=card_id,
        title=title,
        angle=angle,
        tagline=tagline,
        material=material,
        eta_days=eta_days,
        estimated_price_kzt=total,
        score=score,
        why=why,
    )


def build_concepts(brief: ParsedBrief) -> ConceptsResponse:
    cards = [
        _build_card(
            card_id="economy",
            title="Economy Reach",
            angle="Max visibility for minimal budget",
            tagline="Seen by everyone, paid like smart.",
            brief=brief,
            material="banner_frontlit",
            eta_days=max(brief.urgency_days, 4),
            has_design=False,
            delivery_type=DeliveryType.PICKUP,
            score=76,
            why=["Lowest price", "Fast standard production", "Good street visibility"],
        ),
        _build_card(
            card_id="balanced",
            title="Balanced Conversion",
            angle="Best mix of quality and conversion",
            tagline="Look premium, sell faster.",
            brief=brief,
            material="banner_blockout",
            eta_days=max(brief.urgency_days, 3),
            has_design=True,
            delivery_type=brief.delivery_type,
            score=89,
            why=["Higher print contrast", "Includes design support", "Recommended for most businesses"],
        ),
        _build_card(
            card_id="premium",
            title="Premium Brand Lift",
            angle="Memorable brand presence",
            tagline="Premium look clients trust.",
            brief=brief,
            material="acrylic_5mm",
            eta_days=max(brief.urgency_days, 2),
            has_design=True,
            delivery_type=DeliveryType.DELIVERY,
            score=93,
            why=["Premium material", "Highest perceived quality", "Includes delivery and design"],
        ),
    ]
    return ConceptsResponse(brief=brief, cards=cards, recommended_id="balanced")


def tune_tradeoff(brief: ParsedBrief, mode: str) -> ConceptsResponse:
    tuned = brief.model_copy()
    if mode == "cheaper":
        tuned.material = "banner_frontlit"
        tuned.has_design = False
        tuned.delivery_type = DeliveryType.PICKUP
        tuned.urgency_days = max(3, tuned.urgency_days)
    elif mode == "faster":
        tuned.urgency_days = 1
        tuned.delivery_type = DeliveryType.DELIVERY
        tuned.has_design = True
    else:
        tuned.material = "acrylic_5mm"
        tuned.has_design = True
        tuned.delivery_type = DeliveryType.DELIVERY
    return build_concepts(tuned)

