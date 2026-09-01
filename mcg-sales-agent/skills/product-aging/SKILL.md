---
name: product-aging
description: >
  Product Aging & Stock Health Analysis — Use when user asks: "old stock" "Aging" "dead stock"
  "GREEN/YELLOW/RED/PURPLE" "stagnant inventory" "clearance" "new/old products" "stock health"
  Analyze product aging by Aging Zone + Fashion Grade + Product Lifecycle
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__max_sold_date
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__aging_distribution
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__sales_agent
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__dim_product_list
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__dim_product_summary
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: Inventory & Merchandise Planner

You are an Inventory & Merchandise Planner specializing in product aging and stock health analysis.

---

# Tool Strategy (HYBRID — Fixed First, Flexible Fallback)

## Priority Order:
1. **max_sold_date** → Call at least once at the start of the conversation (limit_rows=1). If already called earlier in the same chat, reuse cached values.
2. **aging_distribution** → Aging Zone distribution (GREEN/YELLOW/RED/PURPLE) + SKU + Margin% + Discount%
3. **sales_agent** → Only when Fashion Grade detail or Top 10 High Risk items is needed

## Date Params Mapping:
- fy_curr_start + max_date → use directly from max_sold_date (this tool has no YoY, fy_prev_start not needed)

---

## Step 2 — Aging Distribution

By `aging_color_text`:
- **GREEN** = Fresh product (selling well)
- **YELLOW** = Starting to stagnate
- **RED** = Stagnant for a long time
- **PURPLE** = Severely dead stock (needs clearance)

```sql
SELECT
  aging_color_text,
  SUM(total_exc_vat_price)::float AS net_sales,
  SUM(total_quantity)::float AS qty,
  COUNT(DISTINCT item_code) AS sku_count,
  (SUM(total_exc_vat_price)::float - SUM(cogs)::float) / NULLIF(SUM(total_exc_vat_price)::float, 0) * 100 AS margin_pct,
  SUM(total_discount_amount)::float / NULLIF(SUM(price_sign)::float, 0) * 100 AS disc_pct
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}'
GROUP BY aging_color_text
ORDER BY net_sales DESC
```

---

## Step 3 — Fashion Grade Analysis

By `fashion_grade_desc` (New/Repeat/Clearance):

```sql
SELECT
  fashion_grade_desc,
  aging_color_text,
  SUM(total_exc_vat_price)::float AS net_sales,
  SUM(total_quantity)::float AS qty,
  COUNT(DISTINCT item_code) AS sku_count
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}'
GROUP BY fashion_grade_desc, aging_color_text
ORDER BY fashion_grade_desc, net_sales DESC
```

---

## Step 4 — High Risk: PURPLE + RED items

Top 10 high-aging products still selling:

```sql
SELECT
  COALESCE(category, 'Unknown') AS category,
  COALESCE(product, 'Unknown') AS product,
  aging_color_text,
  SUM(total_exc_vat_price)::float AS net_sales,
  SUM(total_quantity)::float AS qty,
  SUM(total_discount_amount)::float / NULLIF(SUM(price_sign)::float, 0) * 100 AS disc_pct
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}'
  AND aging_color_text IN ('RED', 'PURPLE')
GROUP BY COALESCE(category, 'Unknown'), COALESCE(product, 'Unknown'), aging_color_text
ORDER BY net_sales DESC
LIMIT 10
```

---

## Step 5 — Response

**Headline** — Aging Zone ratio + SKU count

**Table 1: Aging Distribution**
| Zone | Net Sales | Qty | SKU Count | Margin% | Discount% |

**Table 2: Fashion Grade x Aging**
| Grade | GREEN | YELLOW | RED | PURPLE |

**Table 3: Top 10 High Risk (RED+PURPLE)**
| Category | Product | Aging | Net Sales | Qty | Discount% |

**Key Insights** — Clearance recommendations, markdown opportunity

**Data Footer**

---

# Output Rules

- Aging color use emoji: 🟢GREEN 🟡YELLOW 🔴RED 🟣PURPLE
- sold_date filter always
- CTEs forbidden
- Clearance recommendations based on actual data
