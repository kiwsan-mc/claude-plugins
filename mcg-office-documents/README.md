# MCG Office & Output Documents

MCG plugin รวมงาน **output / office automation** — สร้างไฟล์ Excel, สร้าง Dashboard เป็น Cowork Artifact, และจัดการอีเมล Outlook

## Version

**v2.0.8** — ถามกลับเฉพาะเมื่อกำกวมจริง
- **v2.0.8**: เพิ่มการตีความตามที่ผู้ใช้เลือก: **ถามกลับเฉพาะเมื่อกำกวมจริง** — "มีกี่รุ่น"/"จำนวนรุ่น" (ระบุหน่วยแล้ว) ตอบเป็นรุ่น-สีได้เลย · ที่ต้องถามคือ "จำนวน/กี่/เท่าไหร่" ที่ไม่ระบุหน่วย หรือคำถามที่ขาดช่วงเวลา/มิติที่จำเป็น — ระบุตัวอย่างทั้งสองฝั่งไว้ในบล็อกกฎทุก skill
- **v2.0.7**: ประกาศ **`AskUserQuestion`** ใน frontmatter `tools:` ของทุก skill ที่มีรายการ tools อยู่แล้ว (34 ไฟล์) ตามที่ผู้ใช้เลือก — เพื่อให้เรียก tool ได้แน่นอนเมื่อต้องถามกลับ · ไฟล์ที่ไม่มี `tools:` (artifact-creator, email-digest, email-template, generate-srs) ไม่เติม key ใหม่ เพราะการสร้าง allowlist ขึ้นมาอาจตัด tool MCP อื่นของสกิลนั้น · แก้ frontmatter ที่พังจริง 2 ไฟล์: `sales-agent` (บรรทัด note หลุดเข้าไปใน description block จน YAML พัง — ย้ายไปไว้ในเนื้อไฟล์) และ `ms-excel` (description เป็นบรรทัดเดียวมี ": " ทำให้ YAML ไม่ผ่าน — เปลี่ยนเป็น folded block) ⇒ ตอนนี้ frontmatter ทั้ง 38 ไฟล์ parse ผ่านหมด
- **v2.0.6**: เปลี่ยนกฎ "ห้ามเปิดเผยภายใน" จากรายชื่อคำ (ซึ่งโมเดลลอกคำจากไฟล์มาพิมพ์เอง) เป็น **เกณฑ์จับคำ** — ห้ามคำที่ขึ้นต้น `ai.` · ลงท้าย `_synapse`/`_count`/`_key`/`_model`/`_color`/`_quantity` · ชื่อฟังก์ชัน SQL · snake_case · ชื่อ tool พร้อมเตือนให้ตรวจซ้ำก่อนส่ง (รวม Insight + footer) · เพิ่ม check นี้เข้า Final Validation ของทุกไฟล์แม่ (product/inventory/sales/crm/target + business-overview §7)
- **v2.0.5**: เพิ่มกฎ 🔢 **หน่วยต้องตรงประเภท** (SKU ≠ ชิ้น · รุ่น-สี ≠ ชิ้น — ห้ามเขียน "SKU 126,395 ชิ้น") และ **ตัวเลขที่นับได้ต้องเป็นค่าจริง (COUNT(DISTINCT)) ไม่ใช่ค่าประมาณ (APPROX_)** เพราะพบเคสจริงที่ตอบ 32,147 (ค่าประมาณ) ขณะที่ค่าจริงคือ 31,418 = คลาด 2.3% และคำตอบเดียวกันให้เลขไม่ตรงกันคนละรอบ · `product-agent` เพิ่มกฎสัดส่วน: ต้องใช้เศษและส่วนขอบเขตเดียวกัน (เคสจริง "MC = 53.8% ของทั้งหมด" มาจาก 17,291÷32,147 คนละขอบเขต ที่ถูกคือ 65% ในบรรดาที่ระบุแบรนด์)
- **v2.0.4**: เพิ่ม **รายการคำต้องห้าม** ในบล็อกกฎทุก skill — ห้ามปรากฏในคำตอบที่ผู้ใช้เห็นเด็ดขาด: `ai.dim_article` · `ai.fact_*` · `Article_Key` · `Article_Model` · `Article_Model_Color` · `item_code` · `model_color` · `sku_count` · `model_color_count` · ชื่อ tool/MCP · SQL พร้อมคำธุรกิจที่ให้ใช้แทน (จำนวน SKU / จำนวนรุ่น (รุ่น-สี) / จำนวนชิ้น · "ข้อมูลสินค้าในระบบ" · footer = แหล่งกว้าง + as-of) — เพราะ agent ยังพิมพ์ชื่อคอลัมน์ในตารางคำตอบแม้มีกฎห้ามแล้ว
- **v2.0.3**: เพิ่มบรรทัดบังคับในบล็อกกฎทุก skill: 🚫 ห้ามพิมพ์ชื่อตาราง/คอลัมน์/tool/SQL ในคำตอบที่ผู้ใช้เห็น **รวมทั้งกล่อง Insight และ Data Footer** · แก้ความขัดแย้ง "มีกี่รุ่น": คำว่า "รุ่น" = หน่วยที่ระบุแล้ว ⇒ ตอบเป็นรุ่น-สีได้เลย ไม่ต้องถามกลับ (ฝั่ง sales/pricing แก้ให้ตรงกับ product/inventory) · `stock-health` เพิ่มวลีนำทางจำนวน ("สต็อกมีกี่รุ่น-สี") · `assortment-summary` เตือนว่า "รวม" ของตาราง ≠ ยอดทั้ง master
- **v2.0.2**: เวลาถามกลับ/ยืนยันกับผู้ใช้ ให้เรียก tool **`AskUserQuestion`** เสมอ (ตัวเลือก 2–4 ข้อที่เลือกได้จริง · header สั้น + คำถามชัด) — 🚫 ห้ามพิมพ์คำถามลอย ๆ ในคำตอบ · ทั้ง 38 skill มีข้อกำหนดนี้ในบล็อกกฎ และไฟล์แม่ของแต่ละปลั๊กอินมีสเปกวิธีเรียก · ตัวอย่าง "ถาม: ..." ในไฟล์ = เนื้อหาที่ใส่ใน tool call
- **v2.0.1**: ย้ำกฎ **ห้ามเดาข้อมูลมาตอบ** (ใช้กับทุก runtime โดยเฉพาะ Claude Desktop / Cowork) ใน **ทุก skill** ของปลั๊กอิน — ทุกตัวเลข/ข้อเท็จจริงต้องมาจากผลการเรียก tool จริงในบทสนทนาและอ้างอิงกลับได้ · เรียกแล้วไม่พบข้อมูลให้ตอบว่า "ไม่พบข้อมูล" ตามจริง (แยกจาก 0) · ห้ามเดา/ประมาณ/แต่งตัวเลข/ตอบจากความจำของโมเดล
(skill เหล่านี้ไม่เกี่ยวกับ DB/sales analytics จึงไม่ควรอยู่ใน sales agent)

