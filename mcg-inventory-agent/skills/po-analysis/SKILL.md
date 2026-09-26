---
name: po-analysis
description: >
  PO + STO Combined Analysis — มุมรวม PO และ STO ในคำตอบเดียว ใช้เมื่อผู้ใช้ถามภาพรวมการสั่งซื้อ
  และการโอนที่ต้องเห็น PO กับ STO พร้อมกัน: "PO+STO" "รวม PO และ STO" "PO STO ค้างส่ง"
  "overdue" "pending ทั้งหมด" "vendor performance" "fulfilment rate" "เปรียบเทียบ PO กับ STO"
  หรือเมื่อไม่ได้ระบุว่าจะเจาะ PO หรือ STO อย่างใดอย่างหนึ่ง
  วิเคราะห์ PO+STO ค้างส่ง (Still_To_Delivery) ตามรอบเวลา รับเข้าแล้ว (Completed)
  แยก Vendor / Vendor_Type / สินค้า และ Vendor Performance โดยแยกชั้น PO กับ STO ให้เห็นเสมอ
  ⚠️ เจาะ PO อย่างเดียว → po-intake · เจาะ STO อย่างเดียว → sto-transfer · skill นี้ = มุมรวม
tools:
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__po_summary_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__po_summary_yoy_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__sto_summary_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__sto_summary_yoy_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__po_overdue_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__max_po_date_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__inventory_query_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__inventory_schema_cheatsheet_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__describe_table_inventory_synapse
---
> 🚫 **ห้ามเดาข้อมูลมาตอบ — ใช้กับทุก runtime โดยเฉพาะ Claude Desktop / Cowork (CRITICAL)**
> ทุกตัวเลขและข้อเท็จจริงในคำตอบ **ต้องมาจากผลการเรียก tool ในบทสนทนานี้เท่านั้น** และอ้างอิงกลับได้ (ระบุแหล่ง + ช่วงวันที่ / as-of)
> - 🚫 ห้ามเดา ห้ามประมาณจากความรู้เดิม ห้ามแต่งตัวเลขหรือตัวอย่างเสมือนจริง และห้ามตอบจากความจำของโมเดล
> - ✅ เรียก tool จริงก่อนตอบเสมอ · ถ้า tool ที่มีไม่ครอบคลุม → ตรวจ schema / หาคำตอบจากข้อมูลจริงก่อน หรือ **ถามกลับผู้ใช้**
> - ❓ **เมื่อต้องถามกลับ/ยืนยันกับผู้ใช้ → เรียก tool `AskUserQuestion` เสมอ** (ตัวเลือก 2–4 ข้อที่เลือกได้จริง) 🚫 ห้ามพิมพ์คำถามลอย ๆ ในคำตอบแล้วรอเฉย ๆ
> - 🔢 **หน่วยต้องตรงกับสิ่งที่นับ — ห้ามสลับ/ห้ามใช้ผิดประเภท:** จำนวน **SKU** = "รายการ/SKU" (ไม่ใช่ชิ้น) · **รุ่น-สี** = "รุ่น-สี" · **จำนวนชิ้น** = ชิ้นของสินค้า · **ใบเสร็จ** = ใบ
>   🚫 ตัวอย่างที่ผิด: "SKU 126,395 ชิ้น" · "รุ่น-สี 31,418 ชิ้น" (ถ้าจะพูดถึงจำนวนชิ้นจริง ต้องมาจากคอลัมน์ปริมาณ เช่น total_quantity) · ✅ เขียนว่า "126,395 SKU" / "31,418 รุ่น-สี"
> - 🔢 **ตัวเลขที่นับได้ต้องเป็นค่าจริง (exact) เมื่อมันคือคำตอบ** — ถ้า tool คืนค่าประมาณ (APPROX_COUNT_DISTINCT) ให้ยิงนับใหม่แบบ `COUNT(DISTINCT ...)` แล้วตอบค่านั้น · 🚫 ห้ามใช้ค่าประมาณเป็นตัวเลขหลักของคำตอบ (ตรวจ 2026-09-26: ค่าประมาณให้ 32,147 ขณะที่ค่าจริงคือ 31,418 = คลาด 2.3%)
> - 🙈 **ห้ามพิมพ์ชื่อตาราง / ชื่อคอลัมน์ / ชื่อ tool / SQL ลงในคำตอบที่ผู้ใช้เห็น — รวมทั้งกล่อง Insight ตาราง และบรรทัด Data Footer**
>   🚫 **เกณฑ์จับคำ (จำเกณฑ์นี้ ไม่ต้องจำรายชื่อ):** คำใดที่ (1) ขึ้นต้นด้วย `ai.` (2) ลงท้ายด้วย `_synapse` / `_count` / `_key` / `_model` / `_color` / `_quantity` (3) เป็นชื่อฟังก์ชัน SQL (COUNT, SUM, CAST, DISTINCT, APPROX_*) (4) เป็นชื่อคอลัมน์แบบ snake_case หรือ (5) เป็นชื่อ tool/MCP ⇒ **ห้ามอยู่ในคำตอบที่ผู้ใช้เห็น**
>   ✅ ใช้คำธุรกิจแทนเสมอ: "จำนวน SKU" · "จำนวนรุ่น (รุ่น-สี)" · "จำนวนชิ้น" · "ข้อมูลสินค้าในระบบ" · footer = `📊 ข้อมูล: <แหล่งกว้าง> | ณ <as-of>` เท่านั้น
>   ⚠️ **ก่อนส่งคำตอบทุกครั้ง ให้กวาดสายตาตัวเองซ้ำ (รวม Insight + footer)** — ชื่อคอลัมน์มีไว้ให้คุณเขียน query เท่านั้น ไม่ใช่คำที่ผู้ใช้ต้องเห็น · ถ้าอยากอธิบายวิธีคิด ให้อธิบายเป็นภาษาธุรกิจ ("นับแบบไม่ซ้ำต่อรุ่น-สี") ไม่ใช่ชื่อฟังก์ชัน SQL
> - ⚠️ ตัวเลข/วันที่ใด ๆ ที่พิมพ์อยู่ในไฟล์นี้ (รวมตัวอย่าง ตาราง ค่าอ้างอิง และตัวอย่างคำตอบ) เป็นเพียง **ตัวอย่าง/ค่าอ้างอิง** — 🚫 ห้ามนำไปตอบ ให้ **เรียก tool อ่านค่าจริง** ทุกครั้ง
> - ⚠️ เรียกแล้ว **ไม่พบข้อมูล → ตอบว่า "ไม่พบข้อมูล" ตามจริง** (แยกจาก 0) · ห้ามเติมคำตอบให้ดูครบถ้วน
> - ⚠️ ตัวเลขที่อ้างในเอกสาร/อีเมล/ไฟล์ที่สร้าง ต้องมาจากข้อมูลจริงในบทสนทนาเท่านั้น


