# 3-minute walkthrough: Product Usage, Retention & Experiments

A timed script for a Loom recording of about 3 minutes (screen plus camera bubble, 1080p). Say it in your own words; the lines are a guide, not a teleprompter.

**Open these tabs before you press record:** README, dbt/models, results/experiments.md, docs/product_writeup.md, GitHub Actions.

| Time | On screen | What to say |
|---|---|---|
| 0:00–0:20 | Portfolio card, then the README title | Product teams argue about conversion because every dashboard defines it differently. Here, sessions, funnel, retention and stickiness are defined once in dbt over 2.76 million real events, with an A/B toolkit validated on 269,683 real visitors. |
| 0:20–0:45 | README intro and the Data section | It rebuilds the consumer product analytics from my analytics engineering role at a consumer-audio company, on RetailRocket's public data. No employer data is used. |
| 0:45–1:10 | The session and funnel models, with their unit tests | The 30-minute session rule and bot exclusion are unit-tested, and a test checks that every human event lands in exactly one session. |
| 1:10–1:35 | `results/experiments.md` | The toolkit covers sample size, sample-ratio checks, CUPED and guardrails. It recovers planted lifts within 0.3 points, with 93 to 97% interval coverage. |
| 1:35–2:00 | `docs/product_writeup.md` | Only 2.5% of viewing sessions add to cart. That's the step to move, and its tests need about 3 times fewer users. |
| 2:00–2:30 | A/A and broken-split results | A 2% loss of treatment units is caught with p = 2e-10. I also report what didn't work: CUPED does nothing for conversion here, because the pre-period correlation is 0.06. |
| 2:30–2:45 | `docs/design_doc.md`, the options table | The decision I'd defend in an interview: Validate the statistics on real traffic with planted effects before anyone trusts a test result. |
| 2:45–3:00 | Back to the README top | For a product team, that means one number per metric, and winners that are real. The repo, numbers and design doc are linked under the video. |

## Recording checklist
- Close email, chat and notifications. Zoom the browser to 125% so code is readable.
- Run `make fixture-all` once before recording, so CI-style output is fresh if you show it.
- Keep to one take per section; Loom lets you trim. Aim for 2:45 to 3:10.
- Show real numbers on screen as you say them; never estimate on camera.
- Say "synthetic" out loud wherever the README labels data as synthetic.

## After recording
1. Copy the Loom share link.
2. In `README.md`, replace the roadmap line with `- [x] [3-minute Loom walkthrough](<your Loom link>)` and add the link under the title.
3. Add the link to this project's card on saigwe.github.io.
