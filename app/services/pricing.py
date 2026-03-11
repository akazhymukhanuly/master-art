from dataclasses import dataclass

from app.schemas import DeliveryType


@dataclass(frozen=True)
class ServiceRule:
    base_per_m2: int
    setup_fee: int


@dataclass(frozen=True)
class MaterialRule:
    multiplier: float


SERVICE_RULES = {
    "banner": ServiceRule(base_per_m2=6500, setup_fee=4000),
    "freza": ServiceRule(base_per_m2=8500, setup_fee=6000),
    "laser": ServiceRule(base_per_m2=10000, setup_fee=8000),
    "stand": ServiceRule(base_per_m2=12000, setup_fee=15000),
    "billboard": ServiceRule(base_per_m2=9000, setup_fee=12000),
    "design": ServiceRule(base_per_m2=3500, setup_fee=12000),
}

MATERIAL_RULES = {
    "banner_frontlit": MaterialRule(multiplier=1.0),
    "banner_blockout": MaterialRule(multiplier=1.22),
    "acrylic_3mm": MaterialRule(multiplier=1.5),
    "acrylic_5mm": MaterialRule(multiplier=1.8),
    "composite_panel": MaterialRule(multiplier=1.7),
    "film_oracal": MaterialRule(multiplier=1.2),
}

DELIVERY_FEE_KZT = 7000
DESIGN_FEE_KZT = 12000


def normalize_service(service_type: str) -> str:
    key = service_type.strip().lower()
    mapping = {
        "banner": "banner",
        "баннер": "banner",
        "freza": "freza",
        "фреза": "freza",
        "фрезамен кесу": "freza",
        "laser": "laser",
        "лазер": "laser",
        "stand": "stand",
        "стенд": "stand",
        "billboard": "billboard",
        "билборд": "billboard",
        "design": "design",
        "дизайн": "design",
        "corel дизайн": "design",
    }
    return mapping.get(key, "banner")


def normalize_material(material: str) -> str:
    key = material.strip().lower()
    aliases = {
        "frontlit": "banner_frontlit",
        "blockout": "banner_blockout",
        "oracal": "film_oracal",
    }
    normalized = aliases.get(key, key)
    if normalized not in MATERIAL_RULES:
        return "banner_frontlit"
    return normalized


def urgency_multiplier(urgency_days: int) -> float:
    if urgency_days <= 1:
        return 1.50
    if urgency_days == 2:
        return 1.25
    return 1.00


def quantity_discount(quantity: int) -> float:
    if quantity >= 50:
        return 0.90
    if quantity >= 20:
        return 0.94
    if quantity >= 10:
        return 0.97
    return 1.00


def calculate_estimate_kzt(
    service_type: str,
    material: str,
    width_cm: int,
    height_cm: int,
    quantity: int = 1,
    urgency_days: int = 3,
    has_design: bool = False,
    delivery_type: DeliveryType = DeliveryType.PICKUP,
) -> tuple[int, float, str, dict[str, int]]:
    service_key = normalize_service(service_type)
    material_key = normalize_material(material)

    service = SERVICE_RULES[service_key]
    material_rule = MATERIAL_RULES[material_key]
    area_m2 = (width_cm / 100) * (height_cm / 100)

    base_cost = int(service.base_per_m2 * area_m2 * quantity)
    setup_cost = service.setup_fee
    material_surcharge = int(base_cost * (material_rule.multiplier - 1.0))
    design_cost = DESIGN_FEE_KZT if has_design else 0
    logistic_cost = DELIVERY_FEE_KZT if delivery_type == DeliveryType.DELIVERY else 0

    subtotal = base_cost + setup_cost + material_surcharge + design_cost + logistic_cost
    after_discount = int(subtotal * quantity_discount(quantity))
    total = int(after_discount * urgency_multiplier(urgency_days))

    breakdown = {
        "base_cost": base_cost,
        "setup_cost": setup_cost,
        "material_surcharge": material_surcharge,
        "design_cost": design_cost,
        "logistic_cost": logistic_cost,
        "discounted_subtotal": after_discount,
    }
    detail = (
        f"service={service_key}, material={material_key}, area_m2={area_m2:.2f}, "
        f"qty={quantity}, urgency_days={urgency_days}, has_design={has_design}, "
        f"delivery={delivery_type.value}"
    )
    return total, round(area_m2, 2), detail, breakdown

