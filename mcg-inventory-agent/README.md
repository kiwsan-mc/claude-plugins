# MCG Inventory Agent

MC Group Inventory Analyst Agent plugin for Claude Code / Cowork.

ถามข้อมูลสินค้าคงคลัง (stock on hand, aging, PO, STO) ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน Synapse MCP tools.

> 📌 **ศัพท์ MCG:** การสั่งซื้อเข้า/PO = **"Sales In"** (skill `po-intake`) · ยอดขาย = **"Sales Out"** → ใช้ `mcg-sales-agent`

## Version

**v1.3.14** — ห้ามวงเล็บชื่อทางเทคนิค + กระทบยอดตัวเลขก่อนส่ง
- **v1.3.14**: เพิ่ม 2 กฎจากเคสจริงรอบล่าสุด: (1) 🚫 **ห้ามวงเล็บชื่อทางเทคนิคต่อท้ายคำธุรกิจ** — รูปแบบที่หลุดซ้ำ ๆ คือ "รุ่น-สี (ชื่อคอลัมน์)" / "Product Master (ชื่อตาราง)" ⇒ ห้ามวงเล็บคำที่ขึ้นต้น `ai.` หรือ snake_case ต่อท้ายคำธุรกิจ (2) 🧮 **กระทบยอดก่อนส่ง** — ผลรวมของแถวในตารางต้องเท่ากับยอดรวมที่เขียน ถ้าไม่ตรงให้หาสาเหตุ/ระบุขอบเขต/แก้ตัวเลข และห้ามสร้างกลุ่ม "อื่น ๆ" ที่ยอดเกินส่วนที่เหลือ (เคสจริง: ตารางรายแบรนด์บวกได้ 27,141 แต่ยอดที่เขียน 26,541)
- **v1.3.13**: ตัดชื่อคอลัมน์ออกจาก **ประโยคกฎ** 29 บรรทัดใน 14 ไฟล์ (เหลือไว้เฉพาะใน SQL/mapping ที่ต้องใช้เขียน query) เพราะโมเดลลอกคำจากประโยคกฎไปพิมพ์ในคำตอบ · และ `product-agent` สั่งห้ามถามกลับสำหรับ "มีกี่รุ่น"/"จำนวนรุ่น"/"กี่รุ่น" โดยตรง — ให้ตอบจำนวนรุ่น-สีทันที ถ้าจะถามให้ถามเรื่องขอบเขต (ทั้งระบบ vs กรองแบรนด์/หมวด) แทน
- **v1.3.12**: แก้ root cause ของการเปิดไส้ใน: **template footer ในไฟล์เองมีคำต้องห้าม** — ลบ "(Synapse)" ออกจาก footer ทุกจุด (12 จุดใน 5 ปลั๊กอิน) เพราะโมเดลลอกตาม template ของไฟล์ · และย้ายกฎ 🙈 ห้ามพิมพ์ชื่อตาราง/คอลัมน์/tool/SQL ขึ้นเป็น **ข้อแรกสุดของบล็อกกฎ** ในทุก skill (จากเดิมอยู่ข้อ 6) ให้ความสำคัญสูงสุด
- **v1.3.11**: เพิ่มการตีความตามที่ผู้ใช้เลือก: **ถามกลับเฉพาะเมื่อกำกวมจริง** — "มีกี่รุ่น"/"จำนวนรุ่น" (ระบุหน่วยแล้ว) ตอบเป็นรุ่น-สีได้เลย · ที่ต้องถามคือ "จำนวน/กี่/เท่าไหร่" ที่ไม่ระบุหน่วย หรือคำถามที่ขาดช่วงเวลา/มิติที่จำเป็น — ระบุตัวอย่างทั้งสองฝั่งไว้ในบล็อกกฎทุก skill
- **v1.3.10**: ประกาศ **`AskUserQuestion`** ใน frontmatter `tools:` ของทุก skill ที่มีรายการ tools อยู่แล้ว (34 ไฟล์) ตามที่ผู้ใช้เลือก — เพื่อให้เรียก tool ได้แน่นอนเมื่อต้องถามกลับ · ไฟล์ที่ไม่มี `tools:` (artifact-creator, email-digest, email-template, generate-srs) ไม่เติม key ใหม่ เพราะการสร้าง allowlist ขึ้นมาอาจตัด tool MCP อื่นของสกิลนั้น · แก้ frontmatter ที่พังจริง 2 ไฟล์: `sales-agent` (บรรทัด note หลุดเข้าไปใน description block จน YAML พัง — ย้ายไปไว้ในเนื้อไฟล์) และ `ms-excel` (description เป็นบรรทัดเดียวมี ": " ทำให้ YAML ไม่ผ่าน — เปลี่ยนเป็น folded block) ⇒ ตอนนี้ frontmatter ทั้ง 38 ไฟล์ parse ผ่านหมด
- **v1.3.9**: เปลี่ยนกฎ "ห้ามเปิดเผยภายใน" จากรายชื่อคำ (ซึ่งโมเดลลอกคำจากไฟล์มาพิมพ์เอง) เป็น **เกณฑ์จับคำ** — ห้ามคำที่ขึ้นต้น `ai.` · ลงท้าย `_synapse`/`_count`/`_key`/`_model`/`_color`/`_quantity` · ชื่อฟังก์ชัน SQL · snake_case · ชื่อ tool พร้อมเตือนให้ตรวจซ้ำก่อนส่ง (รวม Insight + footer) · เพิ่ม check นี้เข้า Final Validation ของทุกไฟล์แม่ (product/inventory/sales/crm/target + business-overview §7)
- **v1.3.8**: เพิ่มกฎ 🔢 **หน่วยต้องตรงประเภท** (SKU ≠ ชิ้น · รุ่น-สี ≠ ชิ้น — ห้ามเขียน "SKU 126,395 ชิ้น") และ **ตัวเลขที่นับได้ต้องเป็นค่าจริง (COUNT(DISTINCT)) ไม่ใช่ค่าประมาณ (APPROX_)** เพราะพบเคสจริงที่ตอบ 32,147 (ค่าประมาณ) ขณะที่ค่าจริงคือ 31,418 = คลาด 2.3% และคำตอบเดียวกันให้เลขไม่ตรงกันคนละรอบ · `product-agent` เพิ่มกฎสัดส่วน: ต้องใช้เศษและส่วนขอบเขตเดียวกัน (เคสจริง "MC = 53.8% ของทั้งหมด" มาจาก 17,291÷32,147 คนละขอบเขต ที่ถูกคือ 65% ในบรรดาที่ระบุแบรนด์)
- **v1.3.7**: เพิ่ม **รายการคำต้องห้าม** ในบล็อกกฎทุก skill — ห้ามปรากฏในคำตอบที่ผู้ใช้เห็นเด็ดขาด: `ai.dim_article` · `ai.fact_*` · `Article_Key` · `Article_Model` · `Article_Model_Color` · `item_code` · `model_color` · `sku_count` · `model_color_count` · ชื่อ tool/MCP · SQL พร้อมคำธุรกิจที่ให้ใช้แทน (จำนวน SKU / จำนวนรุ่น (รุ่น-สี) / จำนวนชิ้น · "ข้อมูลสินค้าในระบบ" · footer = แหล่งกว้าง + as-of) — เพราะ agent ยังพิมพ์ชื่อคอลัมน์ในตารางคำตอบแม้มีกฎห้ามแล้ว
- **v1.3.6**: เพิ่มบรรทัดบังคับในบล็อกกฎทุก skill: 🚫 ห้ามพิมพ์ชื่อตาราง/คอลัมน์/tool/SQL ในคำตอบที่ผู้ใช้เห็น **รวมทั้งกล่อง Insight และ Data Footer** · แก้ความขัดแย้ง "มีกี่รุ่น": คำว่า "รุ่น" = หน่วยที่ระบุแล้ว ⇒ ตอบเป็นรุ่น-สีได้เลย ไม่ต้องถามกลับ (ฝั่ง sales/pricing แก้ให้ตรงกับ product/inventory) · `stock-health` เพิ่มวลีนำทางจำนวน ("สต็อกมีกี่รุ่น-สี") · `assortment-summary` เตือนว่า "รวม" ของตาราง ≠ ยอดทั้ง master
- **v1.3.5**: เวลาถามกลับ/ยืนยันกับผู้ใช้ ให้เรียก tool **`AskUserQuestion`** เสมอ (ตัวเลือก 2–4 ข้อที่เลือกได้จริง · header สั้น + คำถามชัด) — 🚫 ห้ามพิมพ์คำถามลอย ๆ ในคำตอบ · ทั้ง 38 skill มีข้อกำหนดนี้ในบล็อกกฎ และไฟล์แม่ของแต่ละปลั๊กอินมีสเปกวิธีเรียก · ตัวอย่าง "ถาม: ..." ในไฟล์ = เนื้อหาที่ใส่ใน tool call
- **v1.3.4**: `stock-health` Step 2 ระบุ `model_color_count` = จำนวนรุ่น-สี (ใช้ตอบ "สต็อกมีกี่รุ่น-สี") และห้ามใช้ `sku_count` ตอบคำถามนั้น · ลบตัวอักษรจีนที่หลุด + ปรับข้อความตารางรายวันให้ตรงวันจริง
- **v1.3.3**: ย้ำกฎ **ห้ามเดาข้อมูลมาตอบ** (ใช้กับทุก runtime โดยเฉพาะ Claude Desktop / Cowork) ใน **ทุก skill** ของปลั๊กอิน — ทุกตัวเลข/ข้อเท็จจริงต้องมาจากผลการเรียก tool จริงในบทสนทนาและอ้างอิงกลับได้ · เรียกแล้วไม่พบข้อมูลให้ตอบว่า "ไม่พบข้อมูล" ตามจริง (แยกจาก 0) · ห้ามเดา/ประมาณ/แต่งตัวเลข/ตอบจากความจำของโมเดล
**v1.3.2** — กฎหน่วยจำนวน ("จำนวนรุ่น" = รุ่น-สี) + กฎ **"รับของเข้า → ตอบจำนวนชิ้น"**: ตอบ GR Qty เป็นตัวเลขหลัก ไม่ยกมูลค่าขึ้นนำ · `po-intake` ปรับ Headline/ตารางให้เป็นชิ้น + มีหน่วยทุกคอลัมน์ · tool ฝั่ง stock/PO/STO เพิ่ม `model_color_count` และเรียงตามจำนวนชิ้น

