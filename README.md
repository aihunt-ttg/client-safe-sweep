# client-safe-sweep

**Free Claude Code skill: a pre-send safety sweep for anything a client will see.**

One leaked internal column name, one "Generated with…" footer, one accidental guarantee in a
proposal — that's all it takes to look amateur or lose a deal. This skill runs an 8-check battery
over cover letters, proposals, deliverable CSVs/docs, and emails before they leave your machine:

- secrets/keys/instance URLs
- internal pipeline & methodology leaks
- AI-authorship markers
- absolute guarantees
- experience overclaims (flagged, never auto-fixed)
- cross-client contamination
- internal jargon → plain English
- platform mechanics (character limits, pre-contract contact rules)

Ships with a standalone Python scanner (`tools/secrets_sweep.py`, stdlib only) so you can also
run it in CI or as a pre-send hook.

## Install

In Claude Code:

```
/plugin marketplace add aihunt-ttg/client-safe-sweep
/plugin install client-safe-sweep@client-safe-sweep
```

Then say "sweep this" before you send anything.

## Why free

This is the quality demonstrator for the Freelance Revenue Stack — a set of battle-tested Claude
Code skills for winning and delivering freelance work (job scanning, proof demos, call prep,
cold-call prep). If this free skill catches something for you, the paid stack is where the rest of
the pipeline lives.

## License

MIT. See LICENSE.
