# MCG CRM Agent

MC Group CRM & Member Analyst Agent plugin for Claude Code / Cowork.

วิเคราะห์ลูกค้า/สมาชิก (member) รายตัว, การแบ่ง segment, ส่วนลดสมาชิก, การคืนสินค้า และ ticket/ATV ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน Synapse MCP tools บนตาราง `ai.poc_fact_sales_with_crm`

## Version

**v1.1.11** — ตัดชื่อคอลัมน์ออกจากประโยคกฎ + ห้ามถามกลับ "มีกี่รุ่น"
- **v1.1.11**: ตัดชื่อคอลัมน์ออกจาก **ประโยคกฎ** 29 บรรทัดใน 14 ไฟล์ (เหลือไว้เฉพาะใน SQL/mapping ที่ต้องใช้เขียน query) เพราะโมเดลลอกคำจากประโยคกฎไปพิมพ์ในคำตอบ · และ `product-agent` สั่งห้ามถามกลับสำหรับ "มีกี่รุ่น"/"จำนวนรุ่น"/"กี่รุ่น" โดยตรง — ให้ตอบจำนวนรุ่น-สีทันที ถ้าจะถามให้ถามเรื่องขอบเขต (ทั้งระบบ vs กรองแบรนด์/หมวด) แทน
- **v1.1.10**: แก้ root cause ของการเปิดไส้ใน: **template footer ในไฟล์เองมีคำต้องห้าม** — ลบ "(Synapse)" ออกจาก footer ทุกจุด (12 จุดใน 5 ปลั๊กอิน) เพราะโมเดลลอกตาม template ของไฟล์ · และย้ายกฎ 🙈 ห้ามพิมพ์ชื่อตาราง/คอลัมน์/tool/SQL ขึ้นเป็น **ข้อแรกสุดของบล็อกกฎ** ในทุก skill (จากเดิมอยู่ข้อ 6) ให้ความสำคัญสูงสุด
- **v1.1.9**: เพิ่มการตีความตามที่ผู้ใช้เลือก: **ถามกลับเฉพาะเมื่อกำกวมจริง** — "มีกี่รุ่น"/"จำนวนรุ่น" (ระบุหน่วยแล้ว) ตอบเป็นรุ่น-สีได้เลย · ที่ต้องถามคือ "จำนวน/กี่/เท่าไหร่" ที่ไม่ระบุหน่วย หรือคำถามที่ขาดช่วงเวลา/มิติที่จำเป็น — ระบุตัวอย่างทั้งสองฝั่งไว้ในบล็อกกฎทุก skill
- **v1.1.8**: ประกาศ **`AskUserQuestion`** ใน frontmatter `tools:` ของทุก skill ที่มีรายการ tools อยู่แล้ว (34 ไฟล์) ตามที่ผู้ใช้เลือก — เพื่อให้เรียก tool ได้แน่นอนเมื่อต้องถามกลับ · ไฟล์ที่ไม่มี `tools:` (artifact-creator, email-digest, email-template, generate-srs) ไม่เติม key ใหม่ เพราะการสร้าง allowlist ขึ้นมาอาจตัด tool MCP อื่นของสกิลนั้น · แก้ frontmatter ที่พังจริง 2 ไฟล์: `sales-agent` (บรรทัด note หลุดเข้าไปใน description block จน YAML พัง — ย้ายไปไว้ในเนื้อไฟล์) และ `ms-excel` (description เป็นบรรทัดเดียวมี ": " ทำให้ YAML ไม่ผ่าน — เปลี่ยนเป็น folded block) ⇒ ตอนนี้ frontmatter ทั้ง 38 ไฟล์ parse ผ่านหมด
- **v1.1.7**: เปลี่ยนกฎ "ห้ามเปิดเผยภายใน" จากรายชื่อคำ (ซึ่งโมเดลลอกคำจากไฟล์มาพิมพ์เอง) เป็น **เกณฑ์จับคำ** — ห้ามคำที่ขึ้นต้น `ai.` · ลงท้าย `_synapse`/`_count`/`_key`/`_model`/`_color`/`_quantity` · ชื่อฟังก์ชัน SQL · snake_case · ชื่อ tool พร้อมเตือนให้ตรวจซ้ำก่อนส่ง (รวม Insight + footer) · เพิ่ม check นี้เข้า Final Validation ของทุกไฟล์แม่ (product/inventory/sales/crm/target + business-overview §7)
- **v1.1.6**: เพิ่มกฎ 🔢 **หน่วยต้องตรงประเภท** (SKU ≠ ชิ้น · รุ่น-สี ≠ ชิ้น — ห้ามเขียน "SKU 126,395 ชิ้น") และ **ตัวเลขที่นับได้ต้องเป็นค่าจริง (COUNT(DISTINCT)) ไม่ใช่ค่าประมาณ (APPROX_)** เพราะพบเคสจริงที่ตอบ 32,147 (ค่าประมาณ) ขณะที่ค่าจริงคือ 31,418 = คลาด 2.3% และคำตอบเดียวกันให้เลขไม่ตรงกันคนละรอบ · `product-agent` เพิ่มกฎสัดส่วน: ต้องใช้เศษและส่วนขอบเขตเดียวกัน (เคสจริง "MC = 53.8% ของทั้งหมด" มาจาก 17,291÷32,147 คนละขอบเขต ที่ถูกคือ 65% ในบรรดาที่ระบุแบรนด์)
- **v1.1.5**: เพิ่ม **รายการคำต้องห้าม** ในบล็อกกฎทุก skill — ห้ามปรากฏในคำตอบที่ผู้ใช้เห็นเด็ดขาด: `ai.dim_article` · `ai.fact_*` · `Article_Key` · `Article_Model` · `Article_Model_Color` · `item_code` · `model_color` · `sku_count` · `model_color_count` · ชื่อ tool/MCP · SQL พร้อมคำธุรกิจที่ให้ใช้แทน (จำนวน SKU / จำนวนรุ่น (รุ่น-สี) / จำนวนชิ้น · "ข้อมูลสินค้าในระบบ" · footer = แหล่งกว้าง + as-of) — เพราะ agent ยังพิมพ์ชื่อคอลัมน์ในตารางคำตอบแม้มีกฎห้ามแล้ว
- **v1.1.4**: เพิ่มบรรทัดบังคับในบล็อกกฎทุก skill: 🚫 ห้ามพิมพ์ชื่อตาราง/คอลัมน์/tool/SQL ในคำตอบที่ผู้ใช้เห็น **รวมทั้งกล่อง Insight และ Data Footer** · แก้ความขัดแย้ง "มีกี่รุ่น": คำว่า "รุ่น" = หน่วยที่ระบุแล้ว ⇒ ตอบเป็นรุ่น-สีได้เลย ไม่ต้องถามกลับ (ฝั่ง sales/pricing แก้ให้ตรงกับ product/inventory) · `stock-health` เพิ่มวลีนำทางจำนวน ("สต็อกมีกี่รุ่น-สี") · `assortment-summary` เตือนว่า "รวม" ของตาราง ≠ ยอดทั้ง master
- **v1.1.3**: เวลาถามกลับ/ยืนยันกับผู้ใช้ ให้เรียก tool **`AskUserQuestion`** เสมอ (ตัวเลือก 2–4 ข้อที่เลือกได้จริง · header สั้น + คำถามชัด) — 🚫 ห้ามพิมพ์คำถามลอย ๆ ในคำตอบ · ทั้ง 38 skill มีข้อกำหนดนี้ในบล็อกกฎ และไฟล์แม่ของแต่ละปลั๊กอินมีสเปกวิธีเรียก · ตัวอย่าง "ถาม: ..." ในไฟล์ = เนื้อหาที่ใส่ใน tool call
- **v1.1.2**: ย้ำกฎ **ห้ามเดาข้อมูลมาตอบ** (ใช้กับทุก runtime โดยเฉพาะ Claude Desktop / Cowork) ใน **ทุก skill** ของปลั๊กอิน — ทุกตัวเลข/ข้อเท็จจริงต้องมาจากผลการเรียก tool จริงในบทสนทนาและอ้างอิงกลับได้ · เรียกแล้วไม่พบข้อมูลให้ตอบว่า "ไม่พบข้อมูล" ตามจริง (แยกจาก 0) · ห้ามเดา/ประมาณ/แต่งตัวเลข/ตอบจากความจำของโมเดล
- **v1.1.1**: กฎการนับจำนวน (รุ่น = รุ่น-สี · ถามกลับเมื่อไม่ระบุหน่วย · ระบุหน่วยทุกครั้ง) + เพิ่มสูตรนับ SKU/รุ่น-สี ใน §6 (ต้อง join `dim_article` บน `Article_Key`)
**v1.0.0** — เริ่มต้น: CRM/member domain แยกจาก sales (domain ใหม่)