- **v1.3.1**: **ปลายทางโอน** เพิ่มขั้น **T3 (รุ่นเดียวกัน คนละสี)** ปิดช่องที่ตอบ "ไม่มีปลายทางโอน" ผิด ๆ (ตรวจ 2026-09-25: **17,212 คู่ / 310 รุ่น-สี** ที่ T1/T2 ว่างแต่ T3 เจอ) · ปลายทาง T3 ที่**ถือสีเดียวกันค้างอยู่จะถูกตัดออก** · เตือน **`Salesman_Employee_Code = 999999` ("OTHERS") ใช้ร่วม 1,070 สาขา** ⇒ "salesman เดียวกัน" ของกลุ่มนี้ไม่ใช่พื้นที่จริง ต้องกำกับ · **ห้ามเขียน query เองเพื่อกรองแคบกว่า tool** (เคสจริง: กรอง "ไม่เคยขาย ≥180 วัน" แล้วได้กลุ่มที่ไม่มีใครขายเลย ⇒ ตารางปลายทางว่างทั้งกระดาน) · ถ้าไม่มีปลายทางทั้ง T1–T3 **ต้องมีประโยค fallback (clearance / คืน vendor)** · ห้ามพิมพ์ชื่อตาราง/คอลัมน์ในคำตอบรวมทั้ง Data Footer
- **v1.3.0**: สต็อกมี **2 ฐาน** — default ของธุรกิจคือ**ฐานคงเหลือ** (`Stock_Quantity`) ตอบคู่กับ**ฐานรวมทั้งหมด** (`Stock_Total_*`) เสมอ · **"ของค้าง" นิยามใหม่ = ไม่มีขายที่ร้าน OFFLINE ≥30/60/90 วัน** (แยกจาก aging สี) และ **ต้องแนบตาราง Stock QTY by TOP 10 Model Color** ใน 3 คำถาม (ของค้างมีเยอะไหม / เงินจมในสต็อกเท่าไหร่ / ของค้างเกิน 6 เดือนมีไหม) · **PO ค้างส่ง = `Still_To_Delivery_*`** ไม่ใช่ `Open_Quantity` · เพิ่ม skill `po-analysis` (มุมรวม PO+STO) · แก้คำเตือน "ตารางรายวันล่าช้า" ซึ่งหมดจริงแล้ว (ข้อมูลถึง 2026-09-23)
- **v1.2.0**: ย้ายจาก `gold.script_stock_daily*` / `silver.sap_po` / `silver.sap_sto` ไป `ai.fact_MB52` / `ai.fact_sales_and_stock_daily` / `ai.fact_stock_month_ending` / `ai.fact_po_sto`; เพิ่มกฎต้อง filter `Item_Category` สำหรับ PO/STO
- **v1.1.0**: เพิ่ม freshness + validation rules
- **v1.0.0**: เริ่มต้น — inventory domain