- **v2.0.0**: ย้าย `artifact-creator`, `email-digest`, `email-template` จาก `mcg-sales-agent` เข้ามา
- **v1.1.0**: ms-excel (สูตร, Pivot, Chart, template)

## Skills

| Skill | Role | หน้าที่ | MCP ที่ต้องใช้ |
|-------|------|---------|----------------|
| `ms-excel` | Excel Automation | สร้างไฟล์ Excel จริง — สูตร, Pivot Table, Chart, AI Remarks, template | `ms-excel` (Excellm) |
| `artifact-creator` | Artifact Builder | สร้าง live/interactive HTML dashboard เป็น Cowork artifact (localStorage cache + Chart.js) | **sales toolbox** (ดู ⚠️ ด้านล่าง) |
| `email-digest` | Inbox Triage | สรุปอีเมลที่ยังไม่อ่าน จัดลำดับความสำคัญ + แนะนำการตอบ | `ms-outlook` |
| `email-template` | Email Template | HTML template มาตรฐาน MC Group (Tahoma / #2c3e50 header) สำหรับส่งรายงาน | `ms-outlook` |

## Architecture

```
skills/
├── ms-excel/            ← SKILL.md + references/ (workflow, formula, enterprise templates)
├── artifact-creator/    ← SKILL.md (804 บรรทัด — patterns + validation checklist)
├── email-digest/        ← SKILL.md
└── email-template/      ← SKILL.md
```

## ⚠️ MCP dependency ของ `artifact-creator`

`artifact-creator` **ไม่ใช่ office tool ล้วน** — มันสร้าง dashboard **จากข้อมูลยอดขาย MC Group**
จึงต้องเข้าถึง sales MCP tools (อ้าง `mcp__mcg-toolbox__sales_agent` ในเนื้อ skill และสั่งให้
"ใช้ mcg-sales-agent skills เพื่อดู KPI formula/threshold")

→ ถ้า plugin นี้ไม่ bind sales toolbox ไว้ artifact-creator จะสร้าง dashboard จากข้อมูลจริงไม่ได้
→ **ต้องตรวจ/เพิ่ม MCP server ของ sales toolbox ให้ plugin นี้** (หรือ repoint ให้ไปเรียก
`mcg-sales-agent` แทนการเรียก tool ตรง)

## Usage

- "สร้างไฟล์ Excel ..." / "ทำ Pivot / Chart" → `ms-excel`
- "สร้าง Dashboard เป็น Artifact" / "Live dashboard" / "HTML interactive" → `artifact-creator`
- "สรุปอีเมล" / "มีอะไรใน inbox" → `email-digest`
- "ส่งรายงานทางอีเมล" / "email report" → `email-template`

## ไม่อยู่ในขอบเขต

ยอดขาย/สต็อก/สินค้า/เป้า/member → ส่งไป domain agent
(`mcg-sales-agent` / `mcg-inventory-agent` / `mcg-product-agent` / `mcg-target-agent` / `mcg-crm-agent`)
