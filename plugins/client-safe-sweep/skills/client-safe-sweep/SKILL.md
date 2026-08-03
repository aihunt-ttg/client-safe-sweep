---
name: client-safe-sweep
description: Pre-send safety sweep for ANY client-facing artifact (cover letter, proposal, quote message, deliverable CSV/doc, overview, email, video description) — catches secrets/keys/instance URLs, internal plumbing and methodology leaks, AI-authorship markers, absolute guarantees, experience overclaims, cross-client contamination, and internal jargon; proposes fixes and re-sweeps. Invoke when the user runs /client-safe-sweep, says "sweep this", "is this safe to send", "client-safe check", or before any send gate in other skills.
---

# client-safe-sweep — pre-send safety check for client-facing artifacts

Every artifact that leaves the building gets swept first. The check battery below was built from real
client engagements — including one where an early packaging pass leaked pipeline column names and
rubric identifiers straight into client CSVs. It is a **checklist, not a rewrite tool**: mechanical
hits get fixed on request, judgment calls always go back to the user.

## Scope

Applies to anything a client, lead, or their organization will see: cover letters, proposals, quote
messages, deliverable CSVs/docs, overview PDFs/MDs, client emails, demo video descriptions/captions.
Does NOT apply to internal-only files (state files, session logs, private notes) — sweeping those
wastes a pass. Unsure whether something is client-visible? Ask the user, don't skip it.

## Check battery

| # | Check | Look for (concrete patterns) | Action |
|---|---|---|---|
| 1 | Secrets & infrastructure | `sk-`/key/token/secret/bearer + values; webhook/instance URLs (hosted automation domains, `admin?key=`); base/table/workflow IDs | Remove. Never paraphrase a secret into the text — cite pattern name + location only. |
| 2 | Internal plumbing & methodology | Pipeline column names (internal scorer/model names, dedupe/routing slugs); vendor/actor/tool names the client wasn't sold on; internal absolute paths (`C:\Users`, `work/`, `scripts/`); prompt/rubric variable names (snake_case identifiers loose in prose) | Drop the column, redact the path, reword the identifier |
| 3 | AI-authorship markers | AI model/vendor names, "AI-generated", "Generated with", model names, `Co-Authored-By` | Remove — hard rule, no exceptions |
| 4 | Absolute guarantees | guarantee, 100%, always, never fails, ensures, zero risk, "completely safe" | Reframe to discipline/controls ("we monitor X, alert on Y"), never outcomes |
| 5 | Experience overclaims | Language implying professional experience/credentials the user lacks | FLAG for the user's judgment — never auto-fix |
| 6 | Cross-client contamination | Other clients' names, another job's data/IDs, a reused artifact with stale branding | Remove; re-verify the artifact is this-client-only |
| 7 | De-jargon pass | Internal syntax loose in prose — e.g. `seniority_founder_owner_ceo_md` → "Founder-level title", `non_agency_industry_token` → "non-agency industry signal", "scraper/session artifact" → "public-data caching artifact" | Translate to plain English — meaning unchanged, syntax humanized |
| 8 | Platform mechanics (message/cover-letter artifacts only) | Character count; pre-contract contact-info restrictions | Trim under the platform limit; strip disallowed contact info pre-contract |

**Check 4 litmus** (the no-absolute-guarantees rule): could a client read this as a warranty — could
ONE counterexample falsify it? Yes to either → reframe.
**Check 4 false positive:** a lead's/client's own quoted copy may legitimately contain
"ensures"/"model" (a testimonial, a tagline quoted as evidence) — flag only **our** claims, never
text quoted verbatim from someone else.
**Check 2 example** (real catch, anonymized): internal pipeline columns and an opaque dedupe/routing
slug were dropped from every client CSV; the `Evidence` column was kept but sanitized to a
plain-English field whitelist rather than cut outright — sanitize real evidence, don't reflexively
drop the whole column.
**Check 8 note:** freelance platforms like Upwork block off-platform contact details (email, phone,
external scheduling links) before a contract exists — flag wording that routes around that, not just
the char count.
**Checks 2 & 3 follow the deliverable-rules discipline. Check 5 follows the accurate-experience-claims
rule** — never resolve an overclaim yourself.

## Procedure

1. **Identify the artifact(s)** — file path(s) or pasted text. A multi-file delivery (CSVs +
   overview.md) sweeps together as one pass.
2. **Run the battery, mechanical checks first** (1, 2, 3, 6, 8) — grep/regex pass. Start from the
   bundled `tools/secrets_sweep.py`: its `PATTERNS` dict + CSV header-column check + URL-allowlist
   check is the template; adapt to the artifact at hand, don't reinvent it. Then a read-through for
   the judgment checks (4, 5, 7) — these need eyes, not just regex.
3. **Report the verdict** as a table, every hit with location + proposed fix:

   | Check | Hit | Location | Proposed fix |
   |---|---|---|---|
   | 3 | "Generated with Claude Code" | overview.md:42 | Delete the line |

   A clean sweep still gets an explicit "clean" verdict, not silence.
4. **Apply mechanical fixes only on the user's go-ahead** (checks 1, 2, 3, 6, 7, 8), then re-sweep.
   Reusable pattern for column-drop + token-reword: drop flagged columns, remap internal tokens to
   plain English longest-first, verify zero leftover snake_case after.
5. **Judgment items always go to the user as choices** — guarantee phrasing (4) and overclaim flags
   (5) are never auto-fixed. **The assistant never sends anything.** Sweep, fix, hand back.

## When other skills call this

Any skill about to surface something client-visible (a proposal submit gate, a quote staging step)
should hand the artifact to this sweep first, fold the verdict into its own report, and only then
apply its own send-gate language — instead of reinventing a checklist.

## Keep this sharp (self-annealing)

New leak pattern caught on a real engagement → append one line to the check battery table above
(which check it belongs under, the concrete pattern, the fix). Keep this file under ~130 lines — a
category that outgrows one table row is a signal to split into a `references/` file, not to write
paragraphs here.