## Skills

| Skill | Role | หน้าที่ |
|-------|------|---------|
| `inventory-agent` | Inventory Agent | กฎกลาง, tool priority, aging zones, snapshot rules (shared foundation) |
| `stock-health` | Stock Health Analyst | สต็อกคงเหลือปัจจุบันแยก aging/brand/region + สินค้าเสี่ยง clearance + ของค้าง/เงินจม + **ตารางบังคับ TOP 10 Model Color** |
| `stock-trend` | Inventory Planner | สต็อกย้อนหลัง time series + เปรียบเทียบช่วงเวลา |
| `po-intake` | Procurement Analyst | **Sales In** (PR/PO/GR/open qty) แยก vendor/สาขา + fulfillment — **PO เท่านั้น** |
| `sto-transfer` | Distribution Analyst | โอนย้ายสต็อกระหว่างสาขา + open transfer — **STO เท่านั้น** |
| `po-analysis` | Procurement & Transfer Analyst | **มุมรวม PO+STO** — ค้างส่ง, ตามรอบเวลา, Vendor Performance แยกชั้น PO/STO |

## Architecture

```
skills/
├── inventory-agent/    ← SKILL.md หลัก (rules, tool priority, aging, snapshot pinning)
├── stock-health/       ← #[[file:../inventory-agent/SKILL.md]] + role prompt
├── stock-trend/        ← #[[file:../inventory-agent/SKILL.md]] + role prompt
├── po-intake/          ← #[[file:../inventory-agent/SKILL.md]] + role prompt
├── sto-transfer/       ← #[[file:../inventory-agent/SKILL.md]] + role prompt
└── po-analysis/        ← #[[file:../inventory-agent/SKILL.md]] + role prompt (มุมรวม PO+STO)
```

