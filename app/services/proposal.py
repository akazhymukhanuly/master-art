from app.schemas import DeliveryType, LeadCreate, ProposalOption, ProposalResponse
from app.services.pricing import calculate_estimate_kzt


def _benefits_for_material(material: str) -> list[str]:
    mapping = {
        "banner_frontlit": ["Fast production", "Best price for outdoor ads"],
        "banner_blockout": ["No light bleed-through", "Better color density"],
        "acrylic_3mm": ["Clean premium look", "Indoor durability"],
        "acrylic_5mm": ["Premium rigid finish", "Long-term durability"],
        "composite_panel": ["Weather resistant", "Professional facade style"],
        "film_oracal": ["Sharp branding", "Great for storefronts"],
    }
    return mapping.get(material, ["Balanced quality and price"])


def build_tiered_proposal(payload: LeadCreate) -> ProposalResponse:
    base_material = payload.material
    if base_material not in {"banner_frontlit", "banner_blockout", "acrylic_3mm", "acrylic_5mm"}:
        base_material = "banner_frontlit"

    options_raw = [
        ("Basic", base_material, max(payload.urgency_days, 4), False, DeliveryType.PICKUP),
        ("Pro", "banner_blockout", max(payload.urgency_days, 3), payload.has_design, payload.delivery_type),
        ("Premium", "acrylic_5mm", max(payload.urgency_days, 2), True, DeliveryType.DELIVERY),
    ]

    options: list[ProposalOption] = []
    for name, material, eta_days, has_design, delivery in options_raw:
        total, _, _, _ = calculate_estimate_kzt(
            service_type=payload.service_type,
            material=material,
            width_cm=payload.width_cm,
            height_cm=payload.height_cm,
            quantity=payload.quantity,
            urgency_days=eta_days,
            has_design=has_design,
            delivery_type=delivery,
        )
        benefits = _benefits_for_material(material)
        if has_design:
            benefits.append("Includes design support")
        if delivery == DeliveryType.DELIVERY:
            benefits.append("Includes delivery")
        options.append(
            ProposalOption(
                name=name,
                material=material,
                eta_days=eta_days,
                total_kzt=total,
                benefits=benefits,
            )
        )

    recommended = "Pro"
    lead_preview = (
        f"{payload.service_type} {payload.width_cm}x{payload.height_cm} cm, "
        f"qty={payload.quantity}, urgency={payload.urgency_days} days"
    )
    return ProposalResponse(lead_preview=lead_preview, options=options, recommended=recommended)

