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

**Advisory by default, on purpose.** Measured against the 34-file corpus it still over-fires on two legitimate shapes, and both are pinned in `tests/` as known false positives so nobody loosens the lint to silence them:

- An evidence table of snapshot values, e.g. `| GREEN | 3,944,606 | ฿875.0M | ฿904.6M |`
- A bug-shape ratio the rule explicitly allows, e.g. `PO จะพอง ~42%`

Treat every hit as a question, not a verdict. It is also deliberately narrow: bare policy numbers in threshold rows (`≥80%=🟢`) are left alone, because a lint that fires on those gets switched off. It trades recall for precision, so a clean run is not proof the corpus is clean.

On Windows set `PYTHONIOENCODING=utf-8`; the skill files are Thai and a `cp874` console crashes on the first odd glyph.
