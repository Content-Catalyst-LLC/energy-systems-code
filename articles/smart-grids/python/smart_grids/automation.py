from __future__ import annotations


def flisr_customer_hours_avoided(
    restored_customers: int,
    manual_restoration_minutes: float,
    automated_restoration_minutes: float,
) -> float:
    if restored_customers < 0:
        raise ValueError("restored_customers must be nonnegative")
    if manual_restoration_minutes < 0 or automated_restoration_minutes < 0:
        raise ValueError("restoration times must be nonnegative")
    minutes_saved = max(
        0.0,
        manual_restoration_minutes - automated_restoration_minutes,
    )
    return restored_customers * minutes_saved / 60.0


def communications_availability(
    primary_availability: float,
    backup_availability: float,
) -> float:
    if not 0 <= primary_availability <= 1:
        raise ValueError("primary availability must be in [0,1]")
    if not 0 <= backup_availability <= 1:
        raise ValueError("backup availability must be in [0,1]")
    # Independent parallel paths: probability at least one is available.
    return 1.0 - (1.0 - primary_availability) * (1.0 - backup_availability)


def restoration_fraction(
    total_customers: int,
    customers_restored: int,
) -> float:
    if total_customers <= 0:
        raise ValueError("total_customers must be positive")
    if not 0 <= customers_restored <= total_customers:
        raise ValueError("customers_restored out of range")
    return customers_restored / total_customers