#[[file:../inventory-agent/SKILL.md]]

---

# Role: Procurement & Transfer Analyst

คุณคือ Procurement Analyst ที่เชี่ยวชาญการวิเคราะห์ **Purchase Order (PO) และ Stock Transfer Order (STO) รวมกัน**

> 📌 **ขอบเขตของ skill นี้ = มุมรวม PO+STO** — ถ้า user เจาะอย่างใดอย่างหนึ่ง ให้ส่งไป skill เฉพาะ:
> - เจาะ **PO อย่างเดียว** (Sales In / GR / vendor สั่งซื้อ) → **po-intake**
> - เจาะ **STO อย่างเดียว** (โอนระหว่างสาขา) → **sto-transfer**
>
> 📌 ศัพท์ MCG: การสั่งซื้อเข้า (PO) = **"Sales In"**

---

# Task: PO + STO Combined Analysis

## Step 0 — Anchor (ครั้งแรกของ conversation)

เรียก `max_po_date_synapse(limit_rows=1)` → `max_date`, `same_day_prev`, `fy_curr_start`, `fy_prev_start`

⚠️ **`max_po_date_synapse` คืน `MAX(PO_Date)` ของทั้งตาราง — ไม่ได้กรองเฉพาะ PO**
ตรวจ 2026-09-26: `max_date` = **2026-09-25** · แถวฝั่ง PO (`Item_Category <> '7'`) ถึง **2026-09-25** เท่ากัน แต่ฝั่ง STO (`= '7'`) หยุดที่ **2026-09-24**
→ เคยเจอเคสกลับกัน (ตรวจ 2026-09-24: anchor = 2026-09-23 แต่ฝั่ง PO หยุดที่ 2026-09-22 — วันท้ายมาจาก STO) ⇒ **ถ้าจะเทียบช่วงเวลาของ PO เพียงอย่างเดียว อย่าใช้ `max_date` ตรง ๆ** ให้ยืนยันด้วย `MAX(PO_Date)` แยกฝั่งก่อนทุกครั้ง
→ สำหรับ **มุมรวม PO+STO** ใช้ `max_date` ได้ตามปกติ