## Skills

| Skill | Role | หน้าที่ |
|-------|------|---------|
| `crm-agent` | CRM & Member Agent | กฎกลาง, tool priority, anchor, caveats ข้อมูล (shared foundation) |
| `member-segmentation` | CRM Segmentation Analyst | member by channel/product, frequency segments, top members, demographic (tier/gender/generation) |
| `member-discount` | Member Benefits Analyst | ส่วนลดสมาชิก (CRM discount) + การคืนสินค้า (return analysis) |

## Architecture

```
skills/
├── crm-agent/            ← SKILL.md หลัก (rules, tool priority, anchor, caveats)
├── member-segmentation/  ← #[[file:../crm-agent/SKILL.md]] + role prompt
└── member-discount/      ← #[[file:../crm-agent/SKILL.md]] + role prompt
```

## MCP Tools (Synapse — server: `synapse-crm`)

| Tool | Description |
|------|-------------|
| `max_member_date_synapse` | Anchor: max Sold_Date + FY ranges (เรียกก่อนเสมอ) |
| `member_crm_schema_cheatsheet_synapse` | Schema ของ fact + dims (ก่อน raw query) |
| `member_kpi_overview_synapse` | KPI ภาพรวม: net sales, qty, tickets, members, ATV, CRM discount |
| `member_by_channel_synapse` | Member sales แยก channel / channel_text / branch |
| `member_by_product_synapse` | Member sales แยก category / brand / gender / aging / sales_type |
| `member_frequency_synapse` | Purchase-frequency segments (1 / 2-3 / 4-10 / 11+) |
| `member_top_members_synapse` | Top members (RFM) จัดอันดับตาม net sales |
| `member_discount_synapse` | CRM discount แยก discount_code / channel |
| `member_ticket_atv_synapse` | Ticket / ATV / UPT แยก channel / branch / month |
| `member_return_analysis_synapse` | การคืนสินค้า (return) + return rate |
| `member_by_demographic_synapse` | Member แยก tier / gender / generation (join silver CRM master) |
| `member_sales_agent_synapse` | Raw T-SQL (SELECT/WITH) — fallback |

