# MacrocenterConnector parser behavior

`MacrocenterConnector.parse(raw)` normalizes a Micro Center product page into:

- `in_stock` (`bool`)
- `stock_text` (`str | None`)
- `price` (`Decimal | None`)
- `currency` (`str | None`)
- `raw_payload` metadata for diagnostics

## Stock signal rules

Stock text is read from the first selector that returns non-empty text:

1. `[data-testid='pdp-inventory-status']`
2. `.inventory-status`
3. `.inventory`
4. `#inventory`

Normalization and interpretation:

- Text is whitespace-compacted before use.
- If text contains any of: `out of stock`, `sold out`, `unavailable`, `backorder` -> `in_stock=False`.
- If text contains any of: `in stock`, `available`, `pickup today`, `limited availability` -> `in_stock=True`.
- Missing/unknown text defaults to `in_stock=False`.

## Price signal rules

Price text is read from the first selector that returns non-empty text/content:

1. `[data-testid='price']`
2. `.product-price`
3. `.price`
4. `meta[property='product:price:amount']` (`content` attribute)

Fallback strategy:

- If selector search fails, parser attempts `script[type='application/ld+json']` and extracts a `"price"` key value using a lightweight string scan.

Price normalization:

- Remove `$`, `USD`, commas.
- Parse with `Decimal`; invalid values become `price=None`.
- Currency defaults to `USD` if `$` exists in raw price text.
- Currency is overridden if `meta[property='product:price:currency']` is present.

## Diagnostics and error handling

- Empty payload raises `ValueError("Micro Center parse failed: empty payload")`.
- Successful parses include `raw_payload` metadata keys:
  - `stock_selector`
  - `price_selector`
  - `stock_raw`
  - `price_raw`

This keeps failures localized and gives actionable parser diagnostics without crashing unrelated product checks.
