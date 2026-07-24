# MCG Sales Agent

MC Group Data Analyst Agent plugin for Claude Code / Cowork.

ถามข้อมูลยอดขาย Retail/Fashion ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน MCP tools ที่เชื่อมต่อ MSSQL 2016.

## Skills

| Skill | Role | หน้าที่ |
|-------|------|---------|
| `sales-agent` | MC Group Sales Agent | กฎ สูตร KPI และ SQL rules หลัก (shared foundation) |
| `sales-dashboard` | Data Analyst | สรุปภาพรวม Sales Performance FY27 vs FY26 แยก Channel |
| `sales-sqm` | Retail Operations Expert | วิเคราะห์ Sales per Sqm. แยกสาขา/จังหวัด Top 5 / Bottom 5 |
| `discount-margin` | Financial & Planning Analyst | วิเคราะห์ Discount% vs Margin% แยก Category/Product |
| `member-analysis` | CRM & Sales Strategy Analyst | สัดส่วน Member vs Non-Member, ATV, UPT |
| `channel-regional` | Supply Chain & Retail Planner | สัดส่วนยอดขายแยก Regional x Channel + Stock Allocation |
| `abc-analysis` | Inventory & Merchandising Analyst | ABC Analysis + Hero/Slow-moving Articles |

## Architecture

```
skills/
├── sales-agent/         ← SKILL.md หลัก (rules, SQL, KPIs, thresholds)
├── sales-dashboard/     ← #[[file:../sales-agent/SKILL.md]] + role prompt
├── sales-sqm/           ← #[[file:../sales-agent/SKILL.md]] + role prompt
├── discount-margin/     ← #[[file:../sales-agent/SKILL.md]] + role prompt
├── member-analysis/     ← #[[file:../sales-agent/SKILL.md]] + role prompt
├── channel-regional/    ← #[[file:../sales-agent/SKILL.md]] + role prompt
└── abc-analysis/        ← #[[file:../sales-agent/SKILL.md]] + role prompt
```

แต่ละ skill ย่อย include กฎหลักผ่าน `#[[file:...]]` — ไม่ซ้ำซ้อน แก้ที่เดียวมีผลทุก role.

## MCP Tools

| Tool | Description |
|------|-------------|
| `execute_sql` | Execute T-SQL SELECT queries |
| `describe_table` | Get table schema |
| `list_tables` | List approved tables |

## Usage

พิมพ์คำถามตรงๆ:
- "สรุปภาพรวมยอดขาย" → triggers `sales-dashboard`
- "Sales per sqm สาขาไหนดีสุด" → triggers `sales-sqm`
- "Category ไหน discount สูงเกินไป" → triggers `discount-margin`
- "สัดส่วน Member เป็นเท่าไหร่" → triggers `member-analysis`
- "ยอดขายแยกตามภาค" → triggers `channel-regional`
- "สินค้าขายดี/สต็อกจม" → triggers `abc-analysis`
