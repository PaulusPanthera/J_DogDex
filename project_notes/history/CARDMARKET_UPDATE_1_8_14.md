# DogDex 1.8.14 — Reuse Cardmarket matches and open filtered offers

## What changes

The product finder now starts from the current confirmed product ID, otherwise the saved listing URL, otherwise the card name. Its context includes a direct Saved listing link. Current matches and existing references appear before the broad product catalogue; unrelated catalogue matches are folded away when references exist. A confirmed related match has a **Reuse product** button. **Search all [card name] products** keeps wider discovery available.

The finder reads the merged collector catalogue, including manual corrections and saved matches. It no longer searches only original provider records when suggesting a matching EN/DE reference. A German standard-layout card and its English shadowed counterpart can share a reference without treating that layout terminology difference as a different marketplace product.

## Confirm selected related printings once

After selecting a product, a checklist identifies the related printings eligible for the same product. The current printing stays selected; other eligible entries can be deselected before saving. One confirmation saves the selected mappings atomically. Entries sharing an existing canonical listing or an already confirmed product can participate, subject to the same numbered card identity, language family and compatible physical features.

Product reuse does not merge physical printings or change their verification. It does not establish a new language release. Only existing active, documented collection targets participate. Excluded, provisional and disputed identities/printings are not promoted. JA/KO do not acquire EN/DE mappings.

Existing conflicting confirmed products are not overwritten by batch selection. Stale identities or printing changes invalidate the whole requested batch before any write. Existing confirmed guide-series choices on related printings are preserved. New reverse-holo mappings receive the reverse series, while other printings use the regular series. The current printing's series remains directly editable.

### English/German Base Set Growlithe example

| Existing printing | Canonical Cardmarket listing | Generated offer filters |
|---|---|---|
| German Unlimited | Growlithe V1 BS28 | German, not First Edition, not reverse |
| German First Edition | Growlithe V1 BS28 | German, First Edition, not reverse |
| English Unlimited | Growlithe V1 BS28 | English, not First Edition, not reverse |
| English 1999–2000 copyright | Growlithe V1 BS28 | English, not First Edition, not reverse |
| English First Edition / Shadowless | Growlithe V2 BS28 | English, First Edition, not reverse |
| English Shadowless without stamp | Growlithe V2 BS28 | English, not First Edition, not reverse |

The V1 and V2 families remain separate. The copyright variation retains its own collectible ID; a listing filter cannot distinguish that copyright line. Special foil patterns, stamps and specimen details still require inspecting the actual offer where Cardmarket provides no corresponding filter.

## Offer links and guide prices

Known product links automatically apply the current ledger's language, the printing's First Edition status and reverse-holo status. A compact minimum-condition selector defaults to **Excellent+** and is saved in that browser. It also works in the read-only mobile export. Changing these controls changes the outgoing offers link, not the guide price.

Language IDs are EN 1, DE 3, JA 7 and KO 10. Website minimum-condition values are exposed as named choices rather than requiring users to edit query strings. Other query parameters on an existing outgoing link are retained where applicable; owned filter parameters are set from the currently displayed printing and preference. Product confirmations store canonical product identity without baking a particular offer language or condition into a shared mapping.

The gallery price has a small **Guide** label. Its tooltip and the expandable **Cardmarket guide** identify product-wide scope, including available editions, languages and conditions. There are no new filtered or live asking-price figures in this release.

The official Pokémon JSON guide inspected during the preceding workflow review contains `idProduct`, `idCategory`, averages, low/trend and corresponding `-holo` fields. It has no language, condition or edition dimensions. The inspected source snapshot was created at `2026-10-31T02:42:33+0100`. Appending offer filters to a URL cannot create those missing dimensions.

## Preserved data and installation

All catalogue data, card/printing IDs, ownership quantities, paid costs, wishlists, manual corrections, images and source covers remain intact. No schema migration is needed; matching uses the existing printing-overrides table and backup format. A personal backup preserves the matching records; provider product/price caches continue to be separate downloads. The prior image-health fix and the 1.8.12 data corrections remain included in the full package.

1. Close DogDex.
2. Merge **DogDex_Cardmarket_Update_1_8_14.zip** directly into **J_DogDex**, replacing only its supplied files.
3. Restart DogDex and refresh the browser, using Ctrl+F5 if necessary.
4. Open the printing, choose **Find Cardmarket product** or **Change product**, select the existing/reusable product, review the related-printing checkboxes, and confirm once.
5. Re-export the mobile viewer and commit/push `docs` through GitHub Desktop to publish the updated links and guide labels.

The patch contains no `data`, `my_collection`, runtime or generated `docs` files. Applying it does not perform a bulk matching operation automatically. The collector chooses the mappings from the existing finder.

## Known limits and sources

An arbitrary readable Cardmarket URL does not encode its numeric product ID. When no saved/provider reference connects a URL to an ID, the finder keeps the listing visible and offers catalogue discovery; it never treats a trailing collector number as an ID. Batch reuse is limited to compatible recorded relationships, not a blanket assumption that all English and German editions share one listing.

The supplied product pages returned access restrictions during the preceding research. This patch builds their filters from the supplied URL examples, Cardmarket's attribute/language documentation and the existing catalogue relationships. It does not scrape offer pages or bypass those restrictions.

- Official Pokémon product catalogue: https://downloads.s3.cardmarket.com/productCatalog/productList/products_singles_6.json
- Official Pokémon price guide: https://downloads.s3.cardmarket.com/productCatalog/priceGuide/price_guide_6.json
- Cardmarket Pokémon listing attributes: https://help.cardmarket.com/en/finding-and-listing-pokemon-cards
- Cardmarket API language/offer documentation (historical schema): https://api.cardmarket.com/ws/documentation/API_2.0:Articles
- Cardmarket announcement of public data downloads: https://news.cardmarket.com/en/StarWarsUnlimited/were-making-the-price-guide-and-product-catalogue-available-for-download

See `CARDMARKET_VALIDATION_1_8_14.md` for checks and limits.
