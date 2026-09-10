"""Summarise accuracy from the JSON run logs under research/*/logs.

Each log is a list of {question, ground_truth, response, parsed_answer, is_correct}
and is named <model>_<prompt>_<dataset>_<timestamp>.json (ablation logs omit the
model prefix and were run on gpt-4o). If a (model, prompt, dataset) cell
was run more than once the most recent log wins.

Usage:  python scripts/summarize_results.py [--markdown]
"""
import argparse
import glob
import json
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIRS = {
    "hypTesting": os.path.join(ROOT, "research", "hypTesting", "logs"),
    "reasoning": os.path.join(ROOT, "research", "reasoning", "logs"),
    "ablation": os.path.join(ROOT, "research", "ablation", "logs"),
}
NAME_RE = re.compile(r"^(?:(?P<model>gpt-[\w.-]+?)_)?(?P<prompt>[\w-]+)_(?P<dataset>[A-Za-z]+)_(?P<ts>\d{8}_\d{6})\.json$")
PROMPT_ORDER = ["Standard", "CoT", "Complex-CoT", "HFP-Standard", "HFP-CoT", "HFP-Complex-CoT",
                "HFP-Full", "HFP-Delayed", "HFP-NoReuse", "HFP-Suppressed"]


def load(section):
    cells = {}
    for path in glob.glob(os.path.join(LOG_DIRS[section], "*.json")):
        m = NAME_RE.match(os.path.basename(path))
        if not m:
            continue
        key = (m["model"] or "gpt-4o", m["prompt"], m["dataset"].upper())
        if key in cells and cells[key][0] > m["ts"]:
            continue
        with open(path) as f:
            rows = json.load(f)
        correct = sum(1 for r in rows if r.get("is_correct"))
        cells[key] = (m["ts"], correct, len(rows))
    return cells


def table(cells, markdown):
    models = sorted({k[0] for k in cells})
    datasets = sorted({k[2] for k in cells})
    prompts = [p for p in PROMPT_ORDER if any(k[1] == p for k in cells)]
    prompts += sorted({k[1] for k in cells} - set(prompts))
    out = []
    for model in models:
        out.append(f"\n{model}")
        header = ["prompt"] + datasets + ["avg"]
        rows = []
        for p in prompts:
            accs = []
            row = [p]
            for d in datasets:
                c = cells.get((model, p, d))
                if c:
                    acc = 100 * c[1] / c[2]
                    accs.append(acc)
                    row.append(f"{acc:.1f}")
                else:
                    row.append("–")
            row.append(f"{sum(accs)/len(accs):.1f}" if accs else "–")
            rows.append(row)
        if markdown:
            out.append("| " + " | ".join(header) + " |")
            out.append("|" + "---|" * len(header))
            out += ["| " + " | ".join(r) + " |" for r in rows]
        else:
            w = [max(len(x) for x in col) for col in zip(header, *rows)]
            out.append("  ".join(h.ljust(n) for h, n in zip(header, w)))
            out += ["  ".join(x.ljust(n) for x, n in zip(r, w)) for r in rows]
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--markdown", action="store_true")
    args = ap.parse_args()
    for section in LOG_DIRS:
        cells = load(section)
        if cells:
            print(f"\n## {section}")
            print(table(cells, args.markdown))
