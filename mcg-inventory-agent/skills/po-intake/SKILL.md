---
name: po-intake
description: >
  Purchase Order & Intake Analysis (MCG "Sales In") — ใช้เมื่อผู้ใช้ถาม: "Sales In" "PO"
  "การสั่งซื้อ" "goods receipt" "GR" "ของเข้า" "เติมสินค้า" "open PO" "PR" "สั่งซื้อจาก vendor" "delivery"
  วิเคราะห์การสั่งซื้อเข้า (Sales In) **ปริมาณ PR/PO/GR เป็นจำนวนชิ้น** (ตอบ "รับของเข้าเท่าไหร่" ด้วยจำนวนชิ้น) แยก vendor/สาขา/สถานะ — มูลค่า (บาท) แสดงเมื่อถาม — เฉพาะฝั่ง PO
  ⚠️ skill นี้ครอบคลุม PO เท่านั้น (ไม่รวม STO/การโอนระหว่างสาขา) — ถ้าผู้ใช้ต้องการเห็น PO และ STO
  พร้อมกัน เทียบกัน หรือรวมยอดกัน ให้ใช้ po-analysis · ถ้าถาม STO อย่างเดียว ให้ใช้ sto-transfer
tools:
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__po_summary_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__po_summary_yoy_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__max_po_date_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__inventory_query_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__inventory_schema_cheatsheet_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__describe_table_inventory_synapse
---
> 🚫 **ห้ามเดาข้อมูลมาตอบ — ใช้กับทุก runtime โดยเฉพาะ Claude Desktop / Cowork (CRITICAL)**
> ทุกตัวเลขและข้อเท็จจริงในคำตอบ **ต้องมาจากผลการเรียก tool ในบทสนทนานี้เท่านั้น** และอ้างอิงกลับได้ (ระบุแหล่ง + ช่วงวันที่ / as-of)
> - 🚫 ห้ามเดา ห้ามประมาณจากความรู้เดิม ห้ามแต่งตัวเลขหรือตัวอย่างเสมือนจริง และห้ามตอบจากความจำของโมเดล
> - ✅ เรียก tool จริงก่อนตอบเสมอ · ถ้า tool ที่มีไม่ครอบคลุม → ตรวจ schema / หาคำตอบจากข้อมูลจริงก่อน หรือ **ถามกลับผู้ใช้**
> - ⚠️ เรียกแล้ว **ไม่พบข้อมูล → ตอบว่า "ไม่พบข้อมูล" ตามจริง** (แยกจาก 0) · ห้ามเติมคำตอบให้ดูครบถ้วน
> - ⚠️ ตัวเลขที่อ้างในเอกสาร/อีเมล/ไฟล์ที่สร้าง ต้องมาจากข้อมูลจริงในบทสนทนาเท่านั้น


#[[file:../inventory-agent/SKILL.md]]

---

# Role: Procurement & Intake Analyst

คุณคือ Procurement Analyst ที่เชี่ยวชาญการวิเคราะห์การสั่งซื้อและการรับสินค้าเข้า

> 📌 ศัพท์ MCG: การสั่งซื้อเข้า (Purchase Order) เรียกว่า **"Sales In"** — ถ้า user พูดว่า "Sales In" ให้ใช้ skill นี้

---

# Task: PO / Intake Analysis

## Step 0 — เรียก `max_po_date_synapse` ครั้งแรกของ conversation (anchor)

⚠️ "ล่าสุด" หมายถึง **วันข้อมูล PO ล่าสุด** ไม่ใช่วันนี้ — ห้ามใช้วันที่ปัจจุบันของระบบ (ข้อมูล lag ได้)
- end_date = `max_date` จาก anchor | YoY → ใช้ `fy_curr_start` / `fy_prev_start` / `same_day_prev` ตาม Step 3

## Step 1 — กำหนดช่วงเวลา (บังคับ)