แต่ละ skill ย่อย include กฎหลักผ่าน `#[[file:...]]` — แก้ที่เดียวมีผลทุก role.

## MCP Tools (Synapse — server: `synapse-inventory`)

| Tool | Description |
|------|-------------|
| `stock_on_hand_synapse` | สต็อกคงเหลือปัจจุบัน (auto-pin latest snapshot) แยก dimension |
| `stock_daily_trend_synapse` | สต็อกย้อนหลังตามช่วงเวลา |
| `po_summary_synapse` | Purchase Order (PR/PO/GR/open) |
| `sto_summary_synapse` | Stock Transfer Order |
| `stock_on_hand_yoy_synapse` | สต็อก YoY (snapshot ปัจจุบัน vs วันเดียวกันปีก่อน) |
| `po_summary_yoy_synapse` / `sto_summary_yoy_synapse` | PO / STO YoY (Apple-to-Apple) |
| `max_stock_date_synapse` / `max_po_date_synapse` | anchor date ของสต็อก / PO |
| `inventory_query_synapse` | Raw T-SQL (SELECT/WITH) — fallback |
| `describe_table_inventory_synapse` | Schema lookup |
| `search_columns_inventory_synapse` | Column search |

## Stock on Hand Measures (สต็อกคงเหลือ)

