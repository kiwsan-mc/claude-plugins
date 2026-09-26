# MCG Product Agent

MC Group Product Master Analyst Agent plugin for Claude Code / Cowork.

ถามข้อมูล master สินค้า (assortment) — จำนวน SKU / รุ่น (รุ่น-สี), แบรนด์, หมวดหมู่, ราคา, margin — ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน Synapse MCP tools.

> ⚠️ **"จำนวนรุ่น" = รุ่น-สี** (ไม่ใช่รุ่น และไม่ใช่ SKU) · "จำนวน"/"กี่" ที่ไม่ระบุหน่วย → **ถามกลับก่อน** (SKU / รุ่น (รุ่น-สี) / ชิ้น) ห้ามเดาแล้วตอบตัวเลขเดียว · ทุกจำนวนต้องมีหน่วยกำกับ

## Version

**v1.2.9** — ประกาศ AskUserQuestion ใน frontmatter + แก้ frontmatter ที่พัง
- **v1.2.9**: ประกาศ **`AskUserQuestion`** ใน frontmatter `tools:` ของทุก skill ที่มีรายการ tools อยู่แล้ว (34 ไฟล์) ตามที่ผู้ใช้เลือก — เพื่อให้เรียก tool ได้แน่นอนเมื่อต้องถามกลับ · ไฟล์ที่ไม่มี `tools:` (artifact-creator, email-digest, email-template, generate-srs) ไม่เติม key ใหม่ เพราะการสร้าง allowlist ขึ้นมาอาจตัด tool MCP อื่นของสกิลนั้น · แก้ frontmatter ที่พังจริง 2 ไฟล์: `sales-agent` (บรรทัด note หลุดเข้าไปใน description block จน YAML พัง — ย้ายไปไว้ในเนื้อไฟล์) และ `ms-excel` (description เป็นบรรทัดเดียวมี ": " ทำให้ YAML ไม่ผ่าน — เปลี่ยนเป็น folded block) ⇒ ตอนนี้ frontmatter ทั้ง 38 ไฟล์ parse ผ่านหมด
- **v1.2.8**: เปลี่ยนกฎ "ห้ามเปิดเผยภายใน" จากรายชื่อคำ (ซึ่งโมเดลลอกคำจากไฟล์มาพิมพ์เอง) เป็น **เกณฑ์จับคำ** — ห้ามคำที่ขึ้นต้น `ai.` · ลงท้าย `_synapse`/`_count`/`_key`/`_model`/`_color`/`_quantity` · ชื่อฟังก์ชัน SQL · snake_case · ชื่อ tool พร้อมเตือนให้ตรวจซ้ำก่อนส่ง (รวม Insight + footer) · เพิ่ม check นี้เข้า Final Validation ของทุกไฟล์แม่ (product/inventory/sales/crm/target + business-overview §7)
- **v1.2.7**: เพิ่มกฎ 🔢 **หน่วยต้องตรงประเภท** (SKU ≠ ชิ้น · รุ่น-สี ≠ ชิ้น — ห้ามเขียน "SKU 126,395 ชิ้น") และ **ตัวเลขที่นับได้ต้องเป็นค่าจริง (COUNT(DISTINCT)) ไม่ใช่ค่าประมาณ (APPROX_)** เพราะพบเคสจริงที่ตอบ 32,147 (ค่าประมาณ) ขณะที่ค่าจริงคือ 31,418 = คลาด 2.3% และคำตอบเดียวกันให้เลขไม่ตรงกันคนละรอบ · `product-agent` เพิ่มกฎสัดส่วน: ต้องใช้เศษและส่วนขอบเขตเดียวกัน (เคสจริง "MC = 53.8% ของทั้งหมด" มาจาก 17,291÷32,147 คนละขอบเขต ที่ถูกคือ 65% ในบรรดาที่ระบุแบรนด์)
- **v1.2.6**: เพิ่ม **รายการคำต้องห้าม** ในบล็อกกฎทุก skill — ห้ามปรากฏในคำตอบที่ผู้ใช้เห็นเด็ดขาด: `ai.dim_article` · `ai.fact_*` · `Article_Key` · `Article_Model` · `Article_Model_Color` · `item_code` · `model_color` · `sku_count` · `model_color_count` · ชื่อ tool/MCP · SQL พร้อมคำธุรกิจที่ให้ใช้แทน (จำนวน SKU / จำนวนรุ่น (รุ่น-สี) / จำนวนชิ้น · "ข้อมูลสินค้าในระบบ" · footer = แหล่งกว้าง + as-of) — เพราะ agent ยังพิมพ์ชื่อคอลัมน์ในตารางคำตอบแม้มีกฎห้ามแล้ว
- **v1.2.5**: เพิ่มกฎ 🔴 **ห้ามเอาผลบวกของตาราง group by มาตอบเป็นยอด "ทั้งระบบ"** — แถวที่ dimension เป็น NULL ถูกตัดออก (ตรวจ 2026-09-26: รุ่น-สีทั้ง master 31,418 · ผลบวกรายแบรนด์ 26,541 เพราะไม่มีแบรนด์ 4,877 รุ่น-สี · `APPROX_` คลาดอีก ~1–2%) ⇒ ยอดทั้งระบบให้นับ `COUNT(DISTINCT ...)` ระดับ master และถ้ารายงาน "รวม" ของตาราง ให้กำกับว่า "รวมเฉพาะที่มีค่า <dimension>"
- **v1.2.4**: เพิ่มบรรทัดบังคับในบล็อกกฎทุก skill: 🚫 ห้ามพิมพ์ชื่อตาราง/คอลัมน์/tool/SQL ในคำตอบที่ผู้ใช้เห็น **รวมทั้งกล่อง Insight และ Data Footer** · แก้ความขัดแย้ง "มีกี่รุ่น": คำว่า "รุ่น" = หน่วยที่ระบุแล้ว ⇒ ตอบเป็นรุ่น-สีได้เลย ไม่ต้องถามกลับ (ฝั่ง sales/pricing แก้ให้ตรงกับ product/inventory) · `stock-health` เพิ่มวลีนำทางจำนวน ("สต็อกมีกี่รุ่น-สี") · `assortment-summary` เตือนว่า "รวม" ของตาราง ≠ ยอดทั้ง master
- **v1.2.3**: เวลาถามกลับ/ยืนยันกับผู้ใช้ ให้เรียก tool **`AskUserQuestion`** เสมอ (ตัวเลือก 2–4 ข้อที่เลือกได้จริง · header สั้น + คำถามชัด) — 🚫 ห้ามพิมพ์คำถามลอย ๆ ในคำตอบ · ทั้ง 38 skill มีข้อกำหนดนี้ในบล็อกกฎ และไฟล์แม่ของแต่ละปลั๊กอินมีสเปกวิธีเรียก · ตัวอย่าง "ถาม: ..." ในไฟล์ = เนื้อหาที่ใส่ใน tool call
- **v1.2.2**: ย้ำกฎ **ห้ามเดาข้อมูลมาตอบ** (ใช้กับทุก runtime โดยเฉพาะ Claude Desktop / Cowork) ใน **ทุก skill** ของปลั๊กอิน — ทุกตัวเลข/ข้อเท็จจริงต้องมาจากผลการเรียก tool จริงในบทสนทนาและอ้างอิงกลับได้ · เรียกแล้วไม่พบข้อมูลให้ตอบว่า "ไม่พบข้อมูล" ตามจริง (แยกจาก 0) · ห้ามเดา/ประมาณ/แต่งตัวเลข/ตอบจากความจำของโมเดล
- **v1.2.1**: กฎการนับจำนวน — **"จำนวนรุ่น" = รุ่น-สี** ไม่ใช่รุ่น ไม่ใช่ SKU · "จำนวน/กี่" ที่ไม่ระบุหน่วยต้อง **ถามกลับ** (SKU / รุ่น-สี / ชิ้น) · ทุกคำตอบที่เป็นจำนวนต้องระบุหน่วย · เพิ่มคอลัมน์ `model_color_count` ในตาราง Assortment (ตรวจ 2026-09-26: SKU 128,121 · รุ่น 23,815 · รุ่น-สี 31,418)

