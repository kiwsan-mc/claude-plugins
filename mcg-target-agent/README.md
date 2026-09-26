# MCG Target Agent

MC Group Sales Target Analyst Agent plugin for Claude Code / Cowork.

ถามข้อมูลเป้าขาย vs ยอดจริง (% achievement) และยอดขายระดับ invoice (Company/Account) ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน Synapse MCP tools.

## Version

**v2.1.5** — รายการคำต้องห้ามห้ามพิมพ์ในคำตอบ
- **v2.1.5**: เพิ่ม **รายการคำต้องห้าม** ในบล็อกกฎทุก skill — ห้ามปรากฏในคำตอบที่ผู้ใช้เห็นเด็ดขาด: `ai.dim_article` · `ai.fact_*` · `Article_Key` · `Article_Model` · `Article_Model_Color` · `item_code` · `model_color` · `sku_count` · `model_color_count` · ชื่อ tool/MCP · SQL พร้อมคำธุรกิจที่ให้ใช้แทน (จำนวน SKU / จำนวนรุ่น (รุ่น-สี) / จำนวนชิ้น · "ข้อมูลสินค้าในระบบ" · footer = แหล่งกว้าง + as-of) — เพราะ agent ยังพิมพ์ชื่อคอลัมน์ในตารางคำตอบแม้มีกฎห้ามแล้ว
- **v2.1.4**: เพิ่มบรรทัดบังคับในบล็อกกฎทุก skill: 🚫 ห้ามพิมพ์ชื่อตาราง/คอลัมน์/tool/SQL ในคำตอบที่ผู้ใช้เห็น **รวมทั้งกล่อง Insight และ Data Footer** · แก้ความขัดแย้ง "มีกี่รุ่น": คำว่า "รุ่น" = หน่วยที่ระบุแล้ว ⇒ ตอบเป็นรุ่น-สีได้เลย ไม่ต้องถามกลับ (ฝั่ง sales/pricing แก้ให้ตรงกับ product/inventory) · `stock-health` เพิ่มวลีนำทางจำนวน ("สต็อกมีกี่รุ่น-สี") · `assortment-summary` เตือนว่า "รวม" ของตาราง ≠ ยอดทั้ง master
- **v2.1.3**: เวลาถามกลับ/ยืนยันกับผู้ใช้ ให้เรียก tool **`AskUserQuestion`** เสมอ (ตัวเลือก 2–4 ข้อที่เลือกได้จริง · header สั้น + คำถามชัด) — 🚫 ห้ามพิมพ์คำถามลอย ๆ ในคำตอบ · ทั้ง 38 skill มีข้อกำหนดนี้ในบล็อกกฎ และไฟล์แม่ของแต่ละปลั๊กอินมีสเปกวิธีเรียก · ตัวอย่าง "ถาม: ..." ในไฟล์ = เนื้อหาที่ใส่ใน tool call
- **v2.1.2**: ย้ำกฎ **ห้ามเดาข้อมูลมาตอบ** (ใช้กับทุก runtime โดยเฉพาะ Claude Desktop / Cowork) ใน **ทุก skill** ของปลั๊กอิน — ทุกตัวเลข/ข้อเท็จจริงต้องมาจากผลการเรียก tool จริงในบทสนทนาและอ้างอิงกลับได้ · เรียกแล้วไม่พบข้อมูลให้ตอบว่า "ไม่พบข้อมูล" ตามจริง (แยกจาก 0) · ห้ามเดา/ประมาณ/แต่งตัวเลข/ตอบจากความจำของโมเดล
- **v2.1.1**: กฎการนับจำนวน — "จำนวนรุ่น" = รุ่น-สี · "จำนวน/กี่" ที่ไม่ระบุหน่วยต้องถามกลับ · ทุกคำตอบที่เป็นจำนวนต้องระบุหน่วย

- **v2.1.0**: บังคับส่ง `start_date` / `end_date` ทุกครั้ง (default = `month_start` → `max_date` จาก anchor) — ไม่ใส่จะสแกนทั้งตาราง fact ใช้เวลา 60–100 วิ เทียบกับ 6 วิเมื่อใส่ช่วง 1 เดือน
- **v2.0.0**: ย้ายจาก `gold.script_sales_target` / `silver.sap_zsdr006` ไป `ai.dim_target_main_lines` / `ai.fact_daily_sales_account`; **ถอด target แยก category** (ตารางเป้าใหม่มีแค่ระดับสาขา × วัน); เพิ่มการกรองช่วงวันที่ใน `sales_target_vs_actual_synapse`
- **v1.1.0**: เพิ่ม freshness + validation rules
- **v1.0.0**: เริ่มต้น — target & company-sales domain

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
