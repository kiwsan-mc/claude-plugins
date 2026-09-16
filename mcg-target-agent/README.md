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
| `target-achievement` | Sales Planning Analyst | เป้า vs ยอดจริง + achievement% + 🟢🟡🔴 แยก channel/สาขา/cluster/เดือน |
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
| `sales_target_vs_actual_synapse` | เป้า/day, target & actual qty, actual sales, achievement% (กรอง year/month และช่วงวันที่ได้) |
| `sales_company_summary_synapse` | ยอดขาย invoice-level: net sales, qty, gross profit + GP%, moving cost, discount |
| `sales_query_synapse` | Raw T-SQL (SELECT/WITH) — fallback |
| `describe_table_sales_synapse` | Schema lookup |
| `search_columns_sales_synapse` | Column search |

## Data Sources

- `ai.dim_target_main_lines` — เป้าขายรายวัน **ระดับสาขา × วัน เท่านั้น** (ไม่มี category/channel/cluster)
- `ai.fact_daily_sales_account` — ยอดขายระดับ invoice (Company/Account) — ต้อง filter `Tax_Invoice_Date`

> อัปเดต: ย้ายจาก `gold.script_sales_target` / `silver.sap_zsdr006` มาเป็น schema `[ai]` แล้ว (ตารางเดิมยังอยู่แต่เลิกใช้)

## Usage

- "ทำเป้าได้กี่% แยก channel" → `target-achievement`
- "ยอดขายบัญชีลูกค้า + GP% เดือนนี้" → `company-account-sales`