- **v1.2.0**: ย้ายจาก `silver.sap_article` ไป `ai.dim_article` (ตัด prefix `S_ATC_` ออก, join ด้วย `Article_Key`); ระบุว่า `Grade` / `Color_Tone` ว่างทั้งหมด
- **v1.1.0**: เพิ่ม freshness + validation rules
- **v1.0.0**: เริ่มต้น — product master domain

> ⚠️ นี่คือ **master data ของสินค้า** ไม่ใช่ยอดขาย/สต็อก — ถามยอดขายใช้ `mcg-sales-agent`, ถามสต็อกใช้ `mcg-inventory-agent`

## Skills

| Skill | Role | หน้าที่ |
|-------|------|---------|
| `product-agent` | Product Master Agent | กฎกลาง, tool priority, product dimensions, ขอบเขต (shared foundation) |
| `assortment-summary` | Merchandise Planner | จำนวน SKU / รุ่น (รุ่น-สี) + ราคา + margin แยก dimension (ระบุหน่วยทุกตัวเลข) |
| `attribute-explorer` | Catalog Specialist | list distinct values + drill SKU รายตัว |
| `pricing-structure` | Pricing Analyst | โครงสร้างราคา + margin ตาม price band/category |

## Architecture

```
skills/
├── product-agent/          ← SKILL.md หลัก (rules, tool priority, dimensions, scope)
├── assortment-summary/     ← #[[file:../product-agent/SKILL.md]] + role prompt
├── attribute-explorer/     ← #[[file:../product-agent/SKILL.md]] + role prompt
└── pricing-structure/      ← #[[file:../product-agent/SKILL.md]] + role prompt
```