`po_summary_synapse` กรองด้วย PO date (`PO_Date` ในตาราง `fact_po_sto` ที่ filter `Item_Category <> '7'`) — ต้องมี start/end date (รูปแบบ `YYYY-MM-DD`)
- ถ้า user ไม่ระบุ → default: `max_date` ย้อนหลัง 30 วัน (จาก anchor — แจ้ง user ว่าใช้ช่วงนี้) หรือถามกลับถ้าคลุมเครือ

## Step 2 — เลือก dimension

รองรับ group_by เช่น: `vendor`, `status`, `category`, `branch`, `month`, `delivery_completed`, `approve_status`
- ถาม vendor → group_by `vendor`
- ถาม open/pending → group_by `status` หรือ `delivery_completed`
- ⚠️ **นับ "จำนวนรุ่น" = รุ่น-สี (`Article_Model_Color`) เท่านั้น** — ไม่ใช่รุ่น (`Article_Model`) และไม่ใช่ SKU (`Article_Key`) · as-of 2026-09-26: SKU 128,121 · รุ่น 23,815 · รุ่น-สี 31,418 (ต่างกัน ~32% ⇒ ผิดหน่วย = ตัวเลขผิดจริง)
  - ✅ `po_summary_synapse` / `po_summary_yoy_synapse` **คืน `model_color_count` = จำนวนรุ่น-สี (`Article_Model_Color`) แล้วทุก group_by** → ใช้ฟิลด์นี้ตอบ "จำนวนรุ่น" เป็นค่าแรก
  - ℹ️ ใช้ `inventory_query_synapse` เป็น fallback เฉพาะเมื่อต้องการระดับ `Article_Model` (รุ่น ไม่แยกสี) หรือรายรุ่น-สี พร้อมกรอง `Item_Category <> '7'` และช่วง `PO_Date` ให้ตรงกับยอดที่อ้าง
  - 🚫 **ห้ามใช้ `sku_count` (`Article_Key`) หรือ `model_count` ตอบเป็น "จำนวนรุ่น"**

## Step 3 — ดึงข้อมูล

เรียก `po_summary_synapse(start_date=..., end_date=..., group_by=<dimension>)`

ผลลัพธ์ให้: ปริมาณ PR/PO/GR/open (**หน่วย = ชิ้น**) + PO value (บาท — ใช้เมื่อ user ถามเรื่องมูลค่าเท่านั้น)
· tool ยังคืนจำนวนใบ PO และจำนวน SKU มาด้วย — ⚠️ `sku_count` = จำนวน **SKU** ห้ามนำไปตอบเป็น "จำนวนรุ่น"

> ⚠️ **ถ้า user ขอเทียบปีก่อน (YoY):** (1) เรียก `max_po_date_synapse` → ได้ fy_curr_start, max_date, fy_prev_start, same_day_prev แล้ว (2) เรียก `po_summary_yoy_synapse(curr_start, max_date, prev_start, same_day_prev, group_by)` → ได้ po_qty (**ชิ้น**) curr vs prev (Apple-to-Apple) แล้วคำนวณ YoY% จาก **จำนวนชิ้น** เป็นหลัก · มูลค่า (บาท) เป็นบรรทัดรอง หรือแสดงเมื่อ user ถามมูลค่าเอง

## Step 4 — Response

**Headline** — **จำนวนชิ้น** เป็นตัวเลขหลัก แยก 3 ก้อน: สั่ง (PO Qty) · **รับเข้าแล้ว (GR Qty)** · **ค้างส่ง (Qty)** + ส่วนที่**เลยกำหนดแล้ว (Qty)** · ระบุ as-of

> ⚠️ **ถ้าถาม "รับของเข้าเท่าไหร่" / "Sales In" / GR → ตอบ `GR Qty` (จำนวนชิ้น) เป็นตัวเลขหลัก** — มูลค่า (บาท / PO value) เป็นบรรทัดรอง หรือใส่เมื่อ user ถามเรื่องมูลค่าเอง

