#!/usr/bin/env python3
"""Secrets + compliance sweep for client-facing artifacts.

Scans .md/.txt/.csv/.html files under a target directory for:
  - secrets & credentials
  - AI-authorship markers
  - absolute-guarantee language
  - internal paths / vendor plumbing leaks
  - internal methodology columns in CSV headers
  - non-allowlisted URLs

Secret VALUES are redacted before anything is printed or written — the report carries
pattern names, locations, and a redacted excerpt (`<REDACTED:Nchars>` in place of the
match) so you can find the hit without the report itself becoming a second leak.
Re-runnable; writes a JSON report and exits non-zero when genuine hits remain.

Usage:
  python secrets_sweep.py TARGET_DIR [--out sweep-report.json]
      [--allow-host linkedin.com --allow-host example.com ...]
      [--domain-field "Company Domain"] [--fp false-positives.json]

false-positives.json (optional): a list of hand-verified exceptions, e.g.
  [{"file": "leads.csv", "matched_text": "Slack", "reason": "lead's own client, quoted as evidence"}]
A hit is classified false_positive when its matched_text appears in the hit's context excerpt.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

TEXT_EXTS = {".md", ".txt", ".html", ".htm", ".json", ".xml", ".yml", ".yaml"}

INTERNAL_METHOD_COLUMNS = {
    "source track", "prompt version", "model", "scorer", "llm model",
    "model name", "temperature", "system prompt", "prompt id",
}

PATTERNS = {
    "secrets_credentials": re.compile(
        r"(?i)\b(token|api[_-]?key|secret|bearer|password|credential)\b|sk-[a-zA-Z0-9_-]{3,}"
    ),
    "ai_authorship_markers": re.compile(
        r"(?i)(claude|anthropic|openai|gpt-4|gpt-3\.5|gpt-3|chatgpt|AI-generated|Generated with|"
        r"AI generated|written by AI|large language model|\bllm\b)"
    ),
    "absolute_guarantees": re.compile(
        r"(?i)(guarantee|100%|\balways\b|never fails|\bensures?\b|risk-free|zero risk)"
    ),
    "internal_paths_and_vendor_plumbing": re.compile(
        r"(?i)(C:\\Users|C:/Users|n8n|railway|apify|\bactor\b|airtable|\.env|"
        r"ANTHROPIC_API_KEY|APIFY_TOKEN|webhook|railway\.app|ngrok|onrender|herokuapp|"
        r"instance[_ ]?url|channel[_ ]?id|chat[_ ]?id|scraperapi|brightdata|"
        r"oxylabs|dataimpulse|zenrows|proxycurl|phantombuster)"
    ),
}


def norm_domain(d: str) -> str:
    if not d:
        return ""
    d = d.strip().lower()
    d = re.sub(r"^https?://", "", d)
    d = re.sub(r"^www\.", "", d)
    return d.rstrip("/").split("/")[0]


def make_host_allowed(allowed_hosts, own_domain_getter):
    allowed = {norm_domain(h) for h in allowed_hosts}

    def host_allowed(host: str, own_domain_norm: str) -> bool:
        host = host.lower()
        if host.startswith("www."):
            host = host[4:]
        for a in allowed:
            if a and (host == a or host.endswith("." + a)):
                return True
        if own_domain_norm and (host == own_domain_norm or host.endswith("." + own_domain_norm)):
            return True
        return False

    return host_allowed


def find_urls(text: str):
    return re.findall(r"https?://[^\s\"',)>\]]+", text)


_MASK = lambda s: f"<REDACTED:{len(s)}chars>"
# Value sitting after an `=` or `:` — e.g. api_key = sk-live...
_ASSIGNED_VALUE = re.compile(r"([=:]\s*)(['\"]?)([^\s'\",;]{6,})(\2)")
# Any long unbroken credential-shaped run.
_TOKEN_LIKE = re.compile(r"[A-Za-z0-9_\-]{12,}")


def redact(text: str, pat, cat: str) -> str:
    """Strip secret material out of an excerpt before it is stored or printed.

    Two passes, because one is not enough. The `secrets_credentials` pattern matches
    the LABEL ("api_key", "Bearer", "password"), not the value — so replacing only the
    match removes the word and leaves the actual credential sitting in the surrounding
    excerpt. For that category we additionally mask assigned values and any long
    token-shaped run.

    The aggressive pass is scoped to secrets only: masking every 12-char word would
    make the guarantee/authorship/plumbing excerpts unreadable for no safety gain.

    Value-masking runs BEFORE the keyword pass, not after: the placeholder contains a
    colon, so an assigned-value pass running second would match its own output and
    produce nested `<REDACTED:<REDACTED:...` garbage.
    """
    out = text
    if cat == "secrets_credentials":
        out = _ASSIGNED_VALUE.sub(
            lambda m: f"{m.group(1)}{m.group(2)}{_MASK(m.group(3))}{m.group(4)}", out
        )
        out = _TOKEN_LIKE.sub(lambda m: _MASK(m.group(0)), out)
    return pat.sub(lambda m: _MASK(m.group(0)), out)


def sweep_text_patterns(filename, text, results):
    lines = text.splitlines()
    for cat, pat in PATTERNS.items():
        for i, line in enumerate(lines, start=1):
            for m in pat.finditer(line):
                results[cat]["hits"].append({
                    "file": filename,
                    "line": i,
                    "matched_pattern": cat,
                    "context_excerpt": redact(line.strip(), pat, cat)[:160],
                })


def sweep_csv(filename, path, results, url_report, host_allowed, domain_field):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        header_lower = {h.strip().lower(): h for h in header}
        for bad_col in INTERNAL_METHOD_COLUMNS:
            if bad_col in header_lower:
                results["internal_methodology_csv_columns"]["hits"].append({
                    "file": filename,
                    "column": header_lower[bad_col],
                })
        rows = list(reader)
        url_report["files_checked_for_urls"][filename] = f"{len(rows)} data rows"
        for row_idx, row in enumerate(rows, start=2):  # +1 header, +1 1-index
            own_domain = norm_domain(row.get(domain_field, "") or "") if domain_field else ""
            row_text = " | ".join(f"{k}={v}" for k, v in row.items() if v)
            for cat, pat in PATTERNS.items():
                for m in pat.finditer(row_text):
                    window = row_text[max(0, m.start() - 40):m.end() + 40]
                    results[cat]["hits"].append({
                        "file": filename,
                        "row": row_idx,
                        "matched_pattern": cat,
                        "context_excerpt": redact(window, pat, cat)[:160],
                    })
            for field, val in row.items():
                if not val:
                    continue
                for url in find_urls(val):
                    url_report["total_urls_found"] += 1
                    host = urlparse(url).netloc
                    if not host_allowed(host, own_domain):
                        url_report["flagged_non_allowlisted"].append({
                            "file": filename, "row": row_idx, "field": field,
                            "url": url, "own_company_domain": own_domain,
                        })


def main():
    ap = argparse.ArgumentParser(description="Secrets + compliance sweep for client-facing artifacts.")
    ap.add_argument("target_dir", help="Directory to sweep (recursed).")
    ap.add_argument("--out", default=None, help="Report path (default: <target_dir>/sweep-report.json).")
    ap.add_argument("--allow-host", action="append", default=[],
                    help="Allowed URL host (repeatable). Subdomains match automatically.")
    ap.add_argument("--domain-field", default=None,
                    help="CSV column holding the row's own domain; those URLs are allowed too.")
    ap.add_argument("--fp", default=None, help="Optional false-positives JSON file.")
    args = ap.parse_args()

    target = Path(args.target_dir)
    if not target.is_dir():
        sys.exit(f"not a directory: {target}")
    out_path = Path(args.out) if args.out else target / "sweep-report.json"
    false_positives = json.loads(Path(args.fp).read_text(encoding="utf-8")) if args.fp else []
    host_allowed = make_host_allowed(args.allow_host, None)

    results = {cat: {"hits": []} for cat in PATTERNS}
    results["internal_methodology_csv_columns"] = {"hits": []}
    url_report = {"total_urls_found": 0, "flagged_non_allowlisted": [], "files_checked_for_urls": {}}

    for p in sorted(target.rglob("*")):
        if not p.is_file():
            continue
        if out_path.exists() and p.samefile(out_path):
            continue
        rel = str(p.relative_to(target))
        if p.suffix.lower() == ".csv":
            sweep_csv(rel, p, results, url_report, host_allowed, args.domain_field)
        elif p.suffix.lower() in TEXT_EXTS:
            text = p.read_text(encoding="utf-8-sig", errors="replace")
            sweep_text_patterns(rel, text, results)
            url_report["files_checked_for_urls"][rel] = f"{len(find_urls(text))} URLs present"
            for url in find_urls(text):
                url_report["total_urls_found"] += 1
                if not host_allowed(urlparse(url).netloc, ""):
                    url_report["flagged_non_allowlisted"].append({
                        "file": rel, "row": None, "field": None, "url": url,
                    })

    def is_known_false_positive(hit):
        for fp in false_positives:
            if (hit.get("file") == fp.get("file")
                    and fp.get("matched_text", "").lower() in hit.get("context_excerpt", "").lower()):
                return fp
        return None

    for cat, r in results.items():
        for hit in r["hits"]:
            fp = is_known_false_positive(hit)
            hit["classification"] = "false_positive" if fp else "unclassified_hit"
            if fp:
                hit["false_positive_reason"] = fp.get("reason", "")

    def genuine_count(hits):
        return sum(1 for h in hits if h.get("classification") != "false_positive")

    total_raw = sum(len(v["hits"]) for v in results.values()) + len(url_report["flagged_non_allowlisted"])
    total_genuine = sum(genuine_count(v["hits"]) for v in results.values()) + len(url_report["flagged_non_allowlisted"])

    out = {
        "stage": "secrets_and_compliance_sweep",
        "scope": {"directory": str(target)},
        "patterns_run": [
            {
                "category": cat,
                "pattern": PATTERNS[cat].pattern if cat in PATTERNS else "CSV header column check",
                "raw_hits": len(r["hits"]),
                "genuine_hits": genuine_count(r["hits"]),
                "hit_detail": r["hits"],
            }
            for cat, r in results.items()
        ] + [{
            "category": "non_allowlisted_urls",
            "total_urls_found": url_report["total_urls_found"],
            "flagged_non_allowlisted": len(url_report["flagged_non_allowlisted"]),
            "hit_detail": url_report["flagged_non_allowlisted"],
            "files_checked_for_urls": url_report["files_checked_for_urls"],
        }],
        "total_raw_hits": total_raw,
        "total_genuine_hits": total_genuine,
        "verdict": "ok" if total_genuine == 0 else "fail",
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"total_raw_hits": total_raw, "total_genuine_hits": total_genuine,
                      "verdict": out["verdict"], "report": str(out_path)}, indent=2))
    sys.exit(0 if total_genuine == 0 else 1)


if __name__ == "__main__":
    main()