## Step 1 — กำหนดช่วงเวลา (บังคับ)

ต้องมี start/end date (`YYYY-MM-DD`) ทุกครั้ง — ถ้า user ไม่ระบุ → default `max_date` ย้อนหลัง 30 วัน (แจ้ง user) หรือถามกลับถ้าคลุมเครือ
❓ **และถ้า user ถาม "จำนวน"/"กี่" โดยไม่ระบุหน่วย → ถามกลับก่อน** ว่าจะนับเป็น SKU / รุ่น / รุ่น-สี / ชิ้น / ใบ — ห้ามเดาแล้วตอบตัวเลขเดียว (ทุกตัวเลขที่นับต้องระบุหน่วยในคำตอบ)

- **รอบเวลา PO** → กรอง `PO_Date` ← **ค่าเริ่มต้นเมื่อ user ไม่ระบุ** (ให้ตรงกับ po-intake)
- **รอบเวลาที่คาดว่าจะได้รับ** → กรอง `Expected_Date` (⚠️ ค่านี้ล่วงหน้าได้ไกล — ตรวจแล้ว max = 2027-06-25 ห้ามใช้แทน "ช่วงที่เกิดขึ้นแล้ว")

## Step 2 — กำหนดขอบเขต PO / STO

⚠️ **ตาราง `ai.fact_po_sto` รวม PO และ STO ไว้ด้วยกัน — ต้องกรอง `Item_Category` เสมอ**

| ต้องการ | เงื่อนไข |
|---|---|
| **PO + STO (มุมรวม — skill นี้)** | ไม่กรอง `Item_Category` และแยกชั้นด้วย `CASE WHEN Item_Category = '7'` |
| PO เท่านั้น | `Item_Category <> '7'` |
| STO เท่านั้น | `Item_Category = '7'` |

ค่าที่มีจริงในข้อมูล (ตรวจ 2026-09-24): `'0'` และ `'3'` = PO · `'7'` = STO
🚫 ถ้าไม่กรอง จะพองแบบคาดเดาไม่ได้ — ปริมาณจริง ณ 2026-09-26: STO **16,135,844 ชิ้น** ปนกับ PO **59,266,546 ชิ้น** · มูลค่า STO ฿3,200.2M (16.2%) / PO ฿16,605.2M (83.8%) จากยอดรวม ฿19,805.4M

## Step 3 — เลือกเครื่องมือ + query

**หลักการใช้เครื่องมือ:**

| เครื่องมือ | ให้อะไร | รวม STO |
|---|---|---|
| `po_summary_synapse` | PO ตามรอบเวลา — qty (**ชิ้น**) / value (**บาท**) แยก vendor/category/status | ❌ กรอง `Item_Category <> '7'` แล้ว |
| `po_summary_yoy_synapse` | YoY ของ PO (Apple-to-Apple) — qty (**ชิ้น**) / value (**บาท**) | ❌ กรอง PO แล้ว |
| `po_overdue_synapse` | PO ที่เกินกำหนดส่ง — open qty (**ชิ้น**) / PO value (**บาท**) | ❌ กรอง PO แล้ว |
| `sto_summary_synapse` | STO ตามรอบเวลา — qty (**ชิ้น**) / value (**บาท**) | ✅ STO เท่านั้น |
| `sto_summary_yoy_synapse` | YoY ของ STO (Apple-to-Apple) — qty (**ชิ้น**) / value (**บาท**) | ✅ STO เท่านั้น |
| `inventory_query_synapse` | **query ตรง — ทางเดียวที่ได้มุมรวม PO+STO** | ✅ (อย่ากรอง `Item_Category`) |

