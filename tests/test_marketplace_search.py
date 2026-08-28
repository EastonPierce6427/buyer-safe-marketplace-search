from marketplace_search import (
    DocumentKind,
    MarketplaceDocument,
    SearchContext,
    search_marketplace,
)


class FixedEmbedder:
    def embed(self, texts):
        vectors = {
            "tracking": [1.0, 0.0],
            "public listing": [0.0, 1.0],
            "other buyer tracking": [1.0, 0.0],
            "this order tracking": [0.9, 0.1],
            "different order tracking": [1.0, 0.0],
        }
        return [vectors[text] for text in texts]


def test_search_ranks_only_documents_visible_to_the_buyer_and_order():
    documents = [
        MarketplaceDocument(
            id="asset",
            kind=DocumentKind.SELLER_ASSET,
            seller_id="seller-1",
            text="public listing",
        ),
        MarketplaceDocument(
            id="private-other-buyer",
            kind=DocumentKind.BUYER_UPDATE,
            seller_id="seller-1",
            buyer_id="buyer-2",
            text="other buyer tracking",
        ),
        MarketplaceDocument(
            id="handoff-right-order",
            kind=DocumentKind.ORDER_HANDOFF,
            seller_id="seller-1",
            buyer_id="buyer-1",
            order_id="order-1",
            text="this order tracking",
        ),
        MarketplaceDocument(
            id="handoff-wrong-order",
            kind=DocumentKind.ORDER_HANDOFF,
            seller_id="seller-1",
            buyer_id="buyer-1",
            order_id="order-2",
            text="different order tracking",
        ),
    ]

    hits = search_marketplace(
        documents,
        SearchContext(query="tracking", buyer_id="buyer-1", order_id="order-1"),
        FixedEmbedder(),
    )

    assert [hit.document.id for hit in hits] == ["handoff-right-order", "asset"]
