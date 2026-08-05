# Sweep verdict — `01-before-proposal.md`

**VERDICT: NEEDS-FIXES** — 13 mechanical hits, 3 judgment flags.

Checks 1, 2, 3, 6 and 8 are mechanical (`tools/secrets_sweep.py`, output in
`sweep-report.json`). Checks 4, 5 and 7 need eyes.

| # | Check | Hit | Location | Fix |
|---|---|---|---|---|
| 1 | Secrets & infrastructure | Webhook URL with an admin key in the query string | line 14 | **Remove the URL entirely.** A published endpoint is callable by anyone who reads the proposal. Rotate the key regardless of whether this went out. |
| 2 | Internal plumbing | `Apify`, `actor`, `n8n`, `railway` — four vendor/tool names the client never bought | line 13–14 | Cut all four. The client is buying a result, not a tool inventory. Naming vendors invites both price-shopping and "why can't I just run Apify myself". |
| 2 | Internal plumbing | `leads_master` table name | line 15 | Drop. Also worth checking: a shared table implies other clients' rows. |
| 3 | AI-authorship markers | "Generated with Claude." | line 30 | **Delete.** Hard rule, no judgment call. |
| 4 | Absolute guarantees | "I **guarantee** you'll never miss another enquiry" | line 20 | Reframe to a control: "Every enquiry is logged on arrival and routed to a named owner, with a daily check for anything unrouted." Describes the mechanism; one missed lead doesn't make it false. |
| 4 | Absolute guarantees | "the system **ensures 100%** of leads get a response within the hour" | line 21 | Same reframe. Two independent absolutes in one sentence — a client can read this as a warranty, and one counterexample falsifies it. |
| 5 | Experience overclaims | "With **years of experience** building lead systems **for agencies**" | line 20 | **FLAGGED, not fixed.** Only you know whether "agencies" is a plural you hold. Never auto-resolved. |
| 6 | Cross-client contamination | "I built the same thing for Harbourpoint Dental last quarter" | line 24 | Remove the name, or get written permission. Naming a client to another client is the fastest way to become the person who names *them* to the next one. |
| 7 | De-jargon | `seniority_founder_owner_ceo_md`, `non_agency_industry_token` | line 15 | Translate: "seniority" and "industry fit". Meaning unchanged, syntax humanised. |
| 8 | Platform mechanics | 1,180 chars — under any platform limit; no pre-contract contact details | — | Clean. |

## What the report does not contain

The scanner found the credential and **did not write it down**. The excerpt reads:

```
"context_excerpt": "https:<REDACTED:62chars>"
"url": "https://n8n-prod-4471.up.railway.app/webhook/intake?<REDACTED-QUERY>"
```

Host visible, so you know which vendor leaked. Query redacted, so the report isn't a
second copy of the key. A sweep report that contains the secret has just moved the
problem into a new file.

## Judgment calls stay yours

Check 5 is flagged and never auto-fixed — the tool cannot know which of your claims
are true. Check 4's rewrites are proposals, not edits. Nothing is sent; the sweep
hands back and stops.
