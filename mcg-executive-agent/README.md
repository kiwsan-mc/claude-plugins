# MCG Executive Agent

MC Group Executive Overview Agent plugin for Claude Code / Cowork.

สรุปภาพรวมธุรกิจเป็น executive summary เดียว — ดึง KPI จากหลาย domain (Sales Out + สต็อก/Sales In + Product + Target + Member/CRM) แล้วสังเคราะห์เป็นภาพรวมเดียว แทนที่จะให้แต่ละ domain agent ตอบแยกกัน

รองรับทั้ง:
- **ภาพรวมครบ 5 ด้าน** ("ภาพรวม" / "overview" / "ทุกด้าน")
- **สรุปข้าม domain เฉพาะ** (เช่น "Sales + Target", "ยอดขาย + เป้า", "สรุป ... พร้อม ...") — ดึงแยก query แต่ตอบเป็น summary เดียว

## Version

**v3.0.12** — ห้ามวงเล็บชื่อทางเทคนิค + กระทบยอดตัวเลขก่อนส่ง
- **v3.0.12**: เพิ่ม 2 กฎจากเคสจริงรอบล่าสุด: (1) 🚫 **ห้ามวงเล็บชื่อทางเทคนิคต่อท้ายคำธุรกิจ** — รูปแบบที่หลุดซ้ำ ๆ คือ "รุ่น-สี (ชื่อคอลัมน์)" / "Product Master (ชื่อตาราง)" ⇒ ห้ามวงเล็บคำที่ขึ้นต้น `ai.` หรือ snake_case ต่อท้ายคำธุรกิจ (2) 🧮 **กระทบยอดก่อนส่ง** — ผลรวมของแถวในตารางต้องเท่ากับยอดรวมที่เขียน ถ้าไม่ตรงให้หาสาเหตุ/ระบุขอบเขต/แก้ตัวเลข และห้ามสร้างกลุ่ม "อื่น ๆ" ที่ยอดเกินส่วนที่เหลือ (เคสจริง: ตารางรายแบรนด์บวกได้ 27,141 แต่ยอดที่เขียน 26,541)
- **v3.0.11**: ตัดชื่อคอลัมน์ออกจาก **ประโยคกฎ** 29 บรรทัดใน 14 ไฟล์ (เหลือไว้เฉพาะใน SQL/mapping ที่ต้องใช้เขียน query) เพราะโมเดลลอกคำจากประโยคกฎไปพิมพ์ในคำตอบ · และ `product-agent` สั่งห้ามถามกลับสำหรับ "มีกี่รุ่น"/"จำนวนรุ่น"/"กี่รุ่น" โดยตรง — ให้ตอบจำนวนรุ่น-สีทันที ถ้าจะถามให้ถามเรื่องขอบเขต (ทั้งระบบ vs กรองแบรนด์/หมวด) แทน
- **v3.0.10**: แก้ root cause ของการเปิดไส้ใน: **template footer ในไฟล์เองมีคำต้องห้าม** — ลบ "(Synapse)" ออกจาก footer ทุกจุด (12 จุดใน 5 ปลั๊กอิน) เพราะโมเดลลอกตาม template ของไฟล์ · และย้ายกฎ 🙈 ห้ามพิมพ์ชื่อตาราง/คอลัมน์/tool/SQL ขึ้นเป็น **ข้อแรกสุดของบล็อกกฎ** ในทุก skill (จากเดิมอยู่ข้อ 6) ให้ความสำคัญสูงสุด
- **v3.0.9**: เพิ่มการตีความตามที่ผู้ใช้เลือก: **ถามกลับเฉพาะเมื่อกำกวมจริง** — "มีกี่รุ่น"/"จำนวนรุ่น" (ระบุหน่วยแล้ว) ตอบเป็นรุ่น-สีได้เลย · ที่ต้องถามคือ "จำนวน/กี่/เท่าไหร่" ที่ไม่ระบุหน่วย หรือคำถามที่ขาดช่วงเวลา/มิติที่จำเป็น — ระบุตัวอย่างทั้งสองฝั่งไว้ในบล็อกกฎทุก skill
- **v3.0.8**: ประกาศ **`AskUserQuestion`** ใน frontmatter `tools:` ของทุก skill ที่มีรายการ tools อยู่แล้ว (34 ไฟล์) ตามที่ผู้ใช้เลือก — เพื่อให้เรียก tool ได้แน่นอนเมื่อต้องถามกลับ · ไฟล์ที่ไม่มี `tools:` (artifact-creator, email-digest, email-template, generate-srs) ไม่เติม key ใหม่ เพราะการสร้าง allowlist ขึ้นมาอาจตัด tool MCP อื่นของสกิลนั้น · แก้ frontmatter ที่พังจริง 2 ไฟล์: `sales-agent` (บรรทัด note หลุดเข้าไปใน description block จน YAML พัง — ย้ายไปไว้ในเนื้อไฟล์) และ `ms-excel` (description เป็นบรรทัดเดียวมี ": " ทำให้ YAML ไม่ผ่าน — เปลี่ยนเป็น folded block) ⇒ ตอนนี้ frontmatter ทั้ง 38 ไฟล์ parse ผ่านหมด
- **v3.0.7**: เปลี่ยนกฎ "ห้ามเปิดเผยภายใน" จากรายชื่อคำ (ซึ่งโมเดลลอกคำจากไฟล์มาพิมพ์เอง) เป็น **เกณฑ์จับคำ** — ห้ามคำที่ขึ้นต้น `ai.` · ลงท้าย `_synapse`/`_count`/`_key`/`_model`/`_color`/`_quantity` · ชื่อฟังก์ชัน SQL · snake_case · ชื่อ tool พร้อมเตือนให้ตรวจซ้ำก่อนส่ง (รวม Insight + footer) · เพิ่ม check นี้เข้า Final Validation ของทุกไฟล์แม่ (product/inventory/sales/crm/target + business-overview §7)
- **v3.0.6**: เพิ่มกฎ 🔢 **หน่วยต้องตรงประเภท** (SKU ≠ ชิ้น · รุ่น-สี ≠ ชิ้น — ห้ามเขียน "SKU 126,395 ชิ้น") และ **ตัวเลขที่นับได้ต้องเป็นค่าจริง (COUNT(DISTINCT)) ไม่ใช่ค่าประมาณ (APPROX_)** เพราะพบเคสจริงที่ตอบ 32,147 (ค่าประมาณ) ขณะที่ค่าจริงคือ 31,418 = คลาด 2.3% และคำตอบเดียวกันให้เลขไม่ตรงกันคนละรอบ · `product-agent` เพิ่มกฎสัดส่วน: ต้องใช้เศษและส่วนขอบเขตเดียวกัน (เคสจริง "MC = 53.8% ของทั้งหมด" มาจาก 17,291÷32,147 คนละขอบเขต ที่ถูกคือ 65% ในบรรดาที่ระบุแบรนด์)
- **v3.0.5**: เพิ่ม **รายการคำต้องห้าม** ในบล็อกกฎทุก skill — ห้ามปรากฏในคำตอบที่ผู้ใช้เห็นเด็ดขาด: `ai.dim_article` · `ai.fact_*` · `Article_Key` · `Article_Model` · `Article_Model_Color` · `item_code` · `model_color` · `sku_count` · `model_color_count` · ชื่อ tool/MCP · SQL พร้อมคำธุรกิจที่ให้ใช้แทน (จำนวน SKU / จำนวนรุ่น (รุ่น-สี) / จำนวนชิ้น · "ข้อมูลสินค้าในระบบ" · footer = แหล่งกว้าง + as-of) — เพราะ agent ยังพิมพ์ชื่อคอลัมน์ในตารางคำตอบแม้มีกฎห้ามแล้ว
- **v3.0.4**: เพิ่มบรรทัดบังคับในบล็อกกฎทุก skill: 🚫 ห้ามพิมพ์ชื่อตาราง/คอลัมน์/tool/SQL ในคำตอบที่ผู้ใช้เห็น **รวมทั้งกล่อง Insight และ Data Footer** · แก้ความขัดแย้ง "มีกี่รุ่น": คำว่า "รุ่น" = หน่วยที่ระบุแล้ว ⇒ ตอบเป็นรุ่น-สีได้เลย ไม่ต้องถามกลับ (ฝั่ง sales/pricing แก้ให้ตรงกับ product/inventory) · `stock-health` เพิ่มวลีนำทางจำนวน ("สต็อกมีกี่รุ่น-สี") · `assortment-summary` เตือนว่า "รวม" ของตาราง ≠ ยอดทั้ง master
- **v3.0.3**: เวลาถามกลับ/ยืนยันกับผู้ใช้ ให้เรียก tool **`AskUserQuestion`** เสมอ (ตัวเลือก 2–4 ข้อที่เลือกได้จริง · header สั้น + คำถามชัด) — 🚫 ห้ามพิมพ์คำถามลอย ๆ ในคำตอบ · ทั้ง 38 skill มีข้อกำหนดนี้ในบล็อกกฎ และไฟล์แม่ของแต่ละปลั๊กอินมีสเปกวิธีเรียก · ตัวอย่าง "ถาม: ..." ในไฟล์ = เนื้อหาที่ใส่ใน tool call
- **v3.0.2**: ย้ำกฎ **ห้ามเดาข้อมูลมาตอบ** (ใช้กับทุก runtime โดยเฉพาะ Claude Desktop / Cowork) ใน **ทุก skill** ของปลั๊กอิน — ทุกตัวเลข/ข้อเท็จจริงต้องมาจากผลการเรียก tool จริงในบทสนทนาและอ้างอิงกลับได้ · เรียกแล้วไม่พบข้อมูลให้ตอบว่า "ไม่พบข้อมูล" ตามจริง (แยกจาก 0) · ห้ามเดา/ประมาณ/แต่งตัวเลข/ตอบจากความจำของโมเดล
- **v3.0.1**: กฎการนับจำนวน ("จำนวนรุ่น" = รุ่น-สี) และกฎ **"รับของเข้า → ตอบจำนวนชิ้น"** (ไม่ยกมูลค่าขึ้นนำ) ใช้กับด้าน Sales In/สต็อกของ overview