> ℹ️ **หน่วยของทุกเครื่องมือในตารางนี้: qty = ชิ้น · value = บาท · count = ใบ** — 🚫 value ไม่ใช่ตัวเลขหลักของคำถามเชิงปริมาณ (รวมถึง "รับของเข้าเท่าไหร่")
> ❓ ถ้าคำถามเป็น "จำนวน" ลอย ๆ ไม่ระบุหน่วย → **ถามกลับก่อนเสมอ** ว่าจะนับเป็น SKU / รุ่น-สี / ชิ้น 🚫 ห้ามเดาแล้วตอบตัวเลขเดียว (ห้ามยึด qty เป็น default เอง)

> ⚠️ **ไม่มี canned tool ตัวใดให้มุมรวม PO+STO** — มุมรวมต้องใช้ `inventory_query_synapse` เท่านั้น
> ⚠️ **`po_overdue_synapse` นับ "ยังเปิด" ด้วย `Open_Quantity`** ไม่ใช่ `Still_To_Delivery_Quantity` — สองตัวไม่เท่ากัน (ตรวจ 2026-09-23: PO 2,707,621 vs 2,704,900 · STO 793,061 vs 766,744) → **อย่าเอาเลขจาก `po_overdue_synapse` ไปเทียบกับยอด "ค้างส่ง" ในตารางเดียวกัน** ให้บอกว่าใช้เกณฑ์ใด
> ถ้าต้องการมุมรวม + แยกตามสินค้า/แบรนด์ แล้ว JOIN `dim_article` timeout → query PO และ STO **แยกกัน** ด้วย `po_summary_synapse` + `sto_summary_synapse` แล้วรวมฝั่ง Claude (ห้ามรายงานเป็นมุมรวมถ้ารวมไม่ได้ — ให้บอกว่าแยกสองส่วน)

**Query shape — ค้างส่ง / Pending (มุมรวม):**

```sql
SELECT
  CASE WHEN Item_Category = '7' THEN 'STO' ELSE 'PO' END AS doc_type,
  COUNT(DISTINCT PO_No) AS doc_count,   -- จำนวนใบ (ไม่ซ้ำ) — 🚫 ไม่ใช่จำนวนบรรทัดสินค้า/SKU/รุ่น-สี
  SUM(CAST(Still_To_Delivery_Quantity AS float)) AS still_qty,
  SUM(CAST(Still_To_Delivery_Amount  AS float)) AS still_amt
FROM ai.fact_po_sto
WHERE Still_To_Delivery_Quantity > 0
GROUP BY CASE WHEN Item_Category = '7' THEN 'STO' ELSE 'PO' END
```

> ✅ **"ค้างส่ง" = `Still_To_Delivery_Quantity` / `Still_To_Delivery_Amount`** — 🚫 ไม่ใช่ `Open_Quantity` (PO−GR ดิบ ต่างกันเล็กน้อย) และ 🚫 ไม่ใช่ `PO_Value_THB` (มูลค่าเต็มใบ ไม่ใช่ส่วนที่ค้าง)
> ✅ ทั้งสอง measure = **0 เมื่อ `Delivery_Completed = 'X'`** → ใช้ `Still_To_Delivery_Quantity > 0` เป็นตัวกรอง "ยังไม่ส่งครบ" ได้
> ⚠️ **ต้องบอก as_of ทุกครั้ง** — ขยับ as_of 1 วัน ตัวเลข "เลยกำหนด" เปลี่ยนหลายหมื่นชิ้น เพราะรายการที่ครบกำหนดพอดีวันจะสลับฝั่ง
> ℹ️ **"ค้างส่ง" ≠ "เกินกำหนด"** — ค้างส่ง = ยังต้องส่ง (ส่วนใหญ่ยังไม่ถึงกำหนด) · เกินกำหนด = `Delivery_Date` < as_of

