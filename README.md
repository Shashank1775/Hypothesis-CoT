# Hypothesis-First Prompting (HFP)

A prompting study asking whether making an LLM state a short **hypothesis / plan before it reasons** improves accuracy. HFP is compared against Standard, Chain-of-Thought (CoT), and Complex-CoT prompting on GPT-3.5-Turbo and GPT-4o, across six math word-problem benchmarks and two logical-reasoning benchmarks. An ablation then tests *when* and *how* the hypothesis is used.

Every run is logged per-question (`question`, `ground_truth`, `response`, `parsed_answer`, `is_correct`) so the tables below can be regenerated from the raw logs.

## Prompt variants

| Variant | Instruction |
|---|---|
| Standard | Answer directly |
| CoT | "Think step by step" |
| Complex-CoT | CoT with longer, harder few-shot exemplars |
| **HFP-\*** | Write a one-line `Hypothesis:` (a plan) first, then reason as in the base variant |

Ablation (gpt-4o, math benchmarks): **HFP-Full** (plan first, refer back to it), **HFP-Delayed** (reason first, write the plan afterwards), **HFP-NoReuse** (plan first, don't refer back), **HFP-Suppressed** (explicitly told not to plan). Few-shot exemplars for every variant are in `research/*/prompt_examples/`.

## Benchmarks

- Math: AddSub, ASDiv, AQuA, GSM8K, MultiArith, SVAMP — ~200 sampled problems each (`testingDatasets/*.json`, sampling in `datasets/analyzedDatasets.ipynb`)
- Logic: FOLIO, ProofWriter — 205 sampled problems each

## Results (accuracy %)

Regenerate with `python scripts/summarize_results.py --markdown`.

### Math benchmarks

**gpt-3.5-turbo**

| prompt | ADDSUB | AQUA | ASDIV | GSM | MULTIARTH | SVAMP | avg |
|---|---|---|---|---|---|---|---|
| Standard | 91.0 | 55.1 | 88.8 | 70.0 | 93.2 | 79.0 | 79.5 |
| CoT | 90.5 | 63.9 | 90.7 | 81.5 | 97.6 | 80.5 | 84.1 |
| Complex-CoT | 87.5 | 65.4 | 84.9 | 76.5 | 97.6 | 80.5 | 82.0 |
| HFP-Standard | 93.0 | 63.4 | 89.3 | 70.5 | 95.1 | 85.9 | 82.9 |
| HFP-CoT | 91.5 | 60.0 | 90.7 | 76.5 | 95.6 | 82.9 | 82.9 |
| HFP-Complex-CoT | 90.5 | 62.0 | 90.2 | 77.5 | 96.1 | 84.9 | 83.5 |

**gpt-4o**

| prompt | ADDSUB | AQUA | ASDIV | GSM | MULTIARTH | SVAMP | avg |
|---|---|---|---|---|---|---|---|
| Standard | 91.5 | 55.6 | 88.3 | 67.5 | 92.2 | 76.6 | 78.6 |
| CoT | 89.0 | 67.8 | 90.2 | 80.5 | 98.5 | 81.5 | 84.6 |
| Complex-CoT | 87.5 | 62.0 | 84.4 | 77.0 | 95.6 | 77.6 | 80.7 |
| HFP-Standard | 94.0 | 61.0 | 89.3 | 69.5 | 96.6 | 84.9 | 82.5 |
| HFP-CoT | 91.5 | 60.0 | 92.2 | 77.5 | 96.1 | 83.4 | 83.5 |
| HFP-Complex-CoT | 90.5 | 63.4 | 89.8 | 77.0 | 95.6 | 82.0 | 83.0 |

### Logical reasoning

**gpt-3.5-turbo**

| prompt | FOLIO | PROOFWRITER | avg |
|---|---|---|---|
| Standard | 55.6 | 36.6 | 46.1 |
| CoT | 55.1 | 44.9 | 50.0 |
| Complex-CoT | 56.6 | 48.3 | 52.4 |
| HFP-Standard | 52.2 | 45.4 | 48.8 |
| HFP-CoT | 57.6 | 46.8 | 52.2 |
| HFP-Complex-CoT | 56.1 | 49.3 | 52.7 |

**gpt-4o**

| prompt | FOLIO | PROOFWRITER | avg |
|---|---|---|---|
| Standard | 55.6 | 33.2 | 44.4 |
| CoT | 55.1 | 44.9 | 50.0 |
| Complex-CoT | 58.0 | 47.3 | 52.7 |
| HFP-Standard | 55.6 | 48.8 | 52.2 |
| HFP-CoT | 58.5 | 41.5 | 50.0 |
| HFP-Complex-CoT | 58.0 | 49.8 | 53.9 |

### Ablation (gpt-4o, math)

**gpt-4o**

| prompt | ADDSUB | AQUA | ASDIV | GSM | MULTIARTH | SVAMP | avg |
|---|---|---|---|---|---|---|---|
| HFP-Full | 98.0 | 85.4 | 95.1 | 93.0 | 99.5 | 92.7 | 93.9 |
| HFP-Delayed | 97.0 | 85.9 | 95.1 | 92.5 | 99.5 | 92.7 | 93.8 |
| HFP-NoReuse | 98.5 | 84.9 | 96.1 | 92.0 | 99.5 | 92.2 | 93.9 |
| HFP-Suppressed | 97.0 | 83.9 | 93.2 | 93.5 | 99.5 | 91.7 | 93.1 |



**Takeaways.** Planning first helps most where the base prompt is weakest: on GPT-3.5 HFP-Standard lifts the no-reasoning baseline from 79.5 → 82.9 average, and HFP variants win on AddSub and SVAMP for both models. Plain CoT remains best on GSM8K and AQuA. On logic benchmarks, HFP-Complex-CoT is the strongest setting for both models (52.7 / 53.9), mostly through ProofWriter gains. The ablation shows the *timing* of the hypothesis barely matters (Full ≈ Delayed ≈ NoReuse), while suppressing it costs ~1 point.

## Repository layout

```
research/hypTesting/     HFP vs. baselines on the six math sets (notebook + logs)
research/reasoning/      same comparison on FOLIO and ProofWriter
research/ablation/       HFP timing/reuse ablation on gpt-4o
research/FinalAnalysis.ipynb   plots
scripts/summarize_results.py   accuracy tables from the logs
testingDatasets/         sampled evaluation sets and few-shot prompt files
datasets/                source benchmarks (git submodules) + sampling notebook
outputs/                 early exploratory runs (CoCTtesting.ipynb)
```

## Reproducing

```bash
git clone --recurse-submodules <this repo>
pip install -r requirements.txt
cp .env.example .env     # Azure OpenAI endpoint + key
jupyter lab
```

The notebooks read `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` from the environment (`python-dotenv` or `export` them first) and expect `gpt-35-turbo` and `gpt-4o` deployments. Paths are relative to the notebook's folder.

## License

MIT — see [LICENSE](LICENSE).