- **v3.0.0**: เพิ่ม `synapse-crm` — ภาพรวมครอบคลุม Member/CRM top-line (member sales share + CRM discount); การเจาะลึก member ยัง route ไป `mcg-crm-agent`
- **v2.0.0**: ย้ายแหล่งข้อมูลจาก `gold.` / `silver.` ไป schema `[ai]`; ถอด member / ticket / ATV ออกจาก KPI checklist เพราะไม่มีในแหล่งข้อมูลใหม่ (route ไป `mcg-sales-agent` แทน)
- **v1.2.0**: เพิ่ม freshness + validation rules
- **v1.1.0**: รองรับ cross-domain executive summary
- **v1.0.0**: เริ่มต้น — executive overview plugin

## Skills

| Skill | Role | หน้าที่ |
|-------|------|---------|
| `business-overview` | Executive Overview | เรียก anchor 4 ตัว → ดึง KPI 5 ด้าน → สรุป executive summary เดียว |

## Architecture

```
skills/
└── business-overview/   ← SKILL.md (orchestrator: anchor-first + KPI checklist 5 ด้าน + synthesis template)
```

## MCP Tools (Synapse — 5 servers)

| Domain | Server | Summary tools |
|--------|--------|---------------|
| Sales Out | `synapse-sales` | `max_sold_date_synapse`, `dashboard_kpi_overall_synapse`, `dashboard_by_channel_synapse`, `regional_sales_yoy_synapse`, `subchannel_breakdown_synapse`, `dim_channel_list_synapse`, `sales_agent_synapse`, `retail_sales_schema_cheatsheet_synapse` |
| Sales In / สต็อก | `synapse-inventory` | `max_stock_date_synapse`, `stock_on_hand_synapse`, `stock_value_by_aging_synapse`, `stock_in_transit_synapse`, `po_overdue_synapse` |
| Product | `synapse-product` | `product_dimension_summary_synapse` |
| Target | `synapse-target` | `max_invoice_date_synapse`, `sales_target_vs_actual_synapse`, `sales_company_summary_synapse`, `sales_query_synapse`, `company_sales_schema_cheatsheet_synapse` |
| Member/CRM (top-line) | `synapse-crm` | `max_member_date_synapse`, `member_kpi_overview_synapse`, `member_by_channel_synapse` |