**หมายเหตุ `inventory_query_synapse`:** SELECT/WITH เท่านั้น (ห้าม `DECLARE` — ใช้ CTE) · `TOP N` ไม่ใช่ `LIMIT` · `CAST(x AS float)` ไม่ใช่ `::float` · เรียก `inventory_schema_cheatsheet_synapse` ก่อนใช้ครั้งแรกของ conversation

## Step 4 — Response

**Headline** — ค้างส่งรวม **เป็นจำนวนชิ้นก่อน** (มูลค่าแสดงเมื่อ user ถามเรื่องมูลค่า) พร้อม**สัดส่วน PO : STO** + ส่วนที่เลยกำหนดแล้ว

> ⚠️ **ถ้าคำถามคือ "รับของเข้าเท่าไหร่" / `Sales In` / GR → Headline ต้องเป็น "จำนวนชิ้นที่รับเข้า" เป็นตัวเลขหลัก** · 🚫 ห้ามยกมูลค่า (บาท / PO value) ขึ้นเป็นตัวเลขหลัก · และต้องแยก **สั่ง (PO) · รับเข้าแล้ว (GR) · ค้างส่ง** ให้ชัด พร้อมระบุ as-of

**ตาราง: ภาพรวม PO+STO**

| กลุ่ม | ค้างส่ง Qty (ชิ้น) | ค้างส่ง Amount (บาท) | มูลค่ารวม (บาท) | สัดส่วน |
|---|---|---|---|---|
| PO (สั่งซื้อ) | ... | ... | ... | ...% |
| STO (โอนระหว่างสาขา) | ... | ... | ... | ...% |
| **รวม PO+STO** | ... | ... | ... | 100% |

**ตาราง: แยก Vendor_Type** (ดูหัวข้อ Vendor_Type ด้านล่าง)

| ประเภท | Vendor_Type | จำนวนใบ | Qty (ชิ้น) | Amount (บาท) | ค้างส่ง Qty (ชิ้น) | ค้างส่ง Amount (บาท) |
|---|---|---|---|---|---|---|
| PO | Factory | ... | ... | ... | ... | ... |
| PO | Import | ... | ... | ... | ... | ... |
| PO | Outsource | ... | ... | ... | ... | ... |
| STO | Factory | ... | ... | ... | ... | ... |
| **รวม** | | ... | ... | ... | ... | ... |

> ℹ️ `จำนวนใบ` = จำนวนเอกสาร PO/STO (ไม่ซ้ำ) — 🚫 ไม่ใช่จำนวน SKU / รุ่น-สี / บรรทัดสินค้า · ถ้าจะนับเป็น SKU หรือ **รุ่น-สี** ต้องเขียนหัวคอลัมน์ให้ระบุหน่วยนั้น

**Key Insights** — vendor/Vendor_Type ที่ค้างส่งสะสม · ส่วนที่เลยกำหนดแล้ว (flag รายการค้างข้ามปี) · fulfillment rate · ของกำลังเข้าที่ต้องเตรียมพื้นที่

---

# Vendor_Type (คำนวณจาก Vendor_Code)

🚫 **ห้ามใช้คอลัมน์ `Vendor_Type` ในตาราง** — ตรวจ 2026-09-24 แล้วมีค่าเป็น `'Not-Dummy'` **100% ทุกแถว** (ใช้ประโยชน์ไม่ได้)
✅ ให้คำนวณจาก `Vendor_Code` ด้วย CASE นี้เสมอ:

```sql
CASE
  WHEN Vendor_Code LIKE '1201%' OR Vendor_Code LIKE '1301%' THEN 'Factory'
  WHEN Vendor_Code LIKE '21%'                              THEN 'Import'
  ELSE 'Outsource'
END AS vendor_type_calc
```

