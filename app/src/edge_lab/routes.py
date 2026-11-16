from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError

from edge_lab.codes import new_code
from edge_lab.config import BASE_URL, CODE_LENGTH
from edge_lab.db import DbSession
from edge_lab.models import Link
from edge_lab.schemas import LinkCreate, LinkCreated

router = APIRouter()
MAX_CODE_ATTEMPTS = 3

OwnerKey = Annotated[str, Header(alias="X-Owner-Key")]


@router.post("/api/links", response_model=LinkCreated, status_code=status.HTTP_201_CREATED)
def create_link(payload: LinkCreate, db: DbSession) -> LinkCreated:
    for _ in range(MAX_CODE_ATTEMPTS):
        link = Link(
            code=new_code(CODE_LENGTH),
            url=str(payload.url),
            owner_key=payload.owner_key,
        )
        db.add(link)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            continue
        return LinkCreated(
            code=link.code,
            short_url=f"{BASE_URL}/{link.code}",
            url=link.url,
        )
    raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "code allocation failed")


@router.get("/{code}")
def redirect(code: str, db: DbSession) -> RedirectResponse:
    link = db.get(Link, code)
    if link is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "unknown code")
    return RedirectResponse(link.url, status_code=status.HTTP_302_FOUND)


@router.delete("/api/links/{code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(code: str, db: DbSession, owner_key: OwnerKey) -> Response:
    link = db.get(Link, code)
    if link is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "unknown code")
    if link.owner_key != owner_key:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "not the owner")
    db.delete(link)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
