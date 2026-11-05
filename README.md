# equitygroupjax.com

Static site for American Equity Group (cash buyers), hosted on GitHub Pages from `/docs`. Same setup as `jaxcashbuyers-site`.

- `build.py` — every page (copy, SEO titles/meta, schema, layout) and builds into `docs/`, with sitemap.xml and robots.txt
- `content/deals.json` — the deals. Add, edit, or change `status` (Available / Under Offer / Sold) and rebuild
- `img/` — images

Rebuild: `python3 build.py`

## Rules the build enforces
- Only phone number: (904) 685-8024
- Deals can never carry seller name/phone, contract price, mortgage or EMD (the build fails if they do)
- "Buyer to verify" footer on every page

## Going live (DNS switch)
1. Save photos from the old equitygroupjax.com first.
2. In `build.py` set `BASE = ""` and `LIVE = True` (adds CNAME, allows indexing), rebuild, push.
3. Namecheap DNS: A records for `@` → 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153; CNAME `www` → `equitygroup904-dev.github.io`.
4. Repo Settings → Pages → custom domain `equitygroupjax.com`, Enforce HTTPS.

## Still open
- GHL "Cash Buyer Sign-Up" form (Jacksonville Cash Home Buyers sub-account only): paste its ID into `BUYER_FORM_ID`.
