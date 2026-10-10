# tools

Repo-level checks that apply across the `mcg-*` plugins.

## check-pinned-values.py

Flags a live business figure standing in skill rule text. The standing rule allows a figure in three shapes only: inside a dated evidence block that also carries a guard, an unmistakably synthetic formatting example, or a ratio describing the shape of a bug. Anything else is a stale data source the model will quote as the answer.

The rule was already written down in prose and still accumulated 18 violations across four files, found and fixed on 2026-10-05. That is why it is a lint.

```bash
python tools/check-pinned-values.py            # advisory, exit 0
python tools/check-pinned-values.py --strict   # exit 1 on any hit
python -m unittest discover -s tools/tests -v  # 15 cases
```

**Advisory by default, on purpose.** Measured against the corpus on 2026-10-05 it still over-fires on two legitimate shapes, and both are pinned in `tests/` as known false positives so nobody loosens the lint to silence them:

- An evidence table of snapshot values whose caption carries no date or no guard
- A bug-shape ratio the rule explicitly allows, e.g. `PO จะพอง ~42%`

Treat every hit as a question, not a verdict. It is also deliberately narrow: bare policy numbers in threshold rows (`≥80%=🟢`) are left alone, because a lint that fires on those gets switched off. It trades recall for precision, so a clean run is not proof the corpus is clean.

**What it cannot see.** The four patterns match baht amounts, approximate shares, decimal shares and `~N` scale claims. They do **not** match a bare count, so a live figure like `1,070 สาขา`, `643 สาขา` or `18,935 SKU` in a rule sentence passes unflagged. Counts of branches, stores and SKUs drift exactly like shares do, so a clean run still needs a manual read for them. Measured 2026-10-05: a sweep that reported 3 remaining hits still had live counts of that shape in the same files.

**The lint is block-aware, not line-aware.** The rule allows a figure inside a block whose caption carries a date *and* a guard, so a caption covers every line under it until the next heading. A caption counts when it carries both, and a date counts in ISO (`2026-09-28`) or Thai form (`1-20 ก.ย. 2026`). A table of snapshot values under a dated caption therefore passes, while the same numbers loose in a rule sentence do not.

On Windows set `PYTHONIOENCODING=utf-8`; the skill files are Thai and a `cp874` console crashes on the first odd glyph.

## run-trigger-evals.py

Checks every `*/skills/*/evals/trigger_eval.json` in two passes, because they fail for different reasons and only one of them needs a model.

**Static**, always, no network. Schema, duplicate queries, a query that appears on both sides of the line — which makes a case impossible to satisfy — a skill with no description for anything to decide on, a positive or negative set too thin to prove much, and evals whose skill no longer exists, which is what a rename leaves behind.

**Trigger**, opt-in, needs a model. Gives a skill's own description and one query to an OpenAI-compatible endpoint and asks whether the skill would be invoked. It reads only the answer field: a reasoning model that spends its budget thinking returns an empty one, and its reasoning discusses the question rather than answering it.

    python tools/run-trigger-evals.py                              # static only
    python tools/run-trigger-evals.py --model gpt-4o-mini         --base-url https://api.openai.com/v1 --api-key $KEY       # static + trigger
    python tools/run-trigger-evals.py --model qwen2.5-coder:32b --strict

**This is a proxy, and the output says so.** The deployment decides with its own model, and no local endpoint reproduces that judgement. A clean run means the description discriminates on the model you pointed it at — worth knowing, and not the same as knowing how the deployment behaves. Read a disagreement as a question about the description, not as a defect in the case.

Exit is 0 unless `--strict` is given, matching `check-pinned-values.py`.
