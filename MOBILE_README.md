# DogDex on PC and mobile — version 1.8.6

1.8.6 adds the reviewed printing corrections and preserves the 1.8.5 source navigation. After updating the PC, export the read-only mobile view again, then Commit and Push. Keep my_collection.

1.8.5 unifies expansion subsets and separates retail distributions in Products. After merging the PC update, export the mobile view again, then Commit and Push. The public viewer keeps the same parent/subset navigation and read-only ownership.

Keep the application files directly in your existing `J_DogDex` folder. Keep
your `my_collection` folder there, the research evidence ZIP wherever you prefer,
and your collection backup in your usual backup location. You do not need an
Android app or a second editable collection.

## Update the PC application

1. Close the running DogDex console. Keep an exported collection backup.
2. Extract this package somewhere temporary. Copy the **contents** of its
   `DogDex` folder into your existing `J_DogDex`, replacing matching files, including supplied catalogue data.
3. Keep your existing **`my_collection`** folder. Do not replace or delete it.
4. Start `START_DOGDEX.bat` from `J_DogDex` as usual.

Personal copies, IDs, purchase costs, wishlist, catalog edits and pictures remain
in `my_collection`. Backups now include source covers too. Old version 1–3
backups can be restored in 1.8.4. New exports remain version 4. First start also
saves an automatic pre-upgrade backup for an existing collection.

## First public mobile website: GitHub Desktop

1. In DogDex open **Data health → Backup & Trash → Export mobile view**.
   DogDex generates `J_DogDex/docs` with the current collection snapshot, manual
   corrections, pictures and covers. Wait for the export success message.
2. In GitHub Desktop choose **File → Add local repository**, select your
   `J_DogDex` folder, and use **create a repository here** if it is not one yet.
   Keep the existing folder; avoid creating another nested `J_DogDex` folder.
   Do not choose a new gitignore template: the supplied `.gitignore` already
   limits commits to the mobile viewer and these instructions.
3. Review the changes. You should see `docs`, `.gitignore` and this guide.
   You should **not** see `runtime`, `my_collection`, research ZIPs or databases.
   Commit, then choose **Publish repository**, with **Keep this code private**
   unchecked. Use a new DogDex repository, not your existing PaxDex project.
4. On that repository's GitHub website go to **Settings → Pages**.
   Choose **Deploy from a branch → main → /docs → Save**.
5. After deployment, open the URL shown by GitHub on your phone. Bookmark it or
   use your browser's **Add to Home screen**. The PC does not need to stay on.

GitHub supports a `/docs` publishing source:
https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

## Everyday updates

Edit and collect on the PC as usual. When you want the phone to reflect those
changes: **Export mobile view → Commit in GitHub Desktop → Push origin**.
The phone shows the last exported date. It is a snapshot, not a live connection
to your PC. Changing the collection without another export/push does not update
the phone. There is no mobile editing or two-way synchronization to manage.

The export contains ownership counts, wishlist, catalog fields, images and
available guide prices. Purchase costs, copy notes, audit logs, SQLite files,
backups and editing tokens are not part of the viewer. The supplied `.gitignore`
keeps all other files local; this does not replace your ordinary backup.

## Sources, grouping and pictures

Sources are grouped by TCG series/era with generation labels. Dates on source
tiles now come from the same source field used to sort them. A card's later
distribution date no longer becomes the date of its expansion. Sources with
only year/month precision use an existing expansion sequence hint to break
ties; this does not create an exact German release date. Unqualified English
provider dates are not presented as confirmed German dates.

Open a source and click **Edit source / cover**, or use Data health → Sets &
sources → Edit. Change its series name, regional date, or optional order within
the series. An explicit order takes priority within that series. Upload an image
under **Source cover picture**. Removing it restores the card montage.

Upload → Save → check the picture in DogDex → delete the original download if
you wish. DogDex stores its own copy in `my_collection/catalog_images`. This
applies to source covers, shared card references and individual printing photos.
Export the mobile view again to publish picture changes.

## Cardmarket links and optional prices

Search fallbacks now include the printed card identity, expansion code/name and
collector number. English printed names distinguish forms such as Alolan Vulpix
from ordinary Vulpix. Existing direct links and manual corrections take priority.
A search is still labelled a search: it does not prove a matching product.

Cardmarket's public Pokémon guide is updated daily:
https://news.cardmarket.com/en/Magic/were-making-the-price-guide-and-product-catalogue-available-for-download

**Data health → Backup & Trash → Refresh Cardmarket guide** downloads and caches
the official guide. This uses no paid service or account key. The snapshot is
refreshed at most once per UTC day; a failure retains the previous cache.

A printing receives a price only after its product and price series have been
explicitly confirmed. Open the card, choose the printing and click **Find
Cardmarket product** (or **Change product** for an existing match). Saved source
references appear first. **Search catalogue** searches the official download;
enter a card name, ID or Cardmarket listing URL. No TCGGO lookup is needed.

Open a candidate's listing, select it and check the card, expansion, collector
number, language and physical printing. Tick the confirmation and **Confirm &
save**. DogDex saves the ID and series for that printing and loads its guide price.
The confirmation step has **Change selection** to return to the results. **Remove
price match** clears a link without changing ownership or purchase records.

The official product list does not supply every identifying field. Source hints
and name-only results remain unconfirmed until checked. A pretty URL without
`idProduct` can open the listing but cannot by itself reveal its numeric ID; the
finder searches the current card's saved references/name instead. Manual ID/URL
fields remain in the printing editor for products the search cannot distinguish.
The catalogue and guide caches stay local in `my_collection`. They are not part
of the mobile export. Linking and refreshing happen on the PC; the phone shows
the last exported confirmed matches and price snapshot.

An ordinary holo card does not automatically use the reverse-holo price series.
Stamps, first editions, deck versions, jumbo cards and championship replicas may
need distinct product matches; leave the mapping empty if it is ambiguous.

Matched details show the guide's EUR trend and 30-day average, with source date.
These are product-level references. The file has **no language or condition
breakdown**, so it cannot provide an exact German/English Near Mint value.
Purchase costs are unchanged. No collection-wide valuation or price history is
inferred. Export/push includes the current matched price snapshot on mobile.

## Research archives

The 1.7 research evidence ZIP remains the historical archive. Keep it. The new
1.8.4 evidence, reviewed printing specification and resumable claims queue are
under data/research/printing_184 inside J_DogDex. Read PRINTING_UPDATE_1_8_4.md
for the bounded EN/DE correction and research limits. No JA/KO factual records
or old IDs are changed. None of these private research files is exported to docs.
