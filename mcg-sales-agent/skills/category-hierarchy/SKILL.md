---
name: category-hierarchy
description: >
  Category Hierarchy & Assortment — ใช้เมื่อผู้ใช้ถาม: "MCL" "hierarchy" "product group"
  "sub brand" "Denim" "Fashion" "assortment mix" "สัดส่วน category"
  วิเคราะห์ MCL hierarchy drill-down, product group performance
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__max_sold_date
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__mcl_hierarchy
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__sales_agent
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: Category Manager

คุณคือ Category Manager ที่เชี่ยวชาญ assortment planning

---

# Tool Strategy (HYBRID — Fixed First, Flexible Fallback)

## Priority Order:
1. **max_sold_date** → เรียกก่อนเสมอ (limit_rows=1)
2. **mcl_hierarchy** → MCL Hierarchy drill-down (Level 1-4) + Net Sales, Qty, SKU Count
3. **sales_agent** → เฉพาะเมื่อต้อง Product Group YoY, Sub Brand mix, หรือ specific MCL filter

## Date Params Mapping:
- fy_curr_start + max_date → ใช้ตรงจาก max_sold_date

---

## Step 2 — MCL Hierarchy (Level 1-4)

```sql
SELECT
  mcl1_text AS level1,
  mcl2_text AS level2,
  mcl3_text AS level3,
  mcl4_text AS level4,
  SUM(total_exc_vat_price)::float AS net_sales,
  SUM(total_quantity)::float AS qty,
  COUNT(DISTINCT item_code) AS sku_count
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}'
GROUP BY mcl1_text, mcl2_text, mcl3_text, mcl4_text
ORDER BY net_sales DESC
LIMIT 15
```

---

## Step 3 — Product Group Performance

```sql
SELECT
  product_group_text,
  product_group_text_2,
  sub_brand_text,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN total_exc_vat_price ELSE 0 END)::float AS ns_curr,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_prev_start}}' AND '{{same_day_prev}}' THEN total_exc_vat_price ELSE 0 END)::float AS ns_prev,
  COUNT(DISTINCT item_code) AS sku_count
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_prev_start}}' AND '{{max_date}}'
  AND product_group_text IS NOT NULL
GROUP BY product_group_text, product_group_text_2, sub_brand_text
ORDER BY ns_curr DESC
LIMIT 10
```

---

## Step 4 — Sub Brand Mix

```sql
SELECT
  sub_brand_text,
  SUM(total_exc_vat_price)::float AS net_sales,
  SUM(total_quantity)::float AS qty,
  (SUM(total_exc_vat_price)::float - SUM(cogs)::float) / NULLIF(SUM(total_exc_vat_price)::float, 0) * 100 AS margin_pct,
  SUM(total_discount_amount)::float / NULLIF(SUM(price_sign)::float, 0) * 100 AS disc_pct
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}'
  AND sub_brand_text IS NOT NULL
GROUP BY sub_brand_text
ORDER BY net_sales DESC
```

---

## Step 5 — Response

**Headline** — Top MCL path + sub brand insight

**ตาราง 1: MCL Hierarchy**
| L1 | L2 | L3 | L4 | Net Sales | Qty | SKU |

**ตาราง 2: Product Group + YoY**
| Group | Sub Group | Sub Brand | Net Sales FY27 | YoY% | SKU |

**ตาราง 3: Sub Brand Mix**
| Sub Brand | Net Sales | Qty | Margin% | Discount% |

**Key Insights** — Category growth drivers, assortment gaps

**Data Footer**

---

# Output Rules

- ห้ามใช้ CTE
- sold_date filter เสมอ
- NULL → exclude