`stock_on_hand_synapse` และ `stock_value_by_aging_synapse` คืน 4 measure มาตรฐานนี้:

**⚠️ สต็อกมี 2 ฐาน (basis) — ตอบคู่กันเสมอ** (ดู §5.2 ของ inventory-agent)

| ฐาน | จำนวน | ต้นทุน MV | ต้นทุน STD | ราคาขาย |
|-----|--------|-----------|------------|---------|
| **คงเหลือ** ← default ของธุรกิจ | `Stock_Quantity` | `Stock_Amount` | `Stock_Amount_Standard` | คำนวณ `Selling_Price × Stock_Quantity` |
| **รวมทั้งหมด** | `Stock_Total_Quantity` | `Stock_Total_Amount` | `Stock_Total_Amount_Standard` | `Stock_Total_Selling_Price` |

> ✅ สมการที่พิสูจน์แล้ว: `Stock_Total_Quantity` = `Stock_Quantity` + `Intransit_Quantity` + `Blocked_Quantity` (2026-09-22: 4,949,274 + 83,413 + 7,706 = **5,040,393**)
>
> ⚠️ `stock_on_hand_synapse` / `stock_value_by_aging_synapse` คืน **ฐานรวมทั้งหมด** — ถ้า user ถาม "สต็อกคงเหลือ" ต้องดึงฐานคงเหลือด้วย `inventory_query_synapse` (ถ้าไม่ จะเกินจริง 91,119 ชิ้น / +1.84%)
>
> ⚠️ `Stock_Total_*` มีเฉพาะ `ai.fact_MB52` และ `ai.fact_stock_month_ending` — `ai.fact_sales_and_stock_daily` **ไม่มี** → trend/YoY ทำได้เฉพาะ**ฐานคงเหลือ** (`Stock_Quantity` + `Stock_Amount_Standard`) ซึ่งตรงกับ default พอดี
>
> ✅ `stock_on_hand_yoy_synapse` **ใช้ได้แล้ว** (ตรวจ 2026-09-24) — เคยคืน `qty_curr` = 0 ตอนตารางรายวันหยุดที่ 2026-08-13 แต่ถูกเติมครบถึง 2026-09-23 แล้ว

## Data Sources

- `ai.fact_MB52` — สต็อกคงเหลือ snapshot ล่าสุด (วันเดียว) — current on-hand
- `ai.fact_sales_and_stock_daily` — สต็อกย้อนหลัง + ยอดขายรายวัน (ต้องมี date range)
- `ai.fact_stock_month_ending` — สต็อกสิ้นเดือน (2022-01 … 2026-08)
- `ai.fact_po_sto` — Purchase Order + Stock Transfer Order รวมตารางเดียว → แยกด้วย `Item_Category` (PO = `<> '7'`, STO = `= '7'`)

> อัปเดต: ย้ายจาก `gold.script_stock_daily*` / `silver.sap_po` / `silver.sap_sto` มาเป็น schema `[ai]` แล้ว (ตารางเดิมยังอยู่แต่เลิกใช้)

## Usage

- "สต็อกคงเหลือแยก aging" → `stock-health`
- "แนวโน้มสต็อก 30 วันล่าสุด" → `stock-trend`
- "Sales In / PO ค้างส่งจาก vendor ไหนบ้าง" → `po-intake`
- "การโอนสต็อกระหว่างสาขาเดือนนี้" → `sto-transfer`
- "PO+STO ค้างส่งรวมเท่าไหร่" / "vendor performance ทั้ง PO และ STO" → `po-analysis`
