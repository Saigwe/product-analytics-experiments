# If I owned this product: the one metric I'd move

**Add-to-cart rate per viewing session: 2.5% today.** It's the leakiest step in the funnel, it moves revenue directly, and it's the one this site can actually experiment on.

## What the data says (RetailRocket, 3 May – 18 Sep 2015, bots excluded)

| Funnel step (sessions) | Sessions | Step conversion |
|---|---|---|
| Viewed an item | 1,755,581 | |
| Added to cart | 43,919 | **2.5%** of viewing sessions |
| Purchased | 14,294 | 32.6% of cart sessions |
| End to end | | 0.81% of viewing sessions |

- **Most loss happens before the cart.** 97.5% of viewing sessions never add anything. Once something is in the cart, about a third of sessions buy, which is a reasonable cart-to-purchase rate. Fixing checkout would work on a third of a small number; fixing discovery and add-to-cart works on the big one.
- **Visitors rarely come back.** 87% of visitors have a single session. Day-1 retention averages 2.8%, day 7 0.6% and day 30 0.2%, and DAU/MAU is 3.9%. That makes each first session matter more, which points back to add-to-cart.
- **A few accounts buy a lot.** The heaviest viewer made 559 purchases. These look like business or reseller buyers, so they stay in, but they make visitor-level metrics heavy-tailed.

## Why this metric and not purchase conversion

Experiments decide whether a change worked, and on this traffic purchase conversion is too rare to test quickly:

| Metric (baseline) | Units per arm to detect +10% | At this site's traffic |
|---|---|---|
| Purchase per visitor (0.78%) | 209,585 visitors | about 6 weeks per test |
| Add-to-cart per viewing session (2.5%) | 64,199 sessions | about 1.5 weeks per test |

So add-to-cart experiments run about 3× faster, and purchase conversion stays as the **guardrail** (it must not fall). Two cautions:
- Randomise by visitor and analyse sessions with the delta method (sessions from one visitor aren't independent).
- Check that more carts lead to more purchases, rather than more abandoned carts.

## What I'd test first
1. **Item pages:** a clearer price and availability, and an "add to cart" button visible without scrolling. Measure add-to-cart rate, with purchases per visitor as the guardrail.
2. **Recommendations on item pages** for the 87% who leave after one session. Measure add-to-cart rate and day-7 return.
3. **A returning-visitor prompt** ("still interested in…") for the few who do come back, since they're the ones most likely to buy.

*Caveats: RetailRocket is anonymised (item ids only, no prices or page content), so the test ideas above are product judgement, not something the data shows directly. The traffic figures assume the same volume as May–Sep 2015.*
