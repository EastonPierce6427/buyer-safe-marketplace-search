"""Run one marketplace search without starting the HTTP service."""

import os

from marketplace_search import (
    DocumentKind,
    InfraiEmbedder,
    MarketplaceDocument,
    SearchContext,
    search_marketplace,
)


documents = [
    MarketplaceDocument(
        id="asset-sizing",
        kind=DocumentKind.SELLER_ASSET,
        seller_id="seller-7",
        text="The walnut desk is 120 cm wide and ships flat-packed.",
    ),
    MarketplaceDocument(
        id="update-104",
        kind=DocumentKind.BUYER_UPDATE,
        seller_id="seller-7",
        buyer_id="buyer-42",
        text="Your walnut desk has passed its final quality check.",
    ),
    MarketplaceDocument(
        id="handoff-104",
        kind=DocumentKind.ORDER_HANDOFF,
        seller_id="seller-7",
        buyer_id="buyer-42",
        order_id="order-104",
        text="Order 104 was handed to North Parcel; tracking is NP104.",
    ),
]

context = SearchContext(
    query="Who has my desk and what is the tracking number?",
    buyer_id="buyer-42",
    order_id="order-104",
    limit=2,
)
hits = search_marketplace(
    documents,
    context,
    InfraiEmbedder(api_key=os.environ["INFRAI_API_KEY"]),
)

for hit in hits:
    print(f"{hit.score:.3f}  {hit.document.kind.value}  {hit.document.text}")
