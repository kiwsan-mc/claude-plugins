# MCG Sales Agent

MC Group Data Analyst Agent plugin for Claude Code / Cowork.

ถามข้อมูลยอดขาย Retail/Fashion ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน MCP tools ที่เชื่อมต่อ PostgreSQL (pgvector).

> 📌 **ศัพท์ MCG:** ยอดขาย = **"Sales Out"** (plugin นี้) · การสั่งซื้อเข้า/PO = **"Sales In"** → ใช้ `mcg-inventory-agent` (po-intake)

## Version

**v5.19.2** — ย้ำกฎห้ามเดาข้อมูลมาตอบทุก skill
- **v5.19.2**: ย้ำกฎ **ห้ามเดาข้อมูลมาตอบ** (ใช้กับทุก runtime โดยเฉพาะ Claude Desktop / Cowork) ใน **ทุก skill** ของปลั๊กอิน — ทุกตัวเลข/ข้อเท็จจริงต้องมาจากผลการเรียก tool จริงในบทสนทนาและอ้างอิงกลับได้ · เรียกแล้วไม่พบข้อมูลให้ตอบว่า "ไม่พบข้อมูล" ตามจริง (แยกจาก 0) · ห้ามเดา/ประมาณ/แต่งตัวเลข/ตอบจากความจำของโมเดล
- **v5.19.1**: กฎการนับจำนวน — "จำนวนรุ่น" = **รุ่น-สี** (ไม่ใช่รุ่น ไม่ใช่ SKU) · "จำนวน/กี่" ที่ไม่ระบุหน่วยต้อง **ถามกลับ** (SKU / รุ่น-สี / ชิ้น) · ทุกคำตอบที่เป็นจำนวนต้องระบุหน่วย — วางกฎที่ `sales-agent` (ไฟล์แม่) และปรับหน่วย/ตารางในสกิลลูก

### Changelog
- **v3.0.0**: Migrated to PostgreSQL + pgvector. New tools: `sales_agent`, `pg_describe_table`, `pg_list_tables`. SQL syntax updated to PostgreSQL. Added `FY_Year` column support. SQM threshold ≥50.
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
| `sales_agent` | Execute PostgreSQL SELECT queries |
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
