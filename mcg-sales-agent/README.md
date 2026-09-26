# MCG Sales Agent

MC Group Data Analyst Agent plugin for Claude Code / Cowork.

ถามข้อมูลยอดขาย Retail/Fashion ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน MCP tools ที่เชื่อมต่อ PostgreSQL (pgvector).

> 📌 **ศัพท์ MCG:** ยอดขาย = **"Sales Out"** (plugin นี้) · การสั่งซื้อเข้า/PO = **"Sales In"** → ใช้ `mcg-inventory-agent` (po-intake)

## Version

**v5.19.8** — เกณฑ์จับคำต้องห้าม + check ก่อนส่ง
- **v5.19.8**: เปลี่ยนกฎ "ห้ามเปิดเผยภายใน" จากรายชื่อคำ (ซึ่งโมเดลลอกคำจากไฟล์มาพิมพ์เอง) เป็น **เกณฑ์จับคำ** — ห้ามคำที่ขึ้นต้น `ai.` · ลงท้าย `_synapse`/`_count`/`_key`/`_model`/`_color`/`_quantity` · ชื่อฟังก์ชัน SQL · snake_case · ชื่อ tool พร้อมเตือนให้ตรวจซ้ำก่อนส่ง (รวม Insight + footer) · เพิ่ม check นี้เข้า Final Validation ของทุกไฟล์แม่ (product/inventory/sales/crm/target + business-overview §7)
- **v5.19.7**: เพิ่มกฎ 🔢 **หน่วยต้องตรงประเภท** (SKU ≠ ชิ้น · รุ่น-สี ≠ ชิ้น — ห้ามเขียน "SKU 126,395 ชิ้น") และ **ตัวเลขที่นับได้ต้องเป็นค่าจริง (COUNT(DISTINCT)) ไม่ใช่ค่าประมาณ (APPROX_)** เพราะพบเคสจริงที่ตอบ 32,147 (ค่าประมาณ) ขณะที่ค่าจริงคือ 31,418 = คลาด 2.3% และคำตอบเดียวกันให้เลขไม่ตรงกันคนละรอบ · `product-agent` เพิ่มกฎสัดส่วน: ต้องใช้เศษและส่วนขอบเขตเดียวกัน (เคสจริง "MC = 53.8% ของทั้งหมด" มาจาก 17,291÷32,147 คนละขอบเขต ที่ถูกคือ 65% ในบรรดาที่ระบุแบรนด์)
- **v5.19.6**: เพิ่ม **รายการคำต้องห้าม** ในบล็อกกฎทุก skill — ห้ามปรากฏในคำตอบที่ผู้ใช้เห็นเด็ดขาด: `ai.dim_article` · `ai.fact_*` · `Article_Key` · `Article_Model` · `Article_Model_Color` · `item_code` · `model_color` · `sku_count` · `model_color_count` · ชื่อ tool/MCP · SQL พร้อมคำธุรกิจที่ให้ใช้แทน (จำนวน SKU / จำนวนรุ่น (รุ่น-สี) / จำนวนชิ้น · "ข้อมูลสินค้าในระบบ" · footer = แหล่งกว้าง + as-of) — เพราะ agent ยังพิมพ์ชื่อคอลัมน์ในตารางคำตอบแม้มีกฎห้ามแล้ว
- **v5.19.5**: เพิ่มบรรทัดบังคับในบล็อกกฎทุก skill: 🚫 ห้ามพิมพ์ชื่อตาราง/คอลัมน์/tool/SQL ในคำตอบที่ผู้ใช้เห็น **รวมทั้งกล่อง Insight และ Data Footer** · แก้ความขัดแย้ง "มีกี่รุ่น": คำว่า "รุ่น" = หน่วยที่ระบุแล้ว ⇒ ตอบเป็นรุ่น-สีได้เลย ไม่ต้องถามกลับ (ฝั่ง sales/pricing แก้ให้ตรงกับ product/inventory) · `stock-health` เพิ่มวลีนำทางจำนวน ("สต็อกมีกี่รุ่น-สี") · `assortment-summary` เตือนว่า "รวม" ของตาราง ≠ ยอดทั้ง master
- **v5.19.4**: เวลาถามกลับ/ยืนยันกับผู้ใช้ ให้เรียก tool **`AskUserQuestion`** เสมอ (ตัวเลือก 2–4 ข้อที่เลือกได้จริง · header สั้น + คำถามชัด) — 🚫 ห้ามพิมพ์คำถามลอย ๆ ในคำตอบ · ทั้ง 38 skill มีข้อกำหนดนี้ในบล็อกกฎ และไฟล์แม่ของแต่ละปลั๊กอินมีสเปกวิธีเรียก · ตัวอย่าง "ถาม: ..." ในไฟล์ = เนื้อหาที่ใส่ใน tool call
- **v5.19.3**: แก้ตามผลตรวจ: ถามกลับแบบ 3 ตัวเลือก (SKU / รุ่น (รุ่น-สี) / ชิ้น) แทนการแยก «รุ่น» ออกมา · ติดหน่วย Tickets (ใบเสร็จ) และตาราง Member (฿/ใบ/ชิ้น) · `total_quantity` = จำนวนชิ้น · `pricing-promotion` ให้ถามกลับก่อนค่อยรัน SQL · `category-hierarchy` นับ SKU/รุ่น-สี เฉพาะช่วง FY ปัจจุบัน (FILTER) ให้ตรงหัวตาราง · ระบุกฎตอบ "รับของเข้า" เป็นจำนวนชิ้นในไฟล์แม่
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
