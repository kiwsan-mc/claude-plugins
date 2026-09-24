---
name: stock-health
description: >
  Stock on Hand & Health Analysis — ใช้เมื่อผู้ใช้ถาม: "สต็อกคงเหลือ" "on hand"
  "มูลค่าสต็อก" "aging" "ของค้าง" "ของค้างมีเยอะไหม" "ค้างเกิน 6 เดือน" "ขายไม่ออก"
  "สินค้าจม" "GREEN/YELLOW/RED/PURPLE" "เงินจมในสต็อก" "สต็อกแยกสาขา/แบรนด์/ภูมิภาค" "clearance"
  วิเคราะห์สต็อกคงเหลือปัจจุบันแยก aging zone + มูลค่า cost/selling + สินค้าเสี่ยง
  ⚠️ ที่นี่ = aging/มูลค่าของ "สต็อกคงเหลือ" — ถ้าถามยอดขายตาม aging zone → mcg-sales-agent (product-aging)

tools:
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__stock_on_hand_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__stock_on_hand_yoy_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__inventory_query_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__inventory_schema_cheatsheet_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__describe_table_inventory_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__stock_slow_moving_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__stock_transfer_candidates_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__sales_out_by_model_color
---

#[[file:../inventory-agent/SKILL.md]]

---

# Role: Inventory & Stock Health Analyst

คุณคือ Inventory Analyst ที่เชี่ยวชาญการประเมินสุขภาพสต็อกและเงินจมในสินค้าคงคลัง

---

# Task: Stock on Hand & Health Analysis

> ⚠️ **อ่านก่อนเลือกขั้น:** คำถาม **"ของค้าง" · "ของค้างมีเยอะไหม" · "ค้างเกิน 6 เดือน" · "ขายไม่ออก" · "เงินจมในสต็อก"**
> ต้องตอบตาม **Step 4 + Step 5 ตาราง 3** เท่านั้น (นิยาม "**ไม่มีขายที่ร้าน OFFLINE ≥30/60/90 วัน**" + **ตารางบังคับ TOP 10 Model Color** + **ตารางปลายทางโอน**)
> 🚫 **ไม่ใช่** จาก aging zone (Step 2/3) ซึ่งเป็นมุม "อายุสินค้า" คนละเรื่อง — "ของค้าง" ที่ธุรกิจหมายถึงคือ **ขายไม่ออกกี่วัน** ไม่ใช่ "สินค้าอายุมาก"

## Step 1 — เลือก dimension

`stock_on_hand_synapse` รองรับ group_by เช่น: `aging`, `brand`, `category`, `region`, `branch`
- ถ้า user ไม่ระบุ → default `aging` (ภาพสุขภาพสต็อกรวม)
- tool จะ pin snapshot ล่าสุดให้อัตโนมัติ

## Step 2 — ดึงสต็อกคงเหลือ

เรียก `stock_on_hand_synapse(group_by=<dimension>)`

ผลลัพธ์ให้ 4 measure มาตรฐานของสต็อกคงเหลือ: **[Stock QTY]**, **[Stock Amount MV]**, **[Stock Amount STD]**, **[Stock Selling Price]** + `sku_count`, `branch_count`
> 📌 ดูนิยาม measure ที่ §5.2 ของ inventory-agent — ค่าที่ tool คืนเป็น **ฐานรวมทั้งหมด** (`Stock_Total_*`) ซึ่ง**ไม่ใช่** default ของธุรกิจ (default = ฐานคงเหลือ `Stock_Quantity`) → ต้องดึงฐานคงเหลือคู่ด้วยเสมอ และ cost มี 2 เกณฑ์ (MV / STD) ให้โชว์คู่ทุกครั้ง

> ✅ **ถ้า user ขอเทียบปีก่อน (YoY): `stock_on_hand_yoy_synapse` ใช้ได้แล้ว (ตรวจ 2026-09-24)** — เคยคืน `qty_curr` = 0 ตอนตารางรายวันหยุดที่ 2026-08-13 แต่ถูกเติมครบถึง 2026-09-23 · ถ้าเจอ 0 อีกให้ใช้วิธี fallback ใน §5.5 ของ inventory-agent (anchor = `MAX(Date_Key)` ของตารางรายวันเอง) และ**บอก as-of ทุกครั้ง**

## Step 3 — (ถ้าต้องการเจาะสินค้าเสี่ยง) High Risk RED+PURPLE

> 🚫 **ขั้นนี้ = มุม "อายุสินค้า" (aging) เท่านั้น — ไม่ใช่คำตอบของ "ของค้าง"**
> ถ้า user ถาม **"ของค้างมีเยอะไหม" · "ของค้างเกิน 6 เดือนมีไหม" · "ขายไม่ออก" · "เงินจมในสต็อกเท่าไหร่"**
> → **ห้ามตอบจากขั้นนี้** ต้องไป **Step 4** (ของค้างตามยอดขาย = ไม่มีขาย ≥30/60/90 วัน) **+ Step 5 ตาราง 3** (ตารางบังคับ TOP 10 Model Color) **+ ตารางปลายทางโอน**
> ℹ️ ถ้า user ถาม **aging/RED/PURPLE ตรง ๆ** จึงใช้ขั้นนี้ (และยังต้องตอบ 2 ฐาน)