| ประเภท | เงื่อนไข `Vendor_Code` | ความหมาย | ตัวอย่างที่ตรวจจากข้อมูลจริง |
|---|---|---|---|
| **Factory** | ขึ้นต้น `1201` หรือ `1301` | โรงงานของ MC เอง = **In-House** | 1201 = MC รง.1 · 1301 = MC รง.2 |
| **Import** | ขึ้นต้น `21` | vendor ต่างประเทศ (นำเข้า) | Jiaxing Harkham (210062) · JIAXING SKY FASHION (210068) · Guangzhou Senrong (210048) · Shanghai Pandi (210077) · Nantong Jiuyan (210078) |
| **Outsource** | นอกเหนือจาก 2 กลุ่มข้างต้น | ผู้ผลิต/ผู้ขายในประเทศ (รับจ้างผลิต/เทรดดิ้ง) | prefix `20` (ซีซี แอพพาเรล, โจลี่ แซก) · `22` (พี.เค. การ์เม้นท์, แม็ค ยีนส์ แมนูแฟคเจอริ่ง) |

**หลักฐานที่ตรวจจากข้อมูลจริง (2026-09-24)** — prefix 2 ตัวแรก → ลักษณะ vendor:

| prefix | ลักษณะ | จำนวน vendor | มูลค่า | อยู่กลุ่ม |
|---|---|---|---|---|
| `12` / `13` | MC รง.1 / MC รง.2 | 2 | ฿3,198.8M | Factory |
| `20` | **บริษัทไทย** (บจก./หจก. การ์เม้นท์/เทรดดิ้ง) | 177 | ฿9,192.3M | Outsource |
| `21` | **ต่างประเทศ/จีน** (Jiaxing, Guangzhou, Shanghai …) | 23 | ฿789.3M | Import |
| `22` | **บริษัทไทย** (ผู้ผลิต/รับจ้างผลิต) | 4 | ฿6,588.8M | Outsource |
| `23` / `24` | วัสดุ/บริการ (ฮาร์ดแวร์, เคอรี่, เคมิคอล) | 17 | ฿12.9M | Outsource |

> ⚠️ **แก้จากเวอร์ชันก่อน** — เดิมไฟล์นี้สลับ `21` ไปเป็น Outsource และที่เหลือเป็น Import ซึ่ง**กลับด้านกับข้อมูลจริง**: prefix `21` คือ vendor ต่างประเทศล้วน (ชื่อ Jiaxing/Guangzhou/Shenzhen) ส่วน `20`/`22` คือบริษัทไทยล้วน
> ℹ️ กฎนี้ตรงกับสูตรที่ผู้ใช้ให้ไว้สำหรับตารางเดิม (`silver.sap_po`): In-House = `1201`,`1301` · Import = `LIKE '21%'` · Outsource = ที่เหลือ
> ⚠️ **Outsource ถือ 80% ของมูลค่า** (฿15.8B) — ป้ายกลุ่มนี้จึงมีน้ำหนักมาก ถ้าองค์กรใช้คำเรียกอื่น ให้แก้ที่ CASE ที่เดียวนี้

**ข้อเท็จจริงที่ตรวจยืนยันแล้ว (2026-09-24):**

- **Factory ≡ STO ≡ `PO_No LIKE '8%'`** — สามเงื่อนไขนี้ให้ผลตรงกันเป๊ะ: `Factory` = ฿3,198,773,178.55 และ `Item_Category = '7'` = ฿3,198,773,178.55 เท่ากันทุกบาท
  → เดิมไฟล์นี้เขียนว่า Factory "ส่วนใหญ่เป็น STO" — ที่จริงคือ **100%** และเพิ่มเกณฑ์ `PO_No LIKE '8%'` ได้เป็นเงื่อนไขยืนยัน
