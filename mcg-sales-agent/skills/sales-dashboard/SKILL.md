---
name: sales-dashboard
description: >
  Sales Performance Dashboard Overview v2 — สรุปภาพรวมสำหรับผู้บริหาร
  ใช้เมื่อผู้ใช้ถาม: "ภาพรวม" "Dashboard" "KPI ทั้งหมด" "สรุปผู้บริหาร" "Overall performance"
  คำนวณ 12 KPI พร้อม 3 Key Takeaways
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_execute_sql
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_describe_table
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_list_tables
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
| Net Sales | `SUM(total_exc_vat_price)::float` |
| Discount% | `SUM(total_discount_amount)::float / NULLIF(SUM(price_sign)::float, 0) * 100` |
| Margin% | `(SUM(total_exc_vat_price)::float - SUM(cogs)::float) / NULLIF(SUM(total_exc_vat_price)::float, 0) * 100` |
| Tickets | `SUM(ticket_count)` |
| **ATV** | 🚫 ห้ามใช้ CASE WHEN — `SUM(total_exc_vat_price)::float / NULLIF(SUM(ticket_count)::float, 0)` |
| **UPT** | 🚫 ห้ามใช้ CASE WHEN — `SUM(total_quantity)::float / NULLIF(SUM(ticket_count)::float, 0)` |
| ASP | `SUM(total_exc_vat_price)::float / NULLIF(SUM(total_quantity)::float, 0)` |
| Member Ticket% | ใช้ `member_count` — `SUM(member_count)::float / NULLIF(SUM(ticket_count)::float, 0) * 100` |
| **Member Sales%** (FIXED) | ไม่รวม Marketplace — `SUM(CASE WHEN member_type='Member' AND channel_store<>'Marketplace' THEN total_exc_vat_price ELSE 0 END)::float / NULLIF(SUM(CASE WHEN channel_store<>'Marketplace' THEN total_exc_vat_price ELSE 0 END)::float, 0) * 100` |
| Non-Member Sales% | `SUM(CASE WHEN member_type='Non-Member' AND channel_store<>'Marketplace' THEN total_exc_vat_price ELSE 0 END)::float / NULLIF(SUM(CASE WHEN channel_store<>'Marketplace' THEN total_exc_vat_price ELSE 0 END)::float, 0) * 100` |
| Member ATV | `SUM(total_exc_vat_price)::float / NULLIF(SUM(member_count)::float, 0)` |
| Non-Member ATV | `SUM(total_exc_vat_price)::float / NULLIF((SUM(ticket_count) - SUM(member_count))::float, 0)` |
| YoY% | `(FY27 - FY26) / NULLIF(FY26, 0) * 100` |

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
- CAST AS FLOAT → ใช้ `::float` ทุก KPI
- 🟢🟡🔴 ตาม Thresholds
- ATV/UPT ใช้ SUM ตรง ๆ — 🚫 ห้ามใช้ CASE WHEN ticket_count > 0
- Member% ไม่รวม Marketplace
- ใช้ member_count สำหรับ Member tickets