## Data Source

- `ai.poc_fact_sales_with_crm` — grain `(Invoice_Code, Sequence_Item)` = 1 แถวต่อรายการขาย; มี `Member_Code` + `Invoice_Code` (ตารางเดียวใน [ai] ที่มี member identity + invoice key)
- joins: `ai.dim_article` (Article_Key), `ai.dim_branch` (Branch_Code), `silver.crm_member_profile` / `silver.crm_bigdata_member` (Member_Code — demographic)

## ข้อควรระวัง (ข้อมูล)

1. **ตารางคือยอดขายทั้งหมด (member + non-member)** — `Member_Code` เป็นค่าว่าง 86.7% ของแถว; member-attributed net sales ≈ 16.6% ของรวม → member vs non-member แยกได้จากตารางนี้
2. **Member penetration ต่างกันตาม channel** — OFFLINE (~64%) และ MCSHOP.COM (~62%) member-driven; TIKTOK/SHOPEE/LAZADA guest-driven (member แค่ ~4-9%) → วิเคราะห์ member ต้องแยก channel เสมอ
3. **ไม่มี YoY** — ตารางเริ่ม 2025-07-01 (ยังไม่มีปีก่อนครบ) → YoY ได้ตั้งแต่ 2026-07
4. **ไม่มี COGS** → ไม่มี margin%
5. ครอบคลุม ~88 สาขา (Bangkok + ecommerce) — ไม่ใช่ national
6. **คำถามรายคน** — รหัสลูกค้าเป็น exact identifier: `M2603-013482` ≠ `M2502-013482` → ห้ามใช้ LIKE/prefix match (จะได้ยอดของสมาชิกคนอื่นโดยไม่ error); รหัสรูปแบบ `M` + YYMM + `-` + เลข 6 หลัก

## Usage

- "ใครคือลูกค้าของเรา / สมาชิกซื้อบ่อยแค่ไหน" → `member-segmentation`
- "ส่วนลดสมาชิกเท่าไหร่ / คืนสินค้าเยอะไหม" → `member-discount`
- "ลูกค้า M2603-013482 มียอดซื้อเท่าไหร่" → `crm-agent` (สมาชิกรายคน — exact match รหัสลูกค้า)