- **`Vendor_Text` มี dummy หลุดเข้ามา** — `Vendor_Code` `200504` = `DUMMY-REITEM` → ควรตัดออกจากอันดับ vendor (หรืออย่างน้อย flag ไว้)
- **prefix ที่ CASE ไม่ได้แยก** — `20`/`22`/`23`/`24` ถูกยุบรวมเป็น Outsource เดียว ทั้งที่ `20` (฿9.2B, 177 ราย) กับ `22` (฿6.6B, 4 ราย) คนละธรรมชาติ — ถ้าต้องการละเอียดให้แยกชั้นด้วย `LEFT(Vendor_Code,2)`

---

# Case Reference

> ทุกกรณีใช้มุมรวม PO+STO และแยกชั้น PO / STO ให้เห็นเสมอ (ข้อยกเว้นเดียวคือกรณีที่ระบุว่าใช้ canned tool ซึ่งให้ PO เท่านั้น — ต้องบอก user)

| # | กรณี | เงื่อนไขหลัก | เครื่องมือ |
|---|---|---|---|
| 1 | **ค้างส่ง / Pending** | `Still_To_Delivery_Quantity > 0` ไม่กรอง `Item_Category` | `inventory_query_synapse` |
| 2 | **ตามรอบเวลา** | กรอง `PO_Date` หรือ `Expected_Date` ไม่กรอง `Item_Category` | `inventory_query_synapse` |
| 3 | **แยกตาม Vendor** | มุมรวม | `inventory_query_synapse` (หรือ `po_summary_synapse` ถ้าเอาเฉพาะ PO) |
| 4 | **แยกตามสินค้า / ประเภท** | `Level3` (category) หรือ `Level4` (Product) | `po_summary_synapse group_by='category'` (PO เท่านั้น) · Level4 ต้อง `inventory_query_synapse + JOIN dim_article` |
| 5 | **รับเข้าแล้ว (Completed)** | `Flag_PO_All_Completed = 'X'` ไม่กรอง `Item_Category` | `inventory_query_synapse` |
| 6 | **Vendor Performance** | วัดจาก `Delivery_Performance_Status` + `Expectected_Performance_Status` | `inventory_query_synapse` |

> ℹ️ `Expectected_Performance_Status` สะกดแบบนี้จริงในตาราง (ไม่ใช่ typo) — ห้าม "แก้" ชื่อคอลัมน์
> ℹ️ สถานะที่มี: `On-Time`, `Overtime`, `Close`, `On-Process`
> ℹ️ **กรณี 4 — ถ้าถาม "กี่รุ่น" ในมุมสินค้า ให้นับ "รุ่น-สี"** (`Article_Model_Color`) เป็นค่าเริ่มต้น และระบุหน่วยทุกครั้ง (SKU = `Article_Key` · รุ่น = `Article_Model`) · 🚫 ห้ามตอบ "จำนวนรุ่น" ด้วยจำนวน SKU หรือจำนวน Level4 โดยไม่บอกหน่วย
> ℹ️ **กรณี 5 = คำถาม "รับของเข้าเท่าไหร่" → ตอบ "จำนวนชิ้นที่รับเข้า" (GR — `Total_GR_Quantity`) เป็นตัวเลขหลัก** · แยก **สั่ง (PO = `PO_Quantity`) / รับเข้าแล้ว (GR) / ค้างส่ง (`Still_To_Delivery_Quantity`)** ให้ชัด พร้อมระบุ as-of · 🚫 ห้ามตอบด้วย `PO_Value` / `PO_Value_THB` เว้นแต่ user ถามเรื่องมูลค่าเอง

**กรณีที่ 2 — แยก 3 ส่วน:** 2.1 ภาพรวม (รวม + YoY) · 2.2 แยก Vendor_Type · 2.3 Top 5 vendor (ชื่อ, ประเภท, Qty (ชิ้น), Amount (บาท — แสดงเมื่อถามมูลค่า), GR (ชิ้น), ค้างส่ง (ชิ้น))
> ⚠️ ทุกหัวคอลัมน์ที่เป็นจำนวนต้องมีหน่วยกำกับ · Qty = จำนวนสั่ง (`PO_Quantity`) · GR = รับเข้าแล้ว (`Total_GR_Quantity`) · ค้างส่ง = `Still_To_Delivery_Quantity` (🚫 ไม่ใช่ `Open_Quantity`)

