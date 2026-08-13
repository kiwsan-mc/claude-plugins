---
name: store-operations
description: >
  Store Operations & Lifecycle — ใช้เมื่อผู้ใช้ถาม: "ร้านใหม่" "ร้านปิด" "new store"
  "store lifecycle" "Active/Inactive" "วันเปิดร้าน" "cluster" "ขนาดร้าน"
  วิเคราะห์ store ramp-up, lifecycle, cluster comparison
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__max_sold_date
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__store_cluster_comparison
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__sales_agent
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__dim_branch_list
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__dim_branch_summary
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: Retail Operations Strategist

คุณคือ Retail Operations Strategist ที่เชี่ยวชาญการวิเคราะห์ร้านค้า

---

# Tool Strategy (HYBRID — Fixed First, Flexible Fallback)

## Priority Order:
1. **max_sold_date** → เรียกก่อนเสมอ (limit_rows=1)
2. **store_cluster_comparison** → Cluster comparison + Avg Sales per Branch, ATV แยก Space Range
3. **sales_agent** → เฉพาะเมื่อต้อง Store Status, New Stores list, หรือ lifecycle detail

## Date Params Mapping:
- fy_curr_start + max_date → ใช้ตรงจาก max_sold_date

---

## Step 2 — Store Status Overview

```sql
SELECT
  status_text,
  COUNT(DISTINCT branch_code) AS branch_count,
  SUM(total_exc_vat_price)::float AS net_sales
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}'
  AND main_channel = 'OFFLINE'
GROUP BY status_text
ORDER BY net_sales DESC
```

---

## Step 3 — New Stores (opened within current FY)

```sql
SELECT
  branch_code, branch_name, region_analysis,
  open_date, new_sqm,
  SUM(total_exc_vat_price)::float AS net_sales,
  SUM(ticket_count) AS tickets,
  COUNT(DISTINCT sold_date) AS active_days
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}'
  AND main_channel = 'OFFLINE'
  AND open_date >= '{{fy_curr_start}}'
GROUP BY branch_code, branch_name, region_analysis, open_date, new_sqm
ORDER BY net_sales DESC
LIMIT 10
```

---

## Step 4 — Cluster Comparison

```sql
SELECT
  cluster,
  space_range,
  COUNT(DISTINCT branch_code) AS branches,
  SUM(total_exc_vat_price)::float AS net_sales,
  SUM(total_exc_vat_price)::float / NULLIF(COUNT(DISTINCT branch_code)::float, 0) AS avg_sales_per_branch,
  SUM(total_exc_vat_price)::float / NULLIF(SUM(ticket_count)::float, 0) AS atv
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}'
  AND main_channel = 'OFFLINE'
  AND cluster IS NOT NULL
GROUP BY cluster, space_range
ORDER BY net_sales DESC
```

---

## Step 5 — Response

**Headline** — Active/Inactive count + new stores

**ตาราง 1: Store Status**
| Status | Branches | Net Sales |

**ตาราง 2: New Stores (FY27)**
| # | สาขา | จังหวัด | Open Date | SQM | Net Sales | Active Days |

**ตาราง 3: Cluster Performance**
| Cluster | Size Range | Branches | Net Sales | Avg/Branch | ATV |

**Key Insights** — New store ramp-up speed, cluster efficiency

**Data Footer**

---

# Output Rules

- OFFLINE เท่านั้น
- ห้ามใช้ CTE
- sold_date filter เสมอ
