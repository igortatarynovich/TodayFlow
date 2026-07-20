"""Aggregate API router."""

from fastapi import APIRouter

from todayflow_backend.api import (
    admin,
    auth,
    compatibility,
    forecasts,
    full_reports,
    library,
    payments,
    questions,
    reports,
    geocode,
    reference,
    tarot,
    celestial,
    aspects,
    sharing,
    numerology,
    account,
    intake,
    subscriptions,
    horoscopes,
    journal,
    challenges,
    practices,
    promo_codes,
    oauth,
    thematic_reports,
    tracking,
    generate,
    calendar,
    morning_ritual,
    natal_chart,
    day_flow,
    day_symbols,
    guest_claim,
    habits,
    learning,
    meaning,
)
from todayflow_backend.api import day_connection, today
from todayflow_backend.api import push_notifications

router = APIRouter()
router.include_router(auth.router)
router.include_router(day_symbols.router)
router.include_router(guest_claim.router)
router.include_router(payments.router)
router.include_router(subscriptions.router)
router.include_router(questions.router)
router.include_router(reports.router)
router.include_router(forecasts.router)
router.include_router(library.router)
router.include_router(full_reports.router)
router.include_router(admin.router)
router.include_router(geocode.router)
router.include_router(reference.router)
router.include_router(tarot.router)
router.include_router(celestial.router)
router.include_router(aspects.router)
router.include_router(sharing.router)
router.include_router(numerology.router)
router.include_router(account.router)
router.include_router(intake.router)
router.include_router(horoscopes.router)
router.include_router(compatibility.router)
router.include_router(journal.router)
router.include_router(challenges.router)
router.include_router(practices.router)
router.include_router(promo_codes.router)
router.include_router(oauth.router)
router.include_router(thematic_reports.router)
router.include_router(tracking.router)
router.include_router(generate.router)
router.include_router(calendar.router)
router.include_router(morning_ritual.router)
router.include_router(natal_chart.router)
router.include_router(day_flow.router)
router.include_router(day_connection.router)
router.include_router(today.router)
router.include_router(habits.router)
router.include_router(learning.router)
router.include_router(meaning.router)
router.include_router(push_notifications.router)
router.include_router(push_notifications.internal_router)