## MCP Tools (Synapse — server: `synapse-product`)

| Tool | Description |
|------|-------------|
| `product_dimension_summary_synapse` | จำนวน SKU / รุ่น / รุ่น-สี + avg tag/selling price + margin% แยก dimension (ต้องระบุหน่วยของจำนวนทุกครั้ง) |
| `product_attribute_values_synapse` | list distinct values ของ attribute (+จำนวน SKU เท่านั้น — ไม่ใช่จำนวนรุ่น/รุ่น-สี) |
| `product_list_synapse` | list SKU รายตัว + attributes |
| `product_query_synapse` | Raw T-SQL (SELECT/WITH) — fallback |
| `describe_table_product_synapse` | Schema lookup |
| `search_columns_product_synapse` | Column search |

## Data Source

- `ai.dim_article` — product master (brand, Level1-5, gender, season, color, size, aging, sales type, vendor, price, cost)
- ไม่มีตัวเลขยอดขาย/สต็อกในตารางนี้

> อัปเดต: ย้ายจาก `silver.sap_article` มาเป็น schema `[ai]` แล้ว (ตารางเดิมยังอยู่แต่เลิกใช้) — คอลัมน์ตัด prefix `S_ATC_` ออก และ join ด้วย `Article_Key`
> ⚠️ `Grade` / `Color_Tone` ว่างทั้งหมด (100% NULL) — ใช้ `Fashion_Grade_Text` / `Color` แทน
> 📌 จำนวน ณ 2026-09-26: SKU 128,121 · รุ่น 23,815 · รุ่น-สี 31,418 — สามหน่วยนี้ไม่เท่ากัน (ต่างกัน ~32%) · "จำนวนรุ่น" = รุ่น-สี

## Usage

- "มีกี่ SKU แยกตามแบรนด์" → `assortment-summary`
- "มีกี่รุ่น-สี แยกตามแบรนด์" → `assortment-summary` (ถาม "กี่รุ่น" ไม่ต้องถามกลับ — ตอบเป็นรุ่น-สี)
- "มีสินค้ากี่ตัว" (ไม่ระบุหน่วย) → **ถามกลับก่อน** ว่า SKU / รุ่น (รุ่น-สี) / ชิ้น
- "มีสีอะไรบ้าง / list สินค้ายีนส์" → `attribute-explorer`
- "โครงสร้างราคาแยก price band" → `pricing-structure`
