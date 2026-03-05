# MacrocenterConnector parser behavior

`MacrocenterConnector.parse(raw)` outputs normalized snapshot fields:
- `in_stock`
- `stock_text`
- `price`
- `currency`
- `raw_payload` diagnostics (`stock_selector`, `price_selector`)

## Stock extraction order
1. `[data-testid='pdp-inventory-status']`
2. `.inventory-status`
3. `#inventory`

If text contains `out of stock`, `sold out`, or `unavailable`, parser sets `in_stock=False`.
Any other non-empty stock text is treated as available.

## Price extraction order
1. `[data-testid='price']`
2. `.product-price`
3. `[itemprop='price']`
4. JSON-LD `offers.price`

Currency is inferred from text (`USD`, `RON`, `EUR`, `GBP`) or `meta[property='product:price:currency']`.

## Errors
- Empty payload raises `ValueError("empty payload")`.
- Parsing failures stay localized to a product; workflow logs the exception and continues.
