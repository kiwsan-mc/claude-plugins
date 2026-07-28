# MCG Sales Agent

MC Group Data Analyst Agent plugin for Claude Code / Cowork.

ถามข้อมูลยอดขาย Retail/Fashion ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน MCP tools ที่เชื่อมต่อ PostgreSQL (pgvector).

## Version

**v3.0.0** — Migrated from MSSQL to PostgreSQL (pgvector-enabled)

### Changelog
- **v3.0.0**: Migrated to PostgreSQL + pgvector. New tools: `pg_execute_sql`, `pg_describe_table`, `pg_list_tables`. SQL syntax updated to PostgreSQL. Added `FY_Year` column support. SQM threshold ≥50.
- **v2.2.5**: MSSQL version (deprecated)

## Skills

| Skill | Role | หน้าที่ |
|-------|------|---------|
| `sales-agent` | MC Group Sales Agent | กฎ สูตร KPI และ SQL rules หลัก (shared foundation) |
| `sales-dashboard` | Data Analyst | สรุปภาพรวม Sales Performance FY28 vs FY27 แยก Channel |
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

## MCP Tools (PostgreSQL)

| Tool | Description |
|------|-------------|
| `pg_execute_sql` | Execute PostgreSQL SELECT queries |
| `pg_describe_table` | Get table schema |
| `pg_list_tables` | List approved tables |

## Database

- **Engine**: PostgreSQL 16 (Azure Flexible Server)
- **Table**: `mcg_aiplatform_sales` (~13M rows, 20GB)
- **Features**: pgvector extension enabled
- **Connection**: Via MCP Toolbox v1.8.0

## Usage

พิมพ์คำถามตรงๆ:
- "สรุปภาพรวมยอดขาย" → triggers `sales-dashboard`
- "Sales per sqm สาขาไหนดีสุด" → triggers `sales-sqm`
- "Category ไหน discount สูงเกินไป" → triggers `discount-margin`
- "สัดส่วน Member เป็นเท่าไหร่" → triggers `member-analysis`
- "ยอดขายแยกตามภาค" → triggers `channel-regional`
- "สินค้าขายดี/สต็อกจม" → triggers `abc-analysis`