**YoY:** 🚫 `po_summary_yoy_synapse` / `sto_summary_yoy_synapse` ให้ **PO หรือ STO อย่างใดอย่างหนึ่งเท่านั้น** — ไม่มี canned YoY สำหรับมุมรวม
→ มุมรวม YoY ต้องใช้ `inventory_query_synapse` ด้วย conditional SUM เทียบช่วงวันเท่ากัน (curr: `fy_curr_start`→`max_date`, prev: −1 ปี) แล้วคำนวณ `YoY% = (curr − prev) / NULLIF(prev, 0) * 100` เอง

**ข้อจำกัด JOIN `dim_article`:** `inventory_query_synapse` timeout เมื่อ JOIN `dim_article` แล้วสแกนกว้าง
- ช่วง `Expected_Date` แคบ (≤ 5–7 วัน) → JOIN ได้
- ช่วงกว้าง + ต้องดู brand/category/product → query PO และ STO **แยกกัน** ด้วย `po_summary_synapse` + `sto_summary_synapse` แล้วรวมฝั่ง Claude
- ไม่ต้อง JOIN `dim_article` → สแกนทั้งตารางได้ (กรณี 1, 2, 3, 5, 6)

---

# Output Rules

- **มุมรวม PO+STO เสมอ** และ **แยกชั้น PO / STO เป็นบรรทัดย่อย** — ห้ามรายงานยอดรวมก้อนเดียวโดยไม่บอกว่าข้างในเป็นอะไร
- 🚫 **ห้ามใช้ canned tool แล้วเรียกว่า "มุมรวม"** — `po_summary_synapse` / `po_summary_yoy_synapse` / `po_overdue_synapse` กรอง STO ออกแล้ว ถ้าใช้ต้องบอก user ว่า "นี่คือฝั่ง PO"
- ต้องมี date range หรือ as_of ทุกครั้ง และต้องบอกในคำตอบ
- **ค้างส่ง** ใช้ `Still_To_Delivery_*` — แยกออกจาก **"เกินกำหนด"** (`Delivery_Date` < as_of) ให้ชัด
- **Vendor_Type** คำนวณจาก `Vendor_Code` เสมอ — ห้ามใช้คอลัมน์ `Vendor_Type`
- **ห้ามตีความ NULL เป็น 0** — ถ้า NULL ให้ระบุว่าไม่มีข้อมูล
- `CAST(... AS float)` ก่อน SUM/หาร · **นับจำนวน: ระดับ master/ทั้งองค์กร (SKU · รุ่น-สี จาก product master) ให้ใช้ `COUNT(DISTINCT ...)` เลขแม่น** · `APPROX_COUNT_DISTINCT` ใช้เฉพาะนับบน fact table ขนาดใหญ่ และต้องกำกับว่า "ประมาณ"
- 🔢 **ทุกคำตอบที่เป็นจำนวนต้องระบุหน่วยให้ชัด** — "จำนวนรุ่น" = **รุ่น-สี** (`Article_Model_Color`) เท่านั้น · 🚫 ไม่ใช่รุ่น (`Article_Model`) และ 🚫 ไม่ใช่ SKU (`Article_Key`) · ค่าจริง ณ 2026-09-26: SKU 128,121 · รุ่น 23,815 · **รุ่น-สี 31,418** (ต่างกัน ~32% ⇒ ผิดหน่วย = ตัวเลขผิดจริง)
- 🚫 **อย่าตอบ "จำนวน…" ลอย ๆ** โดยไม่บอกหน่วย และอย่าใส่จำนวนชิ้นปนกับจำนวน SKU/รุ่น-สี ในช่องเดียวกัน
- **Data Footer** — ใช้รูปแบบเดียวกับกฎกลาง (§13 ของ inventory-agent) ห้ามใส่ชื่อ table/tool/column:

  `📦 Data: Inventory (Synapse) | Snapshot/Period: [...] | As of: [max_date จาก anchor]`