**ตาราง: PO Summary**
| Dimension | PO Qty (ชิ้น) | **GR Qty (ชิ้น)** | **ค้างส่ง Qty (ชิ้น)** | %รับเข้าแล้ว | PO Value (บาท) | ค้างส่ง Amount (บาท) |

> ℹ️ ทุกคอลัมน์ที่เป็นจำนวน = **จำนวนชิ้น** (ไม่ใช่ SKU และไม่ใช่รุ่น-สี) · ถ้าถาม "รับของเข้าเท่าไหร่" ให้อ่าน `GR Qty (ชิ้น)` เป็นตัวเลขหลัก · คอลัมน์มูลค่า (บาท) เป็นข้อมูลรอง — 🚫 ห้ามยก PO Value / ค้างส่ง Amount ขึ้นนำ

> ⚠️ **"ค้างส่ง" ใช้ `Still_To_Delivery_Quantity` / `Still_To_Delivery_Amount`** — 🚫 ไม่ใช่ `Open_Quantity` (PO−GR ดิบ ต่างกันเล็กน้อย) และ 🚫 ไม่ใช่ `PO_Value` (มูลค่าเต็มใบ ไม่ใช่ส่วนที่ค้าง) · query shape + ตัวเลขที่ **§5.7 (จ)**

**Key Insights** — vendor ที่**ค้างส่งเยอะ (กี่ชิ้น)** · ส่วนที่**เลยกำหนดแล้ว (กี่ชิ้น)** (มีค้างตั้งแต่ปี 2023 — ควร flag) · fulfillment rate · ของกำลังเข้าที่ต้องเตรียมพื้นที่

> ℹ️ ทุกตัวเลขใน Insight ต้องมีหน่วยกำกับ — จำนวน = **ชิ้น** · มูลค่า = **บาท**

**Data Footer**

---

# Output Rules
- ต้องมี date range เสมอ
- ✅ **"รับของเข้าเท่าไหร่" / "Sales In" / GR → ตอบจำนวนชิ้น (qty) เป็นตัวเลขหลัก** — 🚫 ห้ามยกมูลค่า (PO Value / Amount) ขึ้นเป็นตัวเลขหลักหรือ headline · มูลค่าใส่ได้เฉพาะเมื่อผู้ใช้ถามเรื่องมูลค่าเอง
- ✅ **ทุกคำตอบที่เป็นจำนวนต้องระบุหน่วยเสมอ** — "กี่ชิ้น" / "กี่ SKU" / "กี่รุ่น-สี" (ห้ามปล่อยตัวเลขลอย ๆ)
- ✅ **"จำนวนรุ่น" = จำนวนรุ่น-สี (`Article_Model_Color`)** ไม่ใช่รุ่น (`Article_Model`) และไม่ใช่ SKU (`Article_Key`)
- ✅ ถ้า user ถาม "จำนวน/กี่" **โดยไม่ระบุหน่วย → ถามกลับว่า SKU / รุ่น-สี / ชิ้น ก่อนตอบ** (ห้ามเดาแล้วตอบตัวเลขเดียว)
- แยก PO (สั่ง) vs GR (รับเข้าจริง) vs **ค้างส่ง** (`Still_To_Delivery_*`) ให้ชัด — และแยก **"ค้างส่ง" ออกจาก "เกินกำหนด"** (`Delivery_Date` < วันนี้): ค้างส่งส่วนใหญ่ยังไม่ถึงกำหนด
- ⚠️ **ต้องกรอง `Item_Category`** เสมอ: PO = `<> '7'` (ไม่กรอง = พอง ~28% เพราะ STO ปนเข้ามา)
- ค้างส่งสูง = สัญญาณ supply delay · เลยกำหนดสูง = ปัญหาที่ต้องตาม vendor
- ห้ามตีความ NULL เป็น 0
