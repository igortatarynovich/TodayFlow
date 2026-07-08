"""Endpoints for shareable snippets."""

from fastapi import APIRouter, Depends, HTTPException, Request

from todayflow_backend.api.auth import require_user
from todayflow_backend.core import models
from todayflow_backend.i18n import request_locale, translate
from todayflow_backend.services.sharing import SharingService, get_sharing_service

router = APIRouter(prefix="/share", tags=["shareable"])


@router.get("/snippet", response_model=models.ShareableSnippet)
async def get_shareable_snippet(
    request: Request,
    sharing_service: SharingService = Depends(get_sharing_service),
    user=Depends(require_user),
) -> models.ShareableSnippet:
    """Return a snippet pulled from the latest Lite report."""
    try:
        return sharing_service.shareable_snippet(user)
    except ValueError as exc:
        message = translate("sharing.errors.snippetMissing", locale=request_locale(request))
        raise HTTPException(status_code=404, detail=f"{message}: {exc}")
