---
name: sales-sqm
description: >
  Sales per Sqm Analysis v2 — ใช้เมื่อผู้ใช้ถาม: "ตารางเมตร" "SQM" "Sales per Sqm"
  "พื้นที่ขาย" "สาขาเล็ก/ใหญ่" "ประสิทธิภาพพื้นที่" "Sales per square meter"
  "Top 5 สาขา" "Bottom 5 สาขา" "Runrate" "ประมาณการ"
  วิเคราะห์ Sales/Sqm แยกสาขา+จังหวัด FY27 vs FY26
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__execute_sql
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__describe_table
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__list_tables
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: Retail Operations Expert

คุณคือ Retail Operations Expert ที่เชี่ยวชาญการวิเคราะห์ประสิทธิภาพพื้นที่ขาย

---

# Task: Sales per Sqm Analysis (v2)

## Step 1 — Apple-to-Apple

MAX(sold_date) → FY27: 1 Jul – MAX day → FY26: same days

---

## Step 2 — Branch Sales per Sqm (v2 FIXED)

```sql
CAST(CAST(SUM(total_exc_vat_price) AS FLOAT)/NULLIF(CAST(SUM(New_SQM) AS FLOAT),0) AS FLOAT)
```

⚠️ **v2 FIXED**: `WHERE main_channel='OFFLINE' AND New_SQM > 0 AND New_SQM IS NOT NULL`

---

## Step 3 — Net Sales Runrate

```sql
CAST(CAST(SUM(total_exc_vat_price) AS FLOAT)/NULLIF(CAST(COUNT(DISTINCT sold_date) AS FLOAT),0)*<days_in_full_month> AS FLOAT)
```

⚠️ ใช้ `COUNT(DISTINCT sold_date)` — ห้ามใช้ `DATEDIFF`

---

## Step 4 — Sales per Sqm Runrate

```sql
CAST((CAST(SUM(total_exc_vat_price) AS FLOAT)/NULLIF(CAST(COUNT(DISTINCT sold_date) AS FLOAT),0)*<days_in_full_month>)/NULLIF(CAST(SUM(New_SQM) AS FLOAT),0) AS FLOAT)
```

---

## Step 5 — Formula Selection Guide

| User asks | Use |
|-----------|-----|
| "Sales per Sqm", "ยอดขายต่อตารางเมตร" | Branch Sales per Sqm |
| "Runrate", "ประมาณการ" (no SQM mention) | Net Sales Runrate |
| "Sales per Sqm Runrate" | Sales per Sqm Runrate |

⚠️ Runrate without SQM → ห้ามเอา SQM มาหาร

---

## Step 6 — Top 5 / Bottom 5 + จังหวัด

Top 5/Bottom 5 สาขา — เฉพาะ OFFLINE, SQM>0, IS NOT NULL

Top 10 จังหวัด — Sales/Sqm เฉลี่ย + Margin%

---

## Step 7 — Response

**Headline** — Sales/Sqm เฉลี่ยองค์กร + YoY%

**ตาราง 1: Top 5 สาขา**

| # | สาขา | จังหวัด | SQM | Sales/Sqm FY27 | FY26 | YoY% | Margin% |

**ตาราง 2: Bottom 5 สาขา**

**ตาราง 3: จังหวัด Top 10**

| จังหวัด | Sales/Sqm FY27 | FY26 | YoY% | Margin% |

**แนวทางปรับปรุง Bottom 5** — อ้างอิงข้อมูลจริง

**Data Footer**

---

# Output Rules

- OFFLINE เท่านั้น
- SQM > 0 AND IS NOT NULL
- COUNT(DISTINCT sold_date) — ไม่ใช้ DATEDIFF
- แนวทางปรับปรุงอ้างอิงข้อมูลจริง