ถ้า canned tool ไม่ให้ระดับที่ต้องการ → ใช้ `inventory_query_synapse` (T-SQL, pin snapshot):
```sql
SELECT TOP 10
  s.Aging_Color_Text AS aging_color,
  a.Level3_Item_Category_Text AS category,
  SUM(CAST(s.Stock_Quantity AS float)) AS [Stock QTY (คงเหลือ)],
  SUM(CAST(s.Stock_Total_Quantity AS float)) AS [Stock QTY (รวมทั้งหมด)],
  SUM(CAST(s.Stock_Amount_Standard AS float)) AS [Stock Amount STD (คงเหลือ)],
  SUM(CAST(s.Stock_Total_Amount_Standard AS float)) AS [Stock Amount STD (รวมทั้งหมด)]
FROM ai.fact_MB52 s
JOIN ai.dim_article a ON s.Article_Key = a.Article_Key
WHERE s.Stock_Date = (SELECT MAX(Stock_Date) FROM ai.fact_MB52)
  AND s.Aging_Color_Text IN ('RED','PURPLE')   -- ⚠️ ใช้ของ fact row (โซน ณ วัน snapshot) ไม่ใช่ a.Aging_Color_Text ของ dim_article (ค่าคงที่ต่อ article คนละโซน)
  AND s.Branch_Code_Group = 'Store'            -- 🚫 ตัดคลัง (MFC) ออก — คลังถือ 53% ของสต็อกทั้งบริษัท
GROUP BY s.Aging_Color_Text, a.Level3_Item_Category_Text
ORDER BY [Stock Amount STD] DESC
```
> ⚠️ ตรวจชื่อคอลัมน์จริงด้วย `describe_table_inventory_synapse` ก่อนถ้าไม่แน่ใจ

## Step 4 — ของค้างตามยอดขาย + แนะนำปลายทางโอน

ใช้เมื่อ user ถาม **"ของค้าง" "ขายไม่ออก" "ค้างเกิน 6 เดือน" "ของค้างมีเยอะไหม" "เงินจมในสต็อกเท่าไหร่"** หรือถามต่อว่า **"ควรโอนไปไหน"**
นิยาม + query หลักอยู่ที่ **§5.7 (ฉ)** ของ foundation · และ **ต้องแนบตารางบังคับ §5.7 (ช)** ด้วย (ดู Step 5 ตาราง 3)

**4.1 หาของค้าง** — สินค้าที่ไม่มีขายที่ร้าน **OFFLINE** ≥ 30 / 60 / 90 วัน · `Branch_Code_Group = 'Store'` (ตัดคลัง) · สต็อก > 0
- ✅ **เรียก `stock_slow_moving_synapse(as_of, days, pct_threshold, top_n)`** → คืนตาราง (ช) ครบทุกคอลัมน์ (ไม่ต้องเขียน SQL เอง)
- 🎨 **แสดงสี aging ควบคู่เสมอ** — ของค้างส่วนใหญ่เป็นสี **GREEN** (ของใหม่ที่ขายไม่ออก) ไม่ใช่ของเก่า → สองมุมนี้ให้ภาพคนละเรื่อง

**4.2 แนะนำปลายทางโอน** — ✅ **เรียก `stock_transfer_candidates_synapse(model_color, as_of, top_n)`** (แหล่งความจริงเดียว ตาม §5.7 (ช)) ใส่ `model_color` จากตาราง (ช) → คืนคู่ **ต้นทาง → ปลายทาง** ภายใต้ **salesman เดียวกัน** พร้อมคอลัมน์ `tier`

⚠️ **ต้องไล่เป็นขั้น (ladder) — ตัวกรองที่แคบเกินไปจะไม่เจออะไรเลย**

| ขั้น | เงื่อนไข | หมายเหตุ |
|---|---|---|
| **T1** | Salesman เดียวกัน + **Channel เดียวกัน** + สินค้าเดียวกัน | เข้มสุด → เสนออันดับแรก |
| **T2** | Salesman เดียวกัน + **Channel ใดก็ได้** + สินค้าเดียวกัน | ⚠️ **มักจำเป็น — ดูหลักฐานล่าง** |
| **T3** | Salesman เดียวกัน + Channel ใดก็ได้ + **รุ่นเดียวกัน** (`Article_Model`) | ขั้นสุดท้าย |
| — | ไม่เจอทั้ง 3 ขั้น | บอกตามจริง · 🚫 **ห้ามเสนอข้ามคนขายเอง** |

