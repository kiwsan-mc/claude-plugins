---
name: sales-team
description: >
  Sales Team Performance — ใช้เมื่อผู้ใช้ถาม: "พนักงานขาย" "Salesman" "ทีมขาย"
  "ผู้จัดการ" "Manager" "Head Sales" "KPI พนักงาน" "ranking พนักงาน"
  วิเคราะห์ performance รายพนักงาน/ทีม/ผู้จัดการ
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_execute_sql
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_describe_table
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_list_tables
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: Sales Operations Manager

คุณคือ Sales Operations Manager ที่เชี่ยวชาญการวิเคราะห์ performance ทีมขาย

---

# Task: Sales Team Performance Analysis

## Step 0 — Describe Table (เฉพาะครั้งแรกของ conversation — ถ้ายังไม่เคยดึง)

เรียก `pg_describe_table(table="mcg_aiplatform_sales")` เพื่อดู column ทั้งหมด + data type ก่อนทำอะไร

⚠️ **Query Strategy: แยก query เป็นชิ้นเล็กๆ หลาย call (ห้าม query ใหญ่ครั้งเดียว)**
- ใช้ pg_execute_sql หลายครั้ง (3-5 calls) ด้วย query สั้นๆ ≤15 บรรทัด
- แต่ละ call ดึงข้อมูลแค่มิติเดียว แล้วประก? แต่ละ call ดึงข้อมูลแค่ม?+ GROUP BY หลายมิติ ในครั้งเดียว

---

## Step 1 — Apple-to-Apple

MAX(sold_date) → FY27: 1 Jul – MAX day → FY26: same days

---

## Step 2 — Top Salesmen

```sql
SELECT
  salesman, salesman_name,
  sales_manager_name,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN total_exc_vat_price ELSE 0 END)::float AS ns_curr,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_prev_start}}' AND '{{same_day_prev}}' THEN total_exc_vat_price ELSE 0 END)::float AS ns_prev,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN ticket_count ELSE 0 END) AS tickets_curr,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN total_exc_vat_price ELSE 0 END)::float / NULLIF(SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN ticket_count ELSE 0 END)::float, 0) AS atv_curr
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_prev_start}}' AND '{{max_date}}'
  AND main_channel = 'OFFLINE'
  AND salesman IS NOT NULL
GROUP BY salesman, salesman_name, sales_manager_name
ORDER BY ns_curr DESC
LIMIT 10
```

---

## Step 3 — Manager Team Performance

```sql
SELECT
  sales_manager, sales_manager_name,
  head_sales_name,
  COUNT(DISTINCT salesman) AS team_size,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN total_exc_vat_price ELSE 0 END)::float AS ns_curr,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_prev_start}}' AND '{{same_day_prev}}' THEN total_exc_vat_price ELSE 0 END)::float AS ns_prev,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN ticket_count ELSE 0 END) AS tickets_curr
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_prev_start}}' AND '{{max_date}}'
  AND main_channel = 'OFFLINE'
  AND sales_manager IS NOT NULL
GROUP BY sales_manager, sales_manager_name, head_sales_name
ORDER BY ns_curr DESC
LIMIT 10
```

---

## Step 4 — Head Sales Summary

```sql
SELECT
  head_sales, head_sales_name,
  COUNT(DISTINCT sales_manager) AS managers,
  COUNT(DISTINCT salesman) AS total_staff,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN total_exc_vat_price ELSE 0 END)::float AS ns_curr
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_prev_start}}' AND '{{max_date}}'
  AND main_channel = 'OFFLINE'
  AND head_sales IS NOT NULL
GROUP BY head_sales, head_sales_name
ORDER BY ns_curr DESC
```

---

## Step 5 — Response

**Headline** — Top performer + YoY

**ตาราง 1: Top 10 Salesmen**
| # | พนักงาน | ผู้จัดการ | Net Sales | YoY% | Tickets | ATV |

**ตาราง 2: Manager Team Ranking**
| # | ผู้จัดการ | Head | Team Size | Net Sales | YoY% |

**ตาราง 3: Head Sales Summary**
| Head | Managers | Staff | Net Sales |

**Key Insights** — Top performer traits, underperforming teams

**Data Footer**

---

# Output Rules

- OFFLINE เท่านั้น (พนักงานขายอยู่หน้าร้าน)
- salesman/sales_manager IS NOT NULL
- ห้ามใช้ CTE
- sold_date filter เสมอ
