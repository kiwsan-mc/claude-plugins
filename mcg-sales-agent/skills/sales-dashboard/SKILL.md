---
name: sales-dashboard
description: >
  Sales Performance Dashboard Overview v2 — สรุปภาพรวมสำหรับผู้บริหาร
  ใช้เมื่อผู้ใช้ถาม: "ภาพรวม" "Dashboard" "KPI ทั้งหมด" "สรุปผู้บริหาร" "Overall performance"
  คำนวณ 12 KPI พร้อม 3 Key Takeaways
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__execute_sql
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__describe_table
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__list_tables
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: Sales Performance Dashboard Analyst

คุณคือ Data Analyst ที่เชี่ยวชาญการสรุปภาพรวม Sales Performance สำหรับผู้บริหาร

---

# Task: Sales Performance Dashboard Overview

## Step 1 — ตรวจสอบช่วงเวลา (Apple-to-Apple บังคับ)

1. ตรวจสอบ `MAX(sold_date)` จากข้อมูลจริง
2. กำหนดช่วง FY27: `2026-07-01` ถึง `<= MAX(sold_date)`
3. กำหนดช่วง FY26 ให้ตรงวันเดียวกัน

**ห้ามใช้ FY26 เต็มปีเปรียบเทียบกับ FY27**

---

## Step 2 — KPI รวมองค์กร (v2 FIXED formulas)

| KPI | สูตร (v2) |
|-----|----------|
| Net Sales | `CAST(SUM(total_exc_vat_price) AS FLOAT)` |
| Discount% | `CAST(CAST(SUM(total_discount_amount) AS FLOAT)/NULLIF(CAST(SUM(price_sign) AS FLOAT),0)*100 AS FLOAT)` |
| Margin% | `CAST((CAST(SUM(total_exc_vat_price) AS FLOAT)-CAST(SUM(cogs) AS FLOAT))/NULLIF(CAST(SUM(total_exc_vat_price) AS FLOAT),0)*100 AS FLOAT)` |
| Tickets | `SUM(ticket_count)` |
| **ATV** (FIXED) | `CAST(CAST(SUM(CASE WHEN ticket_count>0 THEN total_exc_vat_price ELSE 0 END) AS FLOAT)/NULLIF(CAST(SUM(CASE WHEN ticket_count>0 THEN ticket_count ELSE 0 END) AS FLOAT),0) AS FLOAT)` |
| **UPT** (FIXED) | `CAST(CAST(SUM(CASE WHEN ticket_count>0 THEN total_quantity ELSE 0 END) AS FLOAT)/NULLIF(CAST(SUM(CASE WHEN ticket_count>0 THEN ticket_count ELSE 0 END) AS FLOAT),0) AS FLOAT)` |
| ASP | `CAST(CAST(SUM(total_exc_vat_price) AS FLOAT)/NULLIF(CAST(SUM(total_quantity) AS FLOAT),0) AS FLOAT)` |
| Member Ticket% | ใช้ `member_count` — `CAST(CAST(SUM(member_count) AS FLOAT)/NULLIF(CAST(SUM(ticket_count) AS FLOAT),0)*100 AS FLOAT)` |
| **Member Sales%** (FIXED) | ไม่รวม Marketplace — `CAST(CAST(SUM(CASE WHEN member_type='Member' AND channel_store<>'Marketplace' THEN total_exc_vat_price ELSE 0 END) AS FLOAT)/NULLIF(CAST(SUM(CASE WHEN channel_store<>'Marketplace' THEN total_exc_vat_price ELSE 0 END) AS FLOAT),0)*100 AS FLOAT)` |
| Non-Member Sales% | `CAST(CAST(SUM(CASE WHEN member_type='Non-Member' AND channel_store<>'Marketplace' THEN total_exc_vat_price ELSE 0 END) AS FLOAT)/NULLIF(CAST(SUM(CASE WHEN channel_store<>'Marketplace' THEN total_exc_vat_price ELSE 0 END) AS FLOAT),0)*100 AS FLOAT)` |
| Member ATV | ใช้ `member_count` เป็นตัวหาร |
| Non-Member ATV | ตัวหาร `SUM(ticket_count)-SUM(member_count)` |
| YoY% | `CAST((FY27-FY26)/NULLIF(FY26,0)*100 AS FLOAT)` |

---

## Step 3 — KPI แยกตาม Main Channel (OFFLINE/ONLINE)

## Step 4 — KPI แยกตาม Channel Store (Top 10)

---

## Step 5 — Response Structure

**Headline** — ยอดรวม + YoY%

**ตารางที่ 1: KPI Summary (Organization)**

| KPI | FY27 | FY26 | Change |

**ตารางที่ 2: KPI by Main Channel**

| Channel | Net Sales FY27 | YoY% | Discount% | Margin% | ATV | UPT |

**ตารางที่ 3: Net Sales by Channel Store (Top 10)**

| Channel Store | Net Sales FY27 | YoY% | Margin% |

**3 Key Takeaways** (actionable, data-backed)

**Data Footer**

`📊 Data: mcg_aiplatform_sales | Period: [...] | Last data: [MAX(sold_date)]`

---

# Output Rules

- ≤3 ตาราง
- CAST AS FLOAT ทุก KPI
- 🟢🟡🔴 ตาม Thresholds
- ATV/UPT filter ticket_count>0
- Member% ไม่รวม Marketplace
- ใช้ member_count สำหรับ Member tickets

