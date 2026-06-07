from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status

from app.api.v1.endpoints.auth import get_current_user
from app.models.journal import JournalEntry, JournalEntryCreate, JournalEntryUpdate
from app.models.user import User
from app.services.cache import cache_service, journal_list_cache_key
from app.services.journal import journal_service

router = APIRouter()


@router.get(
    "/journal",
    summary="List journal entries",
    description="Returns journal entries for the authenticated user. "
    "Responses include an `X-Cache` header (`HIT` or `MISS`) indicating "
    "whether the data was served from Redis.",
    response_model=List[JournalEntry],
)
async def get_journal_entries(
    response: Response,
    current_user: User = Depends(get_current_user),
):
    """Retrieve journal entries for the authenticated user."""
    # Peek at the cache to determine hit/miss before the service call
    cache_key = journal_list_cache_key(current_user.id)
    cached = await cache_service.get_json(cache_key)
    if cached is not None:
        response.headers["X-Cache"] = "HIT"
        return [JournalEntry(**item) for item in cached]

    entries = await journal_service.list_entries(current_user.id)
    response.headers["X-Cache"] = "MISS"
    return entries


@router.post(
    "/journal",
    summary="Create a journal entry",
    response_model=JournalEntry,
    status_code=status.HTTP_201_CREATED,
)
async def create_journal_entry(
    entry: JournalEntryCreate = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Create a new journal entry for the authenticated user."""
    return await journal_service.create_entry(current_user.id, entry)


@router.put(
    "/journal/{entry_id}",
    summary="Update a journal entry",
    response_model=JournalEntry,
)
async def update_journal_entry(
    entry_id: str,
    entry: JournalEntryUpdate = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Update an existing journal entry for the authenticated user."""
    updated = await journal_service.update_entry(current_user.id, entry_id, entry)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found")
    return updated


@router.delete(
    "/journal/{entry_id}",
    summary="Delete a journal entry",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a journal entry for the authenticated user."""
    deleted = await journal_service.delete_entry(current_user.id, entry_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found")
