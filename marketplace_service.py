"""Typed HTTP entry point for marketplace document search."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from marketplace_search import (
    DocumentKind,
    InfraiEmbedder,
    MarketplaceDocument,
    SearchContext,
    search_marketplace,
)


class DocumentInput(BaseModel):
    id: str
    kind: Literal["seller_asset", "buyer_update", "order_handoff"]
    text: str
    seller_id: str
    buyer_id: str | None = None
    order_id: str | None = None


class MarketplaceSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    buyer_id: str = Field(min_length=1)
    order_id: str | None = None
    limit: int = Field(default=3, ge=1, le=20)
    documents: list[DocumentInput] = Field(min_length=1)


class SearchResult(BaseModel):
    id: str
    kind: str
    text: str
    score: float


class MarketplaceSearchResponse(BaseModel):
    results: list[SearchResult]


app = FastAPI(title="Marketplace document search")


@lru_cache
def get_embedder() -> InfraiEmbedder:
    return InfraiEmbedder(api_key=os.environ["INFRAI_API_KEY"])


@app.post("/search", response_model=MarketplaceSearchResponse)
def search(request: MarketplaceSearchRequest) -> MarketplaceSearchResponse:
    documents = [
        MarketplaceDocument(
            id=item.id,
            kind=DocumentKind(item.kind),
            text=item.text,
            seller_id=item.seller_id,
            buyer_id=item.buyer_id,
            order_id=item.order_id,
        )
        for item in request.documents
    ]
    context = SearchContext(
        query=request.query,
        buyer_id=request.buyer_id,
        order_id=request.order_id,
        limit=request.limit,
    )
    hits = search_marketplace(documents, context, get_embedder())
    return MarketplaceSearchResponse(
        results=[
            SearchResult(
                id=hit.document.id,
                kind=hit.document.kind.value,
                text=hit.document.text,
                score=hit.score,
            )
            for hit in hits
        ]
    )
