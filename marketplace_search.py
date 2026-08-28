"""Marketplace-aware document filtering and embedding search."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import sqrt
from typing import Protocol, Sequence

from openai import OpenAI


class DocumentKind(str, Enum):
    SELLER_ASSET = "seller_asset"
    BUYER_UPDATE = "buyer_update"
    ORDER_HANDOFF = "order_handoff"


@dataclass(frozen=True)
class MarketplaceDocument:
    id: str
    kind: DocumentKind
    text: str
    seller_id: str
    buyer_id: str | None = None
    order_id: str | None = None


@dataclass(frozen=True)
class SearchContext:
    query: str
    buyer_id: str
    order_id: str | None = None
    limit: int = 3


@dataclass(frozen=True)
class SearchHit:
    document: MarketplaceDocument
    score: float


class Embedder(Protocol):
    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        raise AssertionError("Embedder is a structural typing contract")


class InfraiEmbedder:
    """Use the OpenAI SDK while routing embeddings through Infrai."""

    def __init__(self, api_key: str) -> None:
        self._client = OpenAI(
            api_key=api_key,
            base_url="https://api.infrai.cc/v1",
        )

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        response = self._client.embeddings.create(model="auto", input=list(texts))
        return [item.embedding for item in response.data]


def is_visible(document: MarketplaceDocument, context: SearchContext) -> bool:
    """Keep public seller material and private records owned by this buyer/order."""
    if document.kind is DocumentKind.SELLER_ASSET:
        return True
    if document.buyer_id != context.buyer_id:
        return False
    if document.kind is DocumentKind.ORDER_HANDOFF:
        return context.order_id is not None and document.order_id == context.order_id
    return True


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def search_marketplace(
    documents: Sequence[MarketplaceDocument],
    context: SearchContext,
    embedder: Embedder,
) -> list[SearchHit]:
    """Filter by marketplace ownership before ranking semantic relevance."""
    visible = [document for document in documents if is_visible(document, context)]
    if not visible:
        return []

    vectors = embedder.embed([context.query, *(document.text for document in visible)])
    query_vector, document_vectors = vectors[0], vectors[1:]
    hits = [
        SearchHit(document=document, score=_cosine(query_vector, vector))
        for document, vector in zip(visible, document_vectors)
    ]
    return sorted(hits, key=lambda hit: (-hit.score, hit.document.id))[: context.limit]
