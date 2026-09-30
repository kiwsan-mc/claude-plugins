# MCG Target Agent

MC Group Sales Target Analyst Agent plugin for Claude Code / Cowork.

ถามข้อมูลเป้าขาย vs ยอดจริง (% achievement) และยอดขายระดับ invoice (Company/Account) ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน Synapse MCP tools.

## Version

**v2.1.24** — ภูมิภาค dynamic: ห้าม hardcode ค่า · เตือนเมื่อชื่อเดิมหาย
- **v2.1.24**: เพิ่มกฎ **ห้าม hardcode ค่าภูมิภาค** (ค่ามัน dynamic): ให้ดึงค่าจริงจากระบบก่อนจัดกลุ่ม/รายงาน · ถ้าชื่อที่ผู้ใช้ถามไม่มีในผลลัพธ์ ให้ **เตือนว่าป้ายชื่อถูกจัดกลุ่มใหม่** ไม่ใช่ตอบ 0 · 🚫 ห้ามสรุป "ยอดตก" จากชื่อที่จับคู่ไม่ตรง (ชื่อเปลี่ยน ≠ ยอดหาย) · แนบหลักฐานประกอบแบบระบุวันที่ (2026-09-30): ชุดภูมิภาคเป็นชื่อรวมกลุ่ม กลุ่ม Mobile มี 1–2 สาขา/ภูมิภาค จึงไม่ใช่สาเหตุของยอดตกก้อนใหญ่
- **v2.1.23**: ปิดเคส "ยอดหาย 2.9M" ตามที่ธุรกิจสั่ง: กำหนด **แหล่งมาตรฐานของยอดขาย = "Sales Out" จาก mcg-sales** ในกฎของทุกสกิล (38 ไฟล์) — ถ้าใช้หลายแหล่งต้องเรียกชื่อเป็นภาษาธุรกิจ ("Sales Out (mcg-sales)" · "ยอดขายบริษัท (invoice)") และ **ห้ามพิมพ์ชื่อตาราง/ระบบในคำตอบหรือ footer** (เคสจริง: footer หลุด `mcg_aiplatform_sales` และคำตอบสลับระหว่างฝั่ง invoice 294.02M กับ Sales Out 296.94M) · `target-achievement` เพิ่มกฎ: ยอดขายจริงสำหรับเทียบเป้าใช้ Sales Out + กฎ VAT (เป้า incl VAT vs Sales Out excl VAT ต้องกำกับฐาน) + ห้ามสลับแหล่งกลางคำตอบ + ทุกตารางใช้ช่วงวันที่เดียวกับ Headline
- **v2.1.22**: เพิ่มกฎบังคับจากเคสจริง: คำตอบเดียวเคยมี Headline เป้า 1–27 (356.03M) แต่ตาราง Channel ใช้เป้าเต็มเดือน (390.97M) + ยอด POS (313.26M) ⇒ **ทุกตารางต้องใช้ช่วงวันที่และฐานเดียวกับ Headline** · ยอดขายบริษัทนับ **ทุกสาขา** (ไม่จำกัดเฉพาะสาขาที่มีเป้า ซึ่งทำให้หาย 4.4M)
- **v2.1.21**: ใช้ข้อเสนอ P6: เพิ่ม **trigger eval ให้ครบ 38/38 สกิล** (เดิมมีแค่ 5 ของ inventory) — รวม **655 เคส** (positive 427 · negative 228) · ตรวจแล้ว: JSON ถูกต้องทุกไฟล์ · ไม่มีคำถามซ้ำในไฟล์ · **ไม่มีวลีใดเป็น positive ของมากกว่า 1 สกิล** (ข้อกำหนดสำคัญของการทดสอบ routing) · วลี negatives อ้างสกิลพี่น้อง/ข้ามโดเมนตามจริง · ไม่มีชื่อคอลัมน์/ตาราง/SQL/ตัวเลขสมมติในคำถาม
- **v2.1.20**: ใช้ข้อเสนอ P1: ย่อบล็อกกฎใน **27 สกิลลูก** จาก ~21 บรรทัด (8 KB) → 5 บรรทัด (~1.4 KB) โดย **คงกฎที่ใช้งานจริงครบทุกข้อ** (ห้ามเดา · ห้ามเปิดไส้ใน + เกณฑ์จับคำ + footer · หน่วย/ถามกลับ/ค่าจริง · กระทบยอด + ตัวอย่างห้ามใช้ตอบ) แล้วชี้ไปที่ "§1 ของ skill แม่" ซึ่ง include อยู่แล้ว ⇒ ไฟล์แม่ 6 ไฟล์และไฟล์ที่ไม่มี include (5 ไฟล์ office/software) ยังพกฉบับเต็มไว้
- **v2.1.19**: แก้ตามผลรีวิวความซ้ำ: (1) **ฐานสต็อก** — `business-overview` สอนให้ใช้ Stock_Total_* และห้าม Stock_Quantity ซึ่ง **ตรงข้ามกับกฎธุรกิจ** (คงเหลือ = Stock_Quantity) ⇒ แก้ให้ตรง inventory-agent (2) **footer 3 จุดยังพิมพ์ชื่อตาราง** `mcg_aiplatform_sales` (ขัดกฎห้ามเปิดไส้ใน) ⇒ เปลี่ยนเป็น "Sales Out (Postgres)" (3) **schema ปลดระวาง** `gold`/`silver` ในตารางแหล่งข้อมูล ⇒ `ai` (4) บล็อกกฎของ `sales-agent` ถูกตัดขาดกลาง (มีบรรทัดลอยแทรก) ⇒ ต่อกลับเป็นบล็อกเดียว (5) `generate-srs` เพิ่ม `AskUserQuestion` ใน allowed-tools (เดิมกฎสั่งให้เรียกแต่ tool ไม่อยู่ใน allowlist) (6) ตัวอย่าง "หน่วยผิด" ในบล็อกทุกไฟล์ใช้เลขจริง 126,395/31,418 ⇒ เปลี่ยนเป็นเลขสมมติ (7) เติมสถานะล่าสุดของตารางรายวันใน business-overview
- **v2.1.18**: ตามผลรีวิว: `target-achievement` เลิกอ้างคอลัมน์ `target_weight` ที่ tool ไม่คืน · `target-agent` แก้ 3 จุด — rebate (ตารางนี้ rebate เป็น 0 ⇒ ไม่มีตัวเลข rebate) · sales mix (ตารางเป้ามีแค่สาขา×วัน ⇒ ไม่มี category/LY) · Step 1 เลิกเขียน SQL หา anchor เอง ให้เรียก `max_invoice_date_synapse`
- **v2.1.17**: เพิ่ม `sales_vs_target_by_subchannel_synapse` reproduce รายงานบริษัท (Target · Net Sales BGP · Ach% · LY · YoY ตาม Sub_Channel) ตรงกับรายงานจริงทุกหลัก · **แก้กฎ VAT ให้ตรงรายงาน: Ach% = Net ÷ Target โดยไม่แปลง VAT** (คอลัมน์ ×1.07 เก็บไว้เป็นข้อมูลเสริม) · เพิ่ม Step 0.6 อธิบายนิยามคอลัมน์ + สูตร ASP/ATV/UPT
- **v2.1.16**: เพิ่ม `sales_target_vs_company_synapse` — เป้า vs ยอดขายบริษัท (invoice · Net_Sales_BGP) ระดับเดือนทั้งบริษัท จำกัดเฉพาะสาขา×วันที่มีเป้า · คืนค่าที่แปลง ×1.07 ให้เทียบกับเป้าได้ตรง + %achievement · skill `target-achievement` เพิ่ม Step 0.5 อธิบาย 2 ฐาน (Company / Sales Out) + กฎ VAT
- **v2.1.15**: เติมเกณฑ์คอลัมน์ (ยอดขาย = `Net_Sales_BGP` · COGS = `COGS`) ลงใน frontmatter description + Headline ของ `company-account-sales` ให้ agent เห็นก่อนอ่านเนื้อไฟล์
- **v2.1.14**: 🔴 **แก้ bug สำคัญ** — ตาราง `ai.dim_target_main_lines` มีคอลัมน์จริง 5 ตัว (`Target_Year` · `Target_Month` · `Branch_Code` · `Target_Date` · **`Target_exc_vat`**) แต่ tool/skill อ้าง `Target_Value` · `Target_Weight` · `Date_Key` ที่ **ไม่มีจริง** ⇒ tool เป้า error ทุกครั้ง · แก้ tool 2 ตัว (`sales_target_vs_actual_synapse`, `target_sales_mix_synapse`) ให้ใช้ `Target_exc_vat` + join ฝั่งเป้าด้วย `Target_Date` และตัดคอลัมน์ target weight ออก (verified: ก.ย. 2026 เป้ารวม ฿390.97M · 586 สาขา)
- **v2.1.13**: แก้ตามคำสั่ง: **"ยอดขาย" ใช้ `Net_Sales_BGP`** (ไม่ใช่ `Net_Sales_Exclude_VAT`) และ **COGS/GP% ใช้ `COGS`** — GP = BGP − COGS · GP% = GP ÷ BGP × 100 (จริง 1-20 ก.ย. 2026: ใหม่ 153.38M/66.30% vs เก่า 149.34M/65.89%) · **กลับกฎเดิมที่ห้ามใช้ COGS** · `company-account-sales` ปรับตาราง/สูตร + ระบุเกณฑ์ทุกครั้ง
- **v2.1.12**: เพิ่ม 2 กฎจากเคสจริงรอบล่าสุด: (1) 🚫 **ห้ามวงเล็บชื่อทางเทคนิคต่อท้ายคำธุรกิจ** — รูปแบบที่หลุดซ้ำ ๆ คือ "รุ่น-สี (ชื่อคอลัมน์)" / "Product Master (ชื่อตาราง)" ⇒ ห้ามวงเล็บคำที่ขึ้นต้น `ai.` หรือ snake_case ต่อท้ายคำธุรกิจ (2) 🧮 **กระทบยอดก่อนส่ง** — ผลรวมของแถวในตารางต้องเท่ากับยอดรวมที่เขียน ถ้าไม่ตรงให้หาสาเหตุ/ระบุขอบเขต/แก้ตัวเลข และห้ามสร้างกลุ่ม "อื่น ๆ" ที่ยอดเกินส่วนที่เหลือ (เคสจริง: ตารางรายแบรนด์บวกได้ 27,141 แต่ยอดที่เขียน 26,541)
- **v2.1.11**: ตัดชื่อคอลัมน์ออกจาก **ประโยคกฎ** 29 บรรทัดใน 14 ไฟล์ (เหลือไว้เฉพาะใน SQL/mapping ที่ต้องใช้เขียน query) เพราะโมเดลลอกคำจากประโยคกฎไปพิมพ์ในคำตอบ · และ `product-agent` สั่งห้ามถามกลับสำหรับ "มีกี่รุ่น"/"จำนวนรุ่น"/"กี่รุ่น" โดยตรง — ให้ตอบจำนวนรุ่น-สีทันที ถ้าจะถามให้ถามเรื่องขอบเขต (ทั้งระบบ vs กรองแบรนด์/หมวด) แทน
- **v2.1.10**: แก้ root cause ของการเปิดไส้ใน: **template footer ในไฟล์เองมีคำต้องห้าม** — ลบ "(Synapse)" ออกจาก footer ทุกจุด (12 จุดใน 5 ปลั๊กอิน) เพราะโมเดลลอกตาม template ของไฟล์ · และย้ายกฎ 🙈 ห้ามพิมพ์ชื่อตาราง/คอลัมน์/tool/SQL ขึ้นเป็น **ข้อแรกสุดของบล็อกกฎ** ในทุก skill (จากเดิมอยู่ข้อ 6) ให้ความสำคัญสูงสุด
- **v2.1.9**: เพิ่มการตีความตามที่ผู้ใช้เลือก: **ถามกลับเฉพาะเมื่อกำกวมจริง** — "มีกี่รุ่น"/"จำนวนรุ่น" (ระบุหน่วยแล้ว) ตอบเป็นรุ่น-สีได้เลย · ที่ต้องถามคือ "จำนวน/กี่/เท่าไหร่" ที่ไม่ระบุหน่วย หรือคำถามที่ขาดช่วงเวลา/มิติที่จำเป็น — ระบุตัวอย่างทั้งสองฝั่งไว้ในบล็อกกฎทุก skill
- **v2.1.8**: ประกาศ **`AskUserQuestion`** ใน frontmatter `tools:` ของทุก skill ที่มีรายการ tools อยู่แล้ว (34 ไฟล์) ตามที่ผู้ใช้เลือก — เพื่อให้เรียก tool ได้แน่นอนเมื่อต้องถามกลับ · ไฟล์ที่ไม่มี `tools:` (artifact-creator, email-digest, email-template, generate-srs) ไม่เติม key ใหม่ เพราะการสร้าง allowlist ขึ้นมาอาจตัด tool MCP อื่นของสกิลนั้น · แก้ frontmatter ที่พังจริง 2 ไฟล์: `sales-agent` (บรรทัด note หลุดเข้าไปใน description block จน YAML พัง — ย้ายไปไว้ในเนื้อไฟล์) และ `ms-excel` (description เป็นบรรทัดเดียวมี ": " ทำให้ YAML ไม่ผ่าน — เปลี่ยนเป็น folded block) ⇒ ตอนนี้ frontmatter ทั้ง 38 ไฟล์ parse ผ่านหมด
- **v2.1.7**: เปลี่ยนกฎ "ห้ามเปิดเผยภายใน" จากรายชื่อคำ (ซึ่งโมเดลลอกคำจากไฟล์มาพิมพ์เอง) เป็น **เกณฑ์จับคำ** — ห้ามคำที่ขึ้นต้น `ai.` · ลงท้าย `_synapse`/`_count`/`_key`/`_model`/`_color`/`_quantity` · ชื่อฟังก์ชัน SQL · snake_case · ชื่อ tool พร้อมเตือนให้ตรวจซ้ำก่อนส่ง (รวม Insight + footer) · เพิ่ม check นี้เข้า Final Validation ของทุกไฟล์แม่ (product/inventory/sales/crm/target + business-overview §7)
- **v2.1.6**: เพิ่มกฎ 🔢 **หน่วยต้องตรงประเภท** (SKU ≠ ชิ้น · รุ่น-สี ≠ ชิ้น — ห้ามเขียน "SKU 126,395 ชิ้น") และ **ตัวเลขที่นับได้ต้องเป็นค่าจริง (COUNT(DISTINCT)) ไม่ใช่ค่าประมาณ (APPROX_)** เพราะพบเคสจริงที่ตอบ 32,147 (ค่าประมาณ) ขณะที่ค่าจริงคือ 31,418 = คลาด 2.3% และคำตอบเดียวกันให้เลขไม่ตรงกันคนละรอบ · `product-agent` เพิ่มกฎสัดส่วน: ต้องใช้เศษและส่วนขอบเขตเดียวกัน (เคสจริง "MC = 53.8% ของทั้งหมด" มาจาก 17,291÷32,147 คนละขอบเขต ที่ถูกคือ 65% ในบรรดาที่ระบุแบรนด์)
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
