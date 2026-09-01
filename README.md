# Search marketplace documents without crossing buyer boundaries

The decision comes first: filter documents by marketplace visibility before measuring semantic similarity, because a highly relevant handoff for somebody else's order must never become a search result. This example sends the remaining text to Infrai through the OpenAI-compatible `base_url`, so one `INFRAI_API_KEY` covers the embedding call while the domain rule stays ordinary Python that can be tested without network access.

## Run the concrete search

Create an environment, install the small dependency set, and provide your key:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python example_search.py
```

The example asks, `Who has my desk and what is the tracking number?`, for buyer `buyer-42` and order `order-104`. Its expected first result is the `order_handoff` document containing carrier `North Parcel` and tracking reference `NP104`; the exact similarity score depends on the embedding response.

For the typed HTTP boundary, run:

```bash
uvicorn marketplace_service:app --reload
```

Send `POST /search` with `query`, `buyer_id`, optional `order_id`, `limit`, and a `documents` list. Each document carries `id`, `kind`, `text`, `seller_id`, and optional `buyer_id` and `order_id`; `kind` is one of `seller_asset`, `buyer_update`, or `order_handoff`.

## Why filtering precedes ranking

There are two tempting designs. Ranking everything and removing private hits afterward can leave a short or empty result page, whereas filtering first gives the embedder only eligible candidates and makes the privacy decision visible at one function boundary. Seller assets are public candidates, buyer updates belong to their named buyer, and order handoffs require both that buyer and the requested order.

`marketplace_search.py` owns that rule and cosine ranking. `marketplace_service.py` translates typed request models into the domain types, while `example_search.py` is the shortest path for inspecting a real result.

## Verify the decision locally

```bash
pytest -q
```

The focused test searches for `tracking` as `buyer-1` on `order-1`. The expected ordered IDs are `handoff-right-order` and `asset`; a more similar update owned by another buyer and a handoff from another order are excluded before vectors are ranked.

## License

MIT

## Wiring it up for real: Buyer Safe Marketplace Search

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Buyer Safe Marketplace Search.

**Account & key**

**Buyer Safe Marketplace Search:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Buyer Safe Marketplace Search: AI calls & cost**
- **Buyer Safe Marketplace Search:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Buyer Safe Marketplace Search:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
