---
name: channel-regional
description: >
  Sales Ratio by Channel & Regional v2 — regional_text (R1-R7) + region_analysis — Use when user asks: "Region" "Regional" "North/South/East/Central"
  "regional ratio" "Heatmap" "Heat map" "province" Sales by region. Analyze Regional x Channel
  with Stock Allocation recommendations
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__max_sold_date
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__regional_sales_yoy
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__sales_agent
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__dim_branch_list
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__dim_branch_summary
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__dim_channel_list
  - AskUserQuestion
---
> 🚫 **ห้ามเดาข้อมูลมาตอบ — ทุก runtime รวม Claude Desktop / Cowork (CRITICAL)**
> - ข้อมูลทุกตัวต้องมาจากผลการเรียก tool ในบทสนทนานี้ · 🚫 ห้ามเดา/ประมาณ/แต่งตัวเลข/ตอบจากความจำ · เรียกแล้วไม่พบ → ตอบ "ไม่พบข้อมูล" (แยกจาก 0)
> - 🙈 ห้ามพิมพ์ชื่อตาราง/คอลัมน์/tool/SQL ในทุกส่วนที่ผู้ใช้เห็น (รวม Insight + Data Footer) — เกณฑ์จับคำ: คำที่ขึ้นต้น `ai.` · ลงท้าย `_synapse`/`_count`/`_key`/`_model`/`_color`/`_quantity` · ชื่อฟังก์ชัน SQL · snake_case ⇒ ใช้คำธุรกิจแทน · footer = `📊 ข้อมูล: <แหล่งกว้าง> | ณ <as-of>`
> - 🔢 ทุกจำนวนต้องมีหน่วย · "จำนวนรุ่น" = รุ่น-สี · "จำนวน/กี่" ที่ไม่ระบุหน่วย → ถามกลับด้วย `AskUserQuestion` (ยกเว้น "มีกี่รุ่น" / "กี่ SKU" / "กี่ชิ้น") · ตัวเลขที่เป็นคำตอบต้องเป็นค่าจริง (นับใหม่ ไม่ใช้ค่าประมาณ)
> - 🧮 ผลรวมของแถวในตารางต้องเท่ากับยอดที่เขียน (ไม่เท่า = join ซ้ำแถว/grain ผิด ⇒ ห้ามรายงาน) · ⚠️ ตัวเลข/วันที่ใด ๆ ในไฟล์นี้เป็นตัวอย่าง — ห้ามนำไปตอบ ให้อ่านค่าจริง
> - 📌 **แหล่งมาตรฐานของยอดขาย = "Sales Out" จาก mcg-sales** — ถ้าต้องใช้หลายแหล่ง ให้บอกชื่อแหล่งเป็น **ภาษาธุรกิจ** ("Sales Out (mcg-sales)" · "ยอดขายบริษัท (invoice)") · 🚫 ห้ามพิมพ์ชื่อตาราง/ระบบในคำตอบหรือ footer
> 📖 กฎฉบับเต็ม + ตัวอย่างผิด/ถูก: **§1 ของ skill แม่** (ไฟล์นี้ include ไว้ด้านล่าง)

#[[file:../sales-agent/SKILL.md]]

---

### 🧮 กระทบยอด + แหล่งป้ายภูมิภาค + ความยาวคำตอบ (บังคับ — จากเคสจริง 2026-09-30)

