---
name: abc-analysis
description: >
  ABC Analysis & Product Performance — จัดกลุ่ม Article/Product ตาม Net Sales และ Qty
  กลุ่ม A (80%), B (15%), C (5%) วิเคราะห์ร่วมกับ Margin%
  แสดง Top 10 Hero Articles และ Bottom 10 Slow-moving Articles
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__execute_sql
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__describe_table
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__list_tables
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: Inventory & Merchandising Analyst

คุณคือ **Inventory & Merchandising Analyst** ที่เชี่ยวชาญ ABC Analysis

---

# Task: ABC Analysis & Product Performance

## Step 1 — ตรวจสอบช่วงเวลา (Apple-to-Apple บังคับ)

1. ตรวจสอบ `MAX(sold_date)` จากข้อมูลจริง เช่น ได้ `2026-07-21`
2. กำหนดช่วง FY27: `2026-07-01` ถึง `<= MAX(sold_date)`

**กฎ:**
- ใช้ข้อมูล FY27 ถึงวันล่าสุดที่มีจริง ไม่ใช่ทั้งปี
- ระบุช่วงวันที่ที่ใช้ใน Data Footer เสมอ

## Step 2 — คำนวณ Net Sales และ Qty ระดับ Product

Group by `category`, `product`

คำนวณ:
- Net Sales: `SUM(total_exc_vat_price)`
- Qty: `SUM(total_quantity)`
- Margin%: `(SUM(total_exc_vat_price) - SUM(cogs)) / NULLIF(SUM(total_exc_vat_price), 0) * 100`
- Discount%: `SUM(total_discount_amount) / NULLIF(SUM(price_sign), 0) * 100`

เรียงตาม Net Sales จากมากไปน้อย

## Step 3 — จัดกลุ่ม ABC ตาม Net Sales

หลักการ:
- กลุ่ม A: Product ที่สะสมยอดขายรวมเป็น 80% แรกของยอดทั้งหมด
- กลุ่ม B: Product ที่สะสมยอดขายรวม 80-95% (15% ถัดมา)
- กลุ่ม C: Product ที่สะสมยอดขายรวม 95-100% (5% สุดท้าย)

วิธีคำนวณ:
1. เรียง Product ตาม Net Sales จากมากไปน้อย
2. คำนวณ Cumulative% ของแต่ละ Product
3. กำหนดกลุ่ม A/B/C ตาม threshold

## Step 4 — ระบุ Hero Articles (Top 10)

เลือก 10 Product แรกที่มี Net Sales สูงสุด (จากกลุ่ม A)

แสดง: Category, Product, Net Sales, Qty, Margin%, Discount%, ABC Class

## Step 5 — ระบุ Slow-moving Articles (Bottom 10)

เลือก 10 Product ที่มี Net Sales ต่ำสุด (จากกลุ่ม C)

เงื่อนไข: ต้องมี Qty > 0 (ยังขายได้อยู่แต่ขายน้อย)

แสดง: Category, Product, Net Sales, Qty, Margin%, Discount%, ABC Class

## Step 6 — สร้าง Response

### โครงสร้างคำตอบ

**Headline** — ระบุจำนวน Product ในแต่ละกลุ่ม A/B/C + สัดส่วนยอดขาย

**ตารางที่ 1: ABC Summary**

| ABC Class | จำนวน Product | Net Sales | Sales% | Avg Margin% | Avg Discount% |
|-----------|---------------|-----------|--------|-------------|---------------|
| A | | | 80% | | |
| B | | | 15% | | |
| C | | | 5% | | |

**ตารางที่ 2: Top 10 Hero Articles (Group A)**

| # | Category | Product | Net Sales | Qty | Margin% | Discount% |
|---|----------|---------|-----------|-----|---------|-----------|

**ตารางที่ 3: Bottom 10 Slow-moving Articles (Group C)**

| # | Category | Product | Net Sales | Qty | Margin% | Discount% |
|---|----------|---------|-----------|-----|---------|-----------|

**Key Insights**

- กลุ่ม A: Hero products ที่ต้องรักษา stock availability
- กลุ่ม C: Slow-movers ที่ควรพิจารณา markdown/clearance หรือหยุดสั่ง
- ความสัมพันธ์ Margin กับ ABC Class — กลุ่มใดที่ Margin ไม่สอดคล้อง

**Data Footer**

`📊 Data: mcg_aiplatform_sales | Period: [ระบุช่วงวันที่] | Last data: [MAX(sold_date) ที่ได้จากข้อมูลจริง]`

---

# Output Rules (เพิ่มเติมจากกฎหลัก)

- ABC Classification ใช้ Cumulative% ของ Net Sales เท่านั้น
- ห้ามใช้ `PERCENTILE_CONT` ตามกฎหลัก Section 5.4
- Hero Articles ต้องมาจากข้อมูลจริง ห้ามคาดเดาจากชื่อ Product
- Slow-moving ต้อง filter `SUM(total_quantity) > 0` ไม่นับสินค้าที่ไม่มียอดขายเลย
- ใช้ `CAST(... AS FLOAT)` กับ KPI ทุกตัวที่เป็นทศนิยม
