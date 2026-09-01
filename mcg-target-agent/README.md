# MCG Target Agent

MC Group Sales Target Analyst Agent plugin for Claude Code / Cowork.

ถามข้อมูลเป้าขาย vs ยอดจริง (% achievement) และยอดขายระดับ invoice (Company/Account) ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน Synapse MCP tools.

## Version

**v1.0.0** — Synapse target & company-sales domain (T-SQL, canned tools + raw query fallback)

> หมายเหตุ: ยอดขายระดับ invoice (นี่) ต่างจากยอดขาย POS รายวันของ `mcg-sales-agent` — KPI ค้าปลีก (ATV/UPT/member) อยู่ที่ sales agent

## Skills

| Skill | Role | หน้าที่ |
|-------|------|---------|
| `target-agent` | Sales Target Agent | กฎกลาง, tool priority, FY, achievement/GP thresholds (shared foundation) |
| `target-achievement` | Sales Planning Analyst | เป้า vs ยอดจริง + achievement% + 🟢🟡🔴 แยก channel/สาขา/category |
| `company-account-sales` | Account Sales Analyst | ยอดขาย invoice-level + GP% + discount แยก account/channel/region/brand |

## Architecture

```
skills/
├── target-agent/           ← SKILL.md หลัก (rules, tool priority, FY, thresholds)
├── target-achievement/     ← #[[file:../target-agent/SKILL.md]] + role prompt
└── company-account-sales/  ← #[[file:../target-agent/SKILL.md]] + role prompt
```

## MCP Tools (Synapse — server: `synapse-target`)

| Tool | Description |
|------|-------------|
| `sales_target_vs_actual_synapse` | เป้า/day, เป้า/category, target & actual qty, actual sales, achievement% |
| `sales_company_summary_synapse` | ยอดขาย invoice-level: net sales, qty, gross profit + GP%, moving cost, discount |
| `sales_query_synapse` | Raw T-SQL (SELECT/WITH) — fallback |
| `describe_table_sales_synapse` | Schema lookup |
| `search_columns_sales_synapse` | Column search |

## Data Sources

- `gold.script_sales_target` — เป้าขายรายวัน/เดือน
- `silver.sap_zsdr006` — ยอดขายระดับ invoice (Company/Account) — ต้อง filter invoice date

## Usage

- "ทำเป้าได้กี่% แยก channel" → `target-achievement`
- "ยอดขายบัญชีลูกค้า + GP% เดือนนี้" → `company-account-sales`