- 🧮 **กระทบยอดก่อนรายงาน** — ผลรวมของทุกแถวในตารางต้องเท่ากับ "ยอดรวมทั้งบริษัท" ที่ tool เดียวกันคืน · ถ้าไม่เท่า = **join ซ้ำแถว (fan-out) / grain ผิด** ⇒ ห้ามรายงาน (เคสจริง: ผลรวมของตารางภูมิภาคสูงกว่ายอดจริงหลายสิบเท่า ขณะที่ตารางจังหวัดในคำตอบเดียวกันถูก) · ⚠️ ห้ามลอกตัวเลขจากไฟล์นี้ — ข้อมูลเปลี่ยนทุกวัน ให้อ่านค่าจริงจาก tool
- 🗺️ **ป้ายภูมิภาคต้องมาจาก branch master** — 🚫 ห้ามใช้ป้ายภูมิภาค "ต่อแถว" ของตารางยอดขาย (มีชื่อเก่า/ใหม่ปนกัน ⇒ แถวชื่อเก่าจะเหลือยอดเพียงบางส่วนของช่วง อ่านเป็น "ยอดตกก้อนใหญ่" ทั้งที่ไม่มีอะไรหาย) · ✅ ใช้ canned tool ที่จัดภูมิภาคให้แล้วก่อน (เช่น `regional_sales_yoy`) ไม่ต้องเขียน GROUP BY เอง
- 🚫 **ห้ามวางชื่อเก่าและชื่อใหม่ในตารางเดียวกัน** (แม้มี footnote) — ถ้าจำเป็นให้แยกตาราง + กำกับว่าเทียบข้ามชุดไม่ได้
- 🔀 **ป้ายภูมิภาคของแต่ละระบบไม่เหมือนกัน (คนละชุดคำ)** — 🚫 ห้ามเทียบชื่อภูมิภาคข้ามระบบ/ข้ามแหล่ง ให้เทียบ **ยอดรวม** แทน
- ⏱️ **จำกัดการเรียก tool ≤ 4–6 ครั้งต่อคำถาม** · ถ้าผู้ใช้ถาม "เสร็จยัง" ให้ **สรุปเท่าที่มีทันที** แล้วค่อยเสนอเพิ่ม — 🚫 ห้ามยิง query ต่อเงียบ ๆ

### 🗺️ ชื่อภูมิภาค (region) — **ห้าม hardcode ค่า ต้องดึงค่าจริงเสมอ** (CRITICAL)

- 🔴 **ค่าภูมิภาคเปลี่ยนได้ (dynamic)** — ห้ามเขียนรายชื่อภูมิภาคลงในคำตอบ/ไฟล์จากความจำ ⇒ **ให้ดึงค่าที่มีจริงในระบบก่อนจัดกลุ่มหรือรายงาน** (ดูรายการจริงจาก tool ที่ group_by ระดับภูมิภาคได้)
- ⚠️ **ถ้าผู้ใช้ถามด้วยชื่อภูมิภาคที่ไม่มีในผลลัพธ์** (เช่น ชื่อเดิมแบบ North / South / Northeast เดี่ยว ๆ) → **ต้องเตือนว่าป้ายชื่ออาจถูกจัดกลุ่มใหม่** แล้วเสนอค่าที่มีจริงให้เลือก · 🚫 ห้ามตอบ 0/ว่างแล้วปล่อยผ่าน
- 🚫 **ห้ามสรุปว่า "ยอดตก" จากชื่อที่จับคู่ไม่ตรง** — ชื่อเดิมไม่มีแถว = **ป้ายชื่อเปลี่ยน ไม่ใช่ยอดขายหาย** ⇒ ต้องบอกให้ชัดและเสนอเทียบภายในชื่อที่มีจริง
- ℹ️ **หลักฐานประกอบ (ตรวจ 2026-09-30 — เป็นค่าชั่วขณะ ต้องอ่านใหม่ทุกครั้ง):** ชุดป้ายภูมิภาค **เปลี่ยนได้ และแต่ละแหล่งใช้คำไม่เหมือนกัน** ⇒ 🚫 ห้ามลอกชื่อภูมิภาคจากไฟล์นี้หรือจากความจำ ให้อ่านค่าที่ tool คืนในรอบนั้น · อาการที่พบคือรายงานซึ่งยึดชื่อเดิมอ่านเป็น **ยอดตกก้อนใหญ่** ทั้งที่ **เป็นการจัดกลุ่มใหม่ ไม่ใช่ยอดหาย** · กลุ่มที่ชื่อมีคำ "Mobile" ต่อท้ายมีเพียง 1–2 สาขา/ภูมิภาค สัดส่วนเล็ก ⇒ ไม่ใช่สาเหตุ

### Regional Mapping (v2)
Uses regional_text (R1-R7) and region_analysis (province name) — no direct region column
NULL+E% branch → Online | NULL+non-E% → Other | Else → RTRIM(regional_text)

## Step 2 — Regional x Main Channel

Use Regional mapping: NULL+E%=Online, NULL+Other=Other, else RTRIM(regional_text)

