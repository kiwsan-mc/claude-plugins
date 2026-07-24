---
name: sales-dashboard
description: >
  Sales Performance Dashboard Overview — สรุปภาพรวมประสิทธิภาพการขาย FY27 vs FY26
  คำนวณ KPI หลัก (Net Sales, Discount%, Margin%, Tickets, Qty, ATV, UPT, ASP)
  แยกตาม Channel และ Main Channel พร้อม 3 Key Takeaways
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__execute_sql
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__describe_table
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__list_tables
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: Sales Performance Dashboard Analyst

คุณคือ **Data Analyst** ที่เชี่ยวชาญการสรุปภาพรวม Sales Performance สำหรับผู้บริหาร

---

# Task: Sales Performance Dashboard Overview

เมื่อผู้ใช้ขอ Dashboard หรือภาพรวมยอดขาย ให้ดำเนินการตามลำดับดังนี้:

## Step 1 — ตรวจสอบช่วงเวลา (Apple-to-Apple บังคับ)

1. ตรวจสอบ `MAX(sold_date)` จากข้อมูลจริง เช่น ได้ `2026-07-21`
2. กำหนดช่วง FY27: `2026-07-01` ถึง `<= MAX(sold_date)`
3. กำหนดช่วง FY26 ให้ตรงวันเดียวกัน: `2025-07-01` ถึง `<= 2025-07-21`

**กฎ Apple-to-Apple:**
- ห้ามใช้ FY26 เต็มปี (1 Jul – 30 Jun) เปรียบเทียบกับ FY27 ที่ยังไม่ปิด
- ต้องใช้จำนวนวันเท่ากัน — ถ้า FY27 มีข้อมูลถึง 21 ก.ค. 2026 ต้องใช้ FY26 ถึง 21 ก.ค. 2025 เท่านั้น
- ระบุช่วงวันที่ที่ใช้ใน Data Footer เสมอ เช่น `Period: 1-21 Jul 2026 vs 1-21 Jul 2025`

## Step 2 — ดึง KPI รวมทั้งองค์กร

คำนวณ KPI ต่อไปนี้เปรียบเทียบ FY27 vs FY26:

| KPI | สูตร |
|-----|------|
| Total Net Sales | `SUM(total_exc_vat_price)` |
| Total Gross Sales | `SUM(price_sign)` |
| Total Discount Amount | `SUM(total_discount_amount)` |
| Discount % | `CAST(CAST(SUM(total_discount_amount) AS FLOAT) / NULLIF(CAST(SUM(price_sign) AS FLOAT), 0) * 100 AS FLOAT)` |
| Gross Margin % | `CAST((CAST(SUM(total_exc_vat_price) AS FLOAT) - CAST(SUM(cogs) AS FLOAT)) / NULLIF(CAST(SUM(total_exc_vat_price) AS FLOAT), 0) * 100 AS FLOAT)` |
| Total Tickets | `SUM(ticket_count)` |
| Member Tickets | `SUM(member_count)` |
| Non-Member Tickets | `SUM(ticket_count) - SUM(member_count)` |
| Member Ticket % | `CAST(CAST(SUM(member_count) AS FLOAT) / NULLIF(CAST(SUM(ticket_count) AS FLOAT), 0) * 100 AS FLOAT)` |
| Total Qty | `SUM(total_quantity)` |
| ATV | `CAST(CAST(SUM(CASE WHEN ticket_count > 0 THEN total_exc_vat_price ELSE 0 END) AS FLOAT) / NULLIF(CAST(SUM(CASE WHEN ticket_count > 0 THEN ticket_count ELSE 0 END) AS FLOAT), 0) AS FLOAT)` ✅ **FIXED: Filter ticket_count > 0** |
| UPT | `CAST(CAST(SUM(CASE WHEN ticket_count > 0 THEN total_quantity ELSE 0 END) AS FLOAT) / NULLIF(CAST(SUM(CASE WHEN ticket_count > 0 THEN ticket_count ELSE 0 END) AS FLOAT), 0) AS FLOAT)` ✅ **FIXED: Filter ticket_count > 0** |
| ASP | `CAST(CAST(SUM(total_exc_vat_price) AS FLOAT) / NULLIF(CAST(SUM(total_quantity) AS FLOAT), 0) AS FLOAT)` |
| Product Mix % | `CAST(CAST(SUM(total_exc_vat_price) AS FLOAT) / NULLIF(CAST(SUM(SUM(total_exc_vat_price)) OVER () AS FLOAT), 0) * 100 AS FLOAT)` — ใช้กับ GROUP BY product |
| Member Sales | `SUM(CASE WHEN member_type = 'Member' THEN total_exc_vat_price ELSE 0 END)` |
| Non-Member Sales | `SUM(CASE WHEN member_type = 'Non-Member' THEN total_exc_vat_price ELSE 0 END)` |
| Member Sales % | `CAST(CAST(SUM(CASE WHEN member_type = 'Member' THEN total_exc_vat_price ELSE 0 END) AS FLOAT) / NULLIF(CAST(SUM(total_exc_vat_price) AS FLOAT), 0) * 100 AS FLOAT)` |
| Non-Member Sales % | `CAST(CAST(SUM(CASE WHEN member_type = 'Non-Member' THEN total_exc_vat_price ELSE 0 END) AS FLOAT) / NULLIF(CAST(SUM(total_exc_vat_price) AS FLOAT), 0) * 100 AS FLOAT)` |
| Member ATV | `CAST(CAST(SUM(CASE WHEN member_type = 'Member' THEN total_exc_vat_price ELSE 0 END) AS FLOAT) / NULLIF(CAST(SUM(member_count) AS FLOAT), 0) AS FLOAT)` |
| Non-Member ATV | `CAST(CAST(SUM(CASE WHEN member_type = 'Non-Member' THEN total_exc_vat_price ELSE 0 END) AS FLOAT) / NULLIF(CAST(SUM(ticket_count) - SUM(member_count) AS FLOAT), 0) AS FLOAT)` |
| Member UPT | `CAST(CAST(SUM(CASE WHEN member_type = 'Member' THEN total_quantity ELSE 0 END) AS FLOAT) / NULLIF(CAST(SUM(member_count) AS FLOAT), 0) AS FLOAT)` |
| Non-Member UPT | `CAST(CAST(SUM(CASE WHEN member_type = 'Non-Member' THEN total_quantity ELSE 0 END) AS FLOAT) / NULLIF(CAST(SUM(ticket_count) - SUM(member_count) AS FLOAT), 0) AS FLOAT)` |
| YoY Growth % | `CAST((FY27 - FY26) / NULLIF(FY26, 0) * 100 AS FLOAT)` |

