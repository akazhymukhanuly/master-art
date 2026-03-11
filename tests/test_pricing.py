from app.schemas import DeliveryType
from app.services.pricing import calculate_estimate_kzt


def test_estimate_increases_with_urgency():
    normal, _, _, _ = calculate_estimate_kzt(
        service_type="banner",
        material="banner_frontlit",
        width_cm=200,
        height_cm=100,
        quantity=1,
        urgency_days=3,
    )
    urgent, _, _, _ = calculate_estimate_kzt(
        service_type="banner",
        material="banner_frontlit",
        width_cm=200,
        height_cm=100,
        quantity=1,
        urgency_days=1,
    )
    assert urgent > normal


def test_estimate_increases_with_delivery_and_design():
    base, _, _, _ = calculate_estimate_kzt(
        service_type="banner",
        material="banner_frontlit",
        width_cm=200,
        height_cm=100,
        quantity=1,
        urgency_days=3,
        has_design=False,
        delivery_type=DeliveryType.PICKUP,
    )
    premium, _, _, _ = calculate_estimate_kzt(
        service_type="banner",
        material="banner_frontlit",
        width_cm=200,
        height_cm=100,
        quantity=1,
        urgency_days=3,
        has_design=True,
        delivery_type=DeliveryType.DELIVERY,
    )
    assert premium > base


def test_discount_applies_on_large_quantity():
    unit, _, _, _ = calculate_estimate_kzt(
        service_type="banner",
        material="banner_frontlit",
        width_cm=100,
        height_cm=100,
        quantity=1,
        urgency_days=3,
    )
    bulk, _, _, _ = calculate_estimate_kzt(
        service_type="banner",
        material="banner_frontlit",
        width_cm=100,
        height_cm=100,
        quantity=50,
        urgency_days=3,
    )
    assert bulk < unit * 50