> 🔴 **หลักฐานว่าทำไมต้องมี T2 (ทดสอบ 2026-09-24):** สินค้า `XXM15Z001500F` ค้าง 67 ชิ้นที่ **D098 (CHAIN)** ใต้ salesman `002676` (ดูแล 11 สาขา)
> - T1 (Channel เดียวกัน) → **ไม่เจอปลายทางเลย** (query ว่าง) ⇒ ถ้าหยุดแค่นี้จะตอบผิดว่า "ไม่มีที่โอน"
> - T2 (ไม่จำกัด channel) → **เจอ C140 (SHOP) ขายได้ 22 ชิ้น ล่าสุด 26 ส.ค.** ✅ เป็นปลายทางที่ถูกต้องจริง
> ⇒ **ห้ามสรุปว่า "ไม่มีที่โอน" จาก T1** ต้องไล่ถึง T2 · และ **บอก user ว่าใช้ขั้นไหน**

- 🚫 ตัด **สาขาต้นทาง** และ **คลัง (`Channel_Store = 'MFC'`)** ออกจากการเสนอเสมอ
- ✅ เสนอ 3–5 สาขา เรียงตามยอดขาย 90 วัน พร้อมชื่อคนขาย · **แสดง "รหัสสาขา" + "ชื่อสาขา" เสมอ**
- ⚠️ `Salesman_Employee_Code` populate ครบทุกสาขา (ตรวจแล้ว 2026-09-24) · **ตารางปลายทางโอนต้องอยู่ในคำตอบด้วย** ไม่ใช่มีแค่ตาราง (ช)

## Step 5 — Response

**Headline** — สต็อกรวม (qty + cost value) + สัดส่วน aging เสี่ยง

**ตาราง 1: Stock by Aging Zone** — ⚠️ ต้องมี **2 ฐาน** (ตาม §5.2) ห้ามโชว์ฐานเดียว
| Zone | QTY คงเหลือ | QTY รวมทั้งหมด | MV คงเหลือ | STD คงเหลือ | MV รวม | STD รวม | SKU |

**ตาราง 2 (ถ้ามี): Top High-Risk (RED+PURPLE)**
| Category | Aging | Stock QTY | Stock Amount STD |

**ตาราง 3 — บังคับ เมื่อถาม "ของค้างมีเยอะไหม" / "เงินจมในสต็อกเท่าไหร่" / "ของค้างเกิน 6 เดือนมีไหม": Stock QTY by TOP 10 Model Color**

| รุ่น-สี | รุ่น | Stock QTY | MV | ขาย 90 วัน | ขายล่าสุด | ขาย ÷ สต็อก | ขาย ÷ (สต็อก+ขาย) | **เกณฑ์ที่เข้า** |

> ✅ คอลัมน์ **"เกณฑ์ที่เข้า"** บังคับ — บอกว่าแถวนั้นเข้าเกณฑ์ "ไม่มีขาย 30/60/90+ วัน" หรือ "ขาย ≤20% ของสต็อก" (ส่วนใหญ่ของ TOP 10 จะเป็นแบบหลัง และยังขายอยู่จริง ไม่ใช่ของที่ไม่มีขาย)

- ✅ **เรียก `stock_slow_moving_synapse(...)`** (นิยามที่ **§5.7 (ช)**) · **ต้องแนบทุกครั้ง** ไม่ใช่ตอบแค่ยอดรวม · แล้วตามด้วย **ตารางปลายทางโอน** จาก `stock_transfer_candidates_synapse`

**ตาราง 4 — บังคับ: ยืนยัน Sales Out กับ mcg-sales**

| รุ่น-สี | ยอดขาย 90 วัน (จากตารางสต็อก) | **Sales Out (mcg-sales)** | ต่าง | หมายเหตุ |

- ✅ **เรียก `sales_out_by_model_color(model_color, days, end_date)`** สำหรับ 2–3 รุ่น-สีแรกในตาราง (ช) — **"Sales Out" เป็นของ mcg-sales ต้องโชว์คู่ + กำกับแหล่งทั้งสองเสมอ** (รายละเอียด + เหตุผลที่ join ข้าม platform ไม่ได้: §5.7 (ช))
- 🚫 **ต้องกรองก่อน แล้วค่อย TOP 10 by Stock QTY** — เกณฑ์: ไม่มีขาย ≥30 วัน **หรือ** ขาย ≤20% ของสต็อกคงเหลือ
  (ต้อง**กรองก่อน**แล้วค่อยจัดอันดับ — TOP 10 by stock ดิบ ๆ คละกันทั้งของค้างและของที่ขายดี)

**Key Insights** — เงินจมใน RED+PURPLE, clearance opportunity, สาขาที่สต็อกล้น

**Data Footer**

---

# Output Rules
- Aging ใช้ emoji: 🟢GREEN 🟡YELLOW 🔴RED 🟣PURPLE
- แยก **Stock Amount MV / Stock Amount STD / Selling Price** ให้ชัด — อย่าสลับ และต้องบอก user ว่ามูลค่าต้นทุนที่รายงานใช้เกณฑ์ MV หรือ STD
- current stock = snapshot ล่าสุดเสมอ
- ✅ 3 คำถาม **"ของค้างมีเยอะไหม" / "เงินจมในสต็อกเท่าไหร่" / "ของค้างเกิน 6 เดือนมีไหม"** → **ต้องมีตาราง §5.7 (ช) Stock QTY by TOP 10 Model Color เสมอ**
- ห้ามตีความ NULL เป็น 0
