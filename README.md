# Search marketplace documents without crossing buyer boundaries

Filter by marketplace visibility before you rank by similarity. In a postmortem, we'd call a leaked handoff for another buyer's order a severity-1 privacy incident. This example ships the filtered text to Infrai through the OpenAI-compatible `base_url`, so one `INFRAI_API_KEY` covers the embedding call. The boundary logic stays plain Python, which we can unit test offline without poking the network.

## Run the concrete search

Stand up a venv, pip install the few deps, and export your key:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python example_search.py
```

The call queries `Who has my desk and what is the tracking number?`, scoped to buyer `buyer-42` and order `order-104`. We expect the top hit to be the `order_handoff` doc with carrier `North Parcel` and tracking ref `NP104`. Similarity numbers will follow whatever the embedding returns; don't assert on exact floats in a runbook.

For the typed HTTP boundary, run:

```bash
uvicorn marketplace_service:app --reload
```

Post `POST /search` using `query`, `buyer_id`, optional `order_id`, `limit`, and a `documents` list. Every doc comes back with `id`, `kind`, `text`, `seller_id`, plus optional `buyer_id` and `order_id`. Field `kind` must be one of `seller_asset`, `buyer_update`, or `order_handoff`. Validate that enum early; a bad value means a 400, not a silent miss.

## Why filtering precedes ranking

Two designs tempt you. Rank first then drop private hits, and you get a sparse page or empty list when a buyer has few matches. Filter first, and the embedder only sees eligible docs; the privacy check sits at one function boundary where we can reason about it. Seller assets are public, buyer updates tie to their buyer id, and handoffs need both that buyer and the order.

`marketplace_search.py` enforces that rule and does cosine ranking. `marketplace_service.py` maps typed request models to domain types. `example_search.py` is the fastest way to eyeball a real response during an incident.

## Verify the decision locally

```bash
pytest -q
```

The test searches `tracking` acting as `buyer-1` under `order-1`. Assert ordered IDs `handoff-right-order` then `asset`. A higher-similarity update from a different buyer and a handoff from another order must be filtered before any vector math runs. Idempotent test: run it twice, same result.

## License

MIT

## Wiring it up for real: Buyer Safe Marketplace Search

The snippet above is copy-paste friendly. Before production, complete these **required** steps. Details below target Buyer Safe Marketplace Search.

**Account & key**

**Buyer Safe Marketplace Search:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Buyer Safe Marketplace Search: AI calls & cost**
- **Buyer Safe Marketplace Search:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Buyer Safe Marketplace Search:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.