## Usage

- "ภาพรวมธุรกิจ" / "overview" / "executive summary" / "ทุกด้าน" → `business-overview` (ครบ 5 ด้าน)
- "สรุป Sales Performance ... + Target ..." / "ยอดขาย + เป้า" / "เพิ่ม ... ด้วย" → `business-overview` (สรุปข้าม domain เป็น summary เดียว)
- คำถามเจาะลึก domain เดียว → ส่งไป agent เฉพาะ (mcg-sales-agent / mcg-inventory-agent / mcg-product-agent / mcg-target-agent / mcg-crm-agent)

## ขอบเขตข้อมูล (อัปเดต)

- ใช้ schema `[ai]` ของ Synapse (ย้ายจาก `gold.` / `silver.` แล้ว)
- ⚠️ **member/CRM มี 2 แหล่ง ห้ามเทียบกัน**: ภาพรวมนี้ดึง top-line member จาก `synapse-crm` (⚠️ **subset ~88 สาขา = กทม.+ออนไลน์**) ส่วน member ratio ทั้งบริษัท + YoY → **mcg-sales-agent** (`member-analysis`, Postgres ครอบคลุมทุกสาขา); เจาะลึก member รายตัว/RFM/tier → **mcg-crm-agent**
- ⚠️ **Tickets / ATV / UPT ไม่มีใน synapse sales fact** → ทั้งบริษัทใช้ **mcg-sales-agent**; เฉพาะ member subset ใช้ `member_ticket_atv_synapse`
- ⚠️ ยอดขาย POS รายวัน กับยอดขาย invoice-level เป็นคนละ population — ไม่บวก/เทียบกันตรง ๆ