⚠️ **Performance Rule — CTEs forbidden — write direct query**:
```sql
-- Use conditional SUM + CASE WHEN regional mapping in a single query
SELECT
  CASE WHEN regional_text IS NULL AND main_channel = 'ONLINE' THEN 'Online'
       WHEN regional_text IS NULL AND main_channel = 'OFFLINE' THEN 'Other'
       ELSE RTRIM(regional_text) END AS regional,
  main_channel,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '<max_date>' THEN total_exc_vat_price ELSE 0 END) AS ns_curr,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_prev_start}}' AND '<same_day_prev>' THEN total_exc_vat_price ELSE 0 END) AS ns_prev
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_prev_start}}' AND '<max_date>'
GROUP BY
  CASE WHEN regional_text IS NULL AND main_channel = 'ONLINE' THEN 'Online'
       WHEN regional_text IS NULL AND main_channel = 'OFFLINE' THEN 'Other'
       ELSE RTRIM(regional_text) END,
  main_channel
ORDER BY ns_curr DESC
```
> ⚠️ **ห้าม hardcode ปีในเงื่อนไข** — ต้องดึง `fy_curr_start` / `fy_prev_start` / `same_day_prev` จาก `max_sold_date` ทุกครั้ง (กฎเดียวกับ sales-agent) ไม่งั้นพอขึ้นปีใหม่คำตอบจะเงียบ ๆ ผิด

Calculate: Net Sales (฿), Sales Ratio%, Tickets (ใบเสร็จ), Margin%, Qty (ชิ้น)

ถ้าคำตอบต้องมี «จำนวนรุ่น» → GROUP BY `model_color` แล้วนับเป็น «จำนวนรุ่น-สี» เท่านั้น — ห้ามนับ `model` แทน (รุ่น-สี ≠ รุ่น ≠ SKU) และติดหน่วยทุกครั้งที่ตอบเป็นจำนวน

---

## Step 3 — Heatmap Regional x Main Channel

| Regional | OFFLINE | ONLINE | OFFLINE% | ONLINE% |

---

## Step 4 — Top 10 Provinces

---

## Step 5 — Response

**Headline** — Fastest growing channel + highest revenue region

**Table 1: Regional** | Regional | Net Sales FY27 | Ratio% | Net Sales FY26 | YoY% | Margin% |

**Table 2: Heatmap** | Regional | OFFLINE | ONLINE | OFFLINE% | ONLINE% |

**Table 3: Top 10 Provinces** | Province | Net Sales | OFFLINE% | ONLINE% | YoY% |

**Stock Allocation suggestions** — based on actual data (ระบุเป็นจำนวน «ชิ้น» เท่านั้น)

ถ้าผู้ใช้ถาม «รับของเข้า» / «Sales In» / ปริมาณรับเข้า (GR) — ไม่ใช่ขอบเขตของ skill นี้ → ตอบจำนวน «ชิ้น» เป็นตัวเลขหลัก แล้วส่งต่อ mcg-inventory-agent (po-intake) · ห้ามยกมูลค่า (บาท / PO value) ขึ้นเป็นตัวเลขหลัก เว้นแต่ผู้ใช้ถามเรื่องมูลค่าเอง · ต้องแยก สั่ง (PO) · รับเข้าแล้ว (GR) · ค้างส่ง พร้อมระบุช่วงวันที่ (as-of)

**Data Footer**

---

# Output Rules

- Regional mapping must not display NULL
- ≤3 tables
- Stock suggestions must reference actual data
- ทุกตัวเลขที่เป็นจำนวน ต้องติดหน่วยกำกับเสมอ (กี่ SKU / กี่รุ่น / กี่รุ่น-สี / กี่ชิ้น) พร้อมบอกขอบเขตที่กรอง — ห้ามปล่อยตัวเลขจำนวนลอย ๆ
- «จำนวนรุ่น» = «รุ่น-สี» (`model_color`) เท่านั้น — ไม่ใช่ `model` และไม่ใช่ SKU (`item_code`) (รุ่น-สี ≠ รุ่น ≠ SKU — ต่างกันมาก ⇒ ผิดหน่วย = ตัวเลขผิดจริง)
- «จำนวน» / «กี่» ที่ไม่ระบุหน่วย → ถามกลับก่อนว่าจะนับเป็น **SKU / รุ่น (รุ่น-สี) / ชิ้น** (ดู §1.1.1) ห้ามเดาแล้วตอบตัวเลขเดียว · 🚫 ไม่มีตัวเลือก "รุ่น" แยกจาก "รุ่น-สี" — คำว่า «รุ่น» = รุ่น-สี เสมอ
