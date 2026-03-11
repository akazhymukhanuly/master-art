from app.schemas import DeliveryType, ParsedBrief
from app.services.concepts import build_concepts, tune_tradeoff


def sample_brief() -> ParsedBrief:
    return ParsedBrief(
        summary="Need visible coffee shop banner",
        service_type="banner",
        material="banner_frontlit",
        width_cm=300,
        height_cm=120,
        quantity=1,
        urgency_days=3,
        has_design=True,
        delivery_type=DeliveryType.PICKUP,
        delivery_address="",
        audience="coffee lovers",
        style_hint="warm premium",
    )


def test_build_concepts_returns_three_cards():
    result = build_concepts(sample_brief())
    assert len(result.cards) == 3
    assert result.recommended_id in {card.id for card in result.cards}


def test_tradeoff_cheaper_reduces_premium_bias():
    base = build_concepts(sample_brief())
    cheaper = tune_tradeoff(sample_brief(), "cheaper")
    assert cheaper.brief.has_design is False
    assert cheaper.brief.delivery_type == DeliveryType.PICKUP
    assert base.recommended_id == "balanced"

