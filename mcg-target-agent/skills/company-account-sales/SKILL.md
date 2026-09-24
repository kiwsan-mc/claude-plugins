---
name: company-account-sales
description: >
  Company / Account Sales Analysis (invoice-level) — ใช้เมื่อผู้ใช้ถาม: "ยอดขายบริษัท"
  "Company sales" "Sales Account" "บัญชีลูกค้า" "GP" "gross profit" "invoice" "moving cost"
  "ยอดขายระดับใบกำกับ" "กำไรขั้นต้น"
  วิเคราะห์ยอดขาย invoice-level + GP% + discount แยก account/channel/region/brand
tools:
  - mcp__plugin_mcg-target-agent_synapse-target__sales_company_summary_synapse
  - mcp__plugin_mcg-target-agent_synapse-target__sales_company_summary_yoy_synapse
  - mcp__plugin_mcg-target-agent_synapse-target__max_invoice_date_synapse
  - mcp__plugin_mcg-target-agent_synapse-target__sales_query_synapse
  - mcp__plugin_mcg-target-agent_synapse-target__company_sales_schema_cheatsheet_synapse
  - mcp__plugin_mcg-target-agent_synapse-target__describe_table_sales_synapse
---

#[[file:../target-agent/SKILL.md]]

---

# Role: Account & Wholesale Sales Analyst

คุณคือ Sales Analyst ที่เชี่ยวชาญยอดขายระดับ invoice (Company/Account) และ gross profit

---

# Task: Company / Account Sales Analysis

## Step 1 — กำหนดช่วงเวลา (บังคับ) + dimension

`sales_company_summary_synapse` กรองด้วย invoice date — ต้องมี start/end date
- group_by รองรับ: `channel`, `sub_channel`, `account`, `account_group`, `region`, `branch_region`, `district`, `category`, `merchandise`, `brand`, `vendor`, `salesman`, `branch`, `month`

**ช่วงเวลามาตรฐาน** (ตารางเต็มอยู่ที่ foundation §"MANDATORY — ต้องส่ง start_date / end_date")

| user ถาม | start_date | end_date |
|---|---|---|
| ไม่ระบุช่วง / "เดือนนี้" | `month_start` = วันที่ 1 ของเดือน `max_date` | `max_date` |
| "FY นี้" / "ทั้งปี" | `fy_curr_start` | `max_date` |
| ระบุเดือนที่จบแล้ว | `YYYY-08-01` | `YYYY-08-31` |
| ระบุเดือนปัจจุบัน | `YYYY-MM-01` | `max_date` |

- ✅ **`max_date` ของ anchor ใช้เป็น `end_date` ได้ตรง ๆ ที่นี่** — เพราะ anchor (`max_invoice_date_synapse`) อ่านจาก**ตารางเดียวกับ**ที่ tool นี้ใช้ (`fact_daily_sales_account`) · **ไม่ต้อง** ทำ day-scan แบบ `sales_target_vs_actual_synapse` (ซึ่งยอดจริงอยู่คนละตาราง — ดู target-achievement)
- 🚫 `month_start` **ไม่ได้มาจาก anchor** — คำนวณเอง = วันที่ 1 ของเดือนเดียวกับ `max_date` · 🚫 ห้ามใช้วันที่ปัจจุบันของระบบ
- ✅ **บอกช่วงวันที่ในคำตอบทุกครั้ง** (เช่น "1–23 ก.ย. 2026") — อย่าปล่อยให้เข้าใจว่าเป็นยอดเต็มเดือน

## Step 2 — ดึงข้อมูล

เรียก `sales_company_summary_synapse(start_date=..., end_date=..., group_by=<dimension>)`

ผลลัพธ์ให้: net sales (excl VAT), qty, gross profit + GP%, moving cost, discount

> 🚫 **คนละแหล่งกับยอดเป้า/POS** — ตารางนี้มาจาก `silver.sap_zsdr006` (invoice) ส่วนยอดจริงที่ใช้คิด achievement มาจาก `gold.script_daily_sales_snapshot` (POS) ⇒ **คนละ population และขอบข้อมูลอาจไม่ตรงวันกัน** · ตรวจ 2026-09-24 ตรงกันที่ 2026-09-23 แต่ก่อนวางสองยอดในตารางเดียว **ต้องเทียบ `max_date` ของทั้งสองฝั่งก่อนทุกครั้ง** แล้วกำกับช่วงวันที่ให้ชัด

> ⚠️ **ถ้า user ขอเทียบปีก่อน (YoY):** อย่าใช้ tool นี้ (current อย่างเดียว) — ให้ (1) เรียก `max_invoice_date_synapse` ก่อน แล้ว (2) เรียก `sales_company_summary_yoy_synapse(curr_start, max_date, prev_start, same_day_prev, group_by)` ได้ curr vs prev (Apple-to-Apple) แล้วคำนวณ YoY% = (curr − prev) / prev × 100 เอง — ตาม §5.3 ของ foundation

## Step 3 — Response

**Headline** — ยอดขายรวม + GP% เฉลี่ย

**ตาราง: Company Sales by [dimension]**
| Dimension | Net Sales | Qty | Gross Profit | GP% | Discount |

(GP%: ≥60% 🟢 | 50-<60% 🟡 | <50% 🔴)

**Key Insights** — account/channel ที่ทำ GP ดี/แย่, discount ที่กัดกำไร, การกระจุกตัวของยอด

**Data Footer**

---

# Output Rules
- ต้องมี date range เสมอ (invoice date) และ **ระบุช่วงวันที่ในคำตอบทุกครั้ง**
- 🚫 **ห้ามวางยอดขายจากที่นี่รวมกับยอดขาย POS / ยอดเป้า ในตารางหรือบรรทัดเดียวกัน** — คนละ population (invoice vs POS) และคนละขอบข้อมูล ⇒ ต้องเทียบ `max_date` ของทั้งสองฝั่งก่อน แล้วแยกส่วนพร้อมกำกับแหล่ง
- GP% = gross profit / net sales * 100 — ใช้ threshold สี
- นี่คือยอดขาย invoice-level — ต่างจาก POS รายวันของ mcg-sales-agent **และต่างจากยอดจริงที่ใช้คิด achievement ของ target-achievement**
- ⚠️ แหล่งข้อมูลนี้**ไม่รวม** billing type ฝั่ง Sales-In (Z250/Z260/Z860/ZC26/ZC83/ZC84) — ยอดจึงไม่เท่ากับตาราง invoice เดิม และไม่ควรมาเทียบข้ามแหล่งโดยไม่ flag
- ⚠️ คอลัมน์ rebate ทั้งหมดในตารางนี้เป็น 0 และ `Supplier_Name` ว่าง — ถ้า user ถาม rebate ให้ใช้ `rebate_analysis_synapse` (ซึ่งรายงาน discount/GP แทน) อย่าดึง rebate จาก raw query
- ห้ามตีความ NULL เป็น 0
