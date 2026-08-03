# client-safe-sweep

A Claude Code skill that sweeps any client-facing artifact **before you send it** — cover letters,
proposals, deliverable CSVs, overview docs, emails, video descriptions.

Built from real freelance engagements, including one where an early packaging pass leaked internal
pipeline column names straight into client CSVs. The skill is the catalogue of everything that was
caught, turned into a repeatable 8-check battery.

## The 8 checks

1. **Secrets & infrastructure** — keys, tokens, webhook/instance URLs, internal IDs
2. **Internal plumbing & methodology** — pipeline column names, internal paths, snake_case identifiers loose in prose
3. **AI-authorship markers** — model names, "Generated with…", `Co-Authored-By` (hard rule: removed)
4. **Absolute guarantees** — "guarantee", "100%", "never fails" → reframed to discipline/controls
5. **Experience overclaims** — flagged for your judgment, never auto-fixed
6. **Cross-client contamination** — other clients' names or data in this client's artifact
7. **De-jargon pass** — internal syntax translated to plain English
8. **Platform mechanics** — character limits, pre-contract contact-info rules

Mechanical hits get fixed on your go-ahead; judgment calls always come back to you as choices.
A clean sweep gets an explicit "clean" verdict, not silence.

## What's inside

- `skills/client-safe-sweep/SKILL.md` — the skill (check battery + procedure)
- `skills/client-safe-sweep/tools/secrets_sweep.py` — standalone scanner (stdlib-only Python):
  regex battery + CSV methodology-column check + URL-allowlist check, JSON report, exit-code verdict.
  Never prints secret values — pattern names and locations only.

## Install

```
/plugin marketplace add aihunt-ttg/client-safe-sweep
/plugin install client-safe-sweep@client-safe-sweep
```

Or run the scanner directly on any folder of client deliverables:

```
python tools/secrets_sweep.py path/to/deliverable/ --allow-host linkedin.com --domain-field "Company Domain"
```

## License

MIT — see [LICENSE](../../LICENSE). If it catches something embarrassing before your client sees it,
that was the point.
