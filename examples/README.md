# Worked example — one proposal, swept

A real run of `client-safe-sweep` on a synthetic proposal. Every name, key and URL
here is invented; the scan output is genuine.

| File | What it is |
|---|---|
| `01-before-proposal.md` | The draft as written. Reads fine. Isn't. |
| `sweep-report.json` | **Actual output** of `tools/secrets_sweep.py` — the mechanical pass |
| `02-sweep-verdict.md` | The full verdict, mechanical + judgment checks |
| `03-after-proposal.md` | The same proposal, cleared to send |

Reproduce it yourself:

```bash
python plugins/client-safe-sweep/skills/client-safe-sweep/tools/secrets_sweep.py examples --out /tmp/report.json
echo $?   # 1 — genuine hits remain
```

Note what the report does **not** contain: the credential. Excerpts are redacted to
`<REDACTED:Nchars>` and URL query strings to `?<REDACTED-QUERY>`, so the report never
becomes a second copy of the thing you were checking for.