### 🔧 Formula Updates (2026-07-24)
- **ATV**: Fixed to exclude returns (filter ticket_count > 0) — Result: -40% vs old formula
- **UPT**: Fixed to exclude returns (filter ticket_count > 0) — Result: -50% vs old formula
- **Member Ticket %**: ใช้ `SUM(member_count)` แทน `CASE WHEN member_type` — แม่นยำกว่า
- **Member/Non-Member ATV/UPT**: ใช้ `member_count` เป็นตัวหารสำหรับ Member และ `ticket_count - member_count` สำหรับ Non-Member
- **Product Mix %**: สูตรใหม่ ใช้ window function `SUM() OVER ()` หา Total โดยไม่ต้อง JOIN
- **Note**: ทุกสูตรใช้ CAST AS FLOAT บนตัวเศษและตัวส่วนก่อนหาร

## Step 3 — ดึง KPI แยกตาม Main Channel

แยก `main_channel` (OFFLINE / ONLINE) — ใช้ query แยกจาก Step 2
- Use corrected ATV & UPT formulas above for each channel

## Step 4 — ดึง KPI แยกตาม Channel Store

แยก `channel_store` — เรียงตาม Net Sales สูงสุด — แสดง Top 10
- Use corrected ATV & UPT formulas above for each channel store

## Step 5 — สร้าง Response

### โครงสร้างคำตอบ

**Headline** — 1 บรรทัด ระบุยอดรวม + YoY%

**ตารางที่ 1: KPI Summary (Organization Level)**

| KPI | FY27 | FY26 | Change |
|-----|------|------|--------|

**ตารางที่ 2: KPI by Main Channel**

| Channel | Net Sales FY27 | Net Sales FY26 | YoY% | Discount% | Margin% | ATV | UPT |
|---------|---------------|---------------|------|-----------|---------|-----|-----|

**ตารางที่ 3: Net Sales by Channel Store (Top 10)**

| Channel Store | Net Sales FY27 | Net Sales FY26 | YoY% | Margin% |
|---------------|---------------|---------------|------|---------|

**3 Key Takeaways**

ระบุ 3 ประเด็นที่ส่งผลต่อยอดขายมากที่สุด โดยต้องมีข้อมูลรองรับ:
1. สิ่งที่ทำได้ดีที่สุด
2. สิ่งที่ควรติดตาม
3. แนวทางดำเนินการต่อ

**Data Footer**

`📊 Data: mcg_aiplatform_sales | Period: [ระบุช่วงวันที่] | Last data: [MAX(sold_date) ที่ได้จากข้อมูลจริง]`

---

# Output Rules (เพิ่มเติมจากกฎหลัก)

- ใช้ไม่เกิน 3 ตาราง
- KPI ทุกตัวต้อง `CAST(... AS FLOAT)` ก่อน `NULLIF`
- ใช้ emoji status ตาม KPI Thresholds ในกฎหลัก
- ASP = Average Selling Price = Net Sales ÷ Qty
- ห้ามรวม Marketplace ในการคำนวณ Member % (ตามกฎหลัก Section 9)
- ✅ **ATV & UPT**: Filter ticket_count > 0 to exclude returns (updated 2026-07-24)