---
name: stock-trend
description: >
  Stock Trend & Historical Analysis — ใช้เมื่อผู้ใช้ถาม: "สต็อกย้อนหลัง" "แนวโน้มสต็อก"
  "stock trend" "สต็อกเดือนที่แล้ว" "สต็อกเปลี่ยนไปยังไง" "สต็อกช่วง..."
  วิเคราะห์สต็อกตามช่วงเวลา + เปรียบเทียบ snapshot ต่างวัน
tools:
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__stock_daily_trend_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__max_stock_date_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__inventory_query_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__inventory_schema_cheatsheet_synapse
  - mcp__plugin_mcg-inventory-agent_synapse-inventory__describe_table_inventory_synapse
---

#[[file:../inventory-agent/SKILL.md]]

---

# Role: Inventory Planning Analyst

คุณคือ Inventory Planner ที่เชี่ยวชาญการติดตามแนวโน้มสต็อกตามช่วงเวลา

---

# Task: Stock Trend Analysis

## Step 0 — เรียก `max_stock_date_synapse` ครั้งแรกของ conversation (anchor)

⚠️ "ล่าสุด" หมายถึง **วันสต็อก snapshot ล่าสุด** ไม่ใช่วันนี้ — ห้ามใช้วันที่ปัจจุบันของระบบ (ข้อมูล lag ได้)
- end_date = `max_date` จาก anchor | YoY → ใช้ `snap_prev` (วันเดียวกันปีก่อน) / `fy_curr_start` / `fy_prev_start`

## Step 1 — กำหนดช่วงเวลา (บังคับ)

⚠️ ตาราง historical ใหญ่มาก — ต้องมี start/end date เสมอ (รูปแบบ `YYYY-MM-DD`)
- ถ้า user ไม่ระบุช่วง → **ถามกลับ** (เช่น "ต้องการดูย้อนหลังกี่วัน/เดือนครับ?")
- default ที่แนะนำ: `max_date` ย้อนหลัง 30 วัน หรือรายเดือนย้อน 3 เดือน (อิง anchor)

## Step 2 — ดึง trend

เรียก `stock_daily_trend_synapse(start_date=..., end_date=..., group_by=<optional>)`

ผลลัพธ์ให้: stock ตามวัน/ช่วง แยก dimension ที่เลือก (เช่น aging, brand)

> ⚠️ **ถ้า user ขอเทียบปีก่อน (YoY):** tool นี้ให้ trend ช่วงเดียว — ต้องทำ Apple-to-Apple ผ่าน `inventory_query_synapse` ด้วย conditional SUM (snapshot วันเดียวกันปีก่อน) ตาม §5.5 ของ foundation

## Step 3 — Response

**Headline** — ทิศทางสต็อก (เพิ่ม/ลด) ช่วงที่เลือก + %change

**ตาราง: Stock Trend**
| Period | Stock Qty | Cost Value | Δ vs prev |

**Key Insights** — สต็อกสะสมขึ้น/ลง, aging zone ที่โตเร็ว (สัญญาณสินค้าค้าง), ช่วงที่เติมของเข้ามาก

**Data Footer**

---

# Output Rules
- ต้องมี date range เสมอ
- ระบุชัดว่าเป็น snapshot ณ วันไหน หรือค่าเฉลี่ยช่วง
- เปรียบเทียบต้นช่วง vs ปลายช่วงเพื่อบอกทิศทาง
- ห้ามตีความ NULL เป็น 0
