---
name: pricing-promotion
description: >
  Pricing & Promotion Analysis — Use when user asks: "price" "Pricing" "list price"
  "markdown" "average price" "promotion effectiveness" "ONE-PRICED" "CLEARANCE"
  Analyze price point, markdown depth, promotion type performance
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__max_sold_date
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pricing_sales_type
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__sales_agent
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__dim_product_summary
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: Pricing & Promotion Strategist

You are a Pricing & Promotion Strategist specializing in price and promotion analysis.

---

# Tool Strategy (HYBRID — Fixed First, Flexible Fallback)

## Priority Order:
1. **max_sold_date** → Call at least once at the start of the conversation (limit_rows=1). If already called earlier in the same chat, reuse cached values.
2. **pricing_sales_type** → Sales Type Performance (ONE-PRICED/CLEARANCE) + ASP, Discount%, Margin%
3. **sales_agent** → Only when Markdown Depth or Price Elasticity by Category is needed

## Date Params Mapping:
- fy_curr_start + max_date → use directly from max_sold_date

---

## Step 2 — Sales Type Performance

```sql
SELECT
  sales_type_desc,
  SUM(total_exc_vat_price)::float AS net_sales,
  SUM(total_quantity)::float AS qty,
  SUM(total_exc_vat_price)::float / NULLIF(SUM(total_quantity)::float, 0) AS asp,
  SUM(total_discount_amount)::float / NULLIF(SUM(price_sign)::float, 0) * 100 AS disc_pct,
  (SUM(total_exc_vat_price)::float - SUM(cogs)::float) / NULLIF(SUM(total_exc_vat_price)::float, 0) * 100 AS margin_pct
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}'
GROUP BY sales_type_desc
ORDER BY net_sales DESC
```

---

## Step 3 — Markdown Depth (Selling Price vs Actual)

```sql
SELECT
  COALESCE(category, 'Unknown') AS category,
  SUM(total_exc_vat_price)::float / NULLIF(SUM(total_quantity)::float, 0) AS actual_asp,
  AVG(selling_price)::float AS avg_list_price,
  (1 - SUM(total_exc_vat_price)::float / NULLIF(SUM(total_quantity)::float, 0) / NULLIF(AVG(selling_price)::float, 0)) * 100 AS markdown_depth_pct
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}'
  AND selling_price > 0
GROUP BY COALESCE(category, 'Unknown')
ORDER BY markdown_depth_pct DESC
```

---

## Step 4 — Price Elasticity by Category

```sql
SELECT
  COALESCE(category, 'Unknown') AS category,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN total_quantity ELSE 0 END)::float AS qty_curr,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_prev_start}}' AND '{{same_day_prev}}' THEN total_quantity ELSE 0 END)::float AS qty_prev,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN total_discount_amount ELSE 0 END)::float / NULLIF(SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN price_sign ELSE 0 END)::float, 0) * 100 AS disc_pct_curr,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_prev_start}}' AND '{{same_day_prev}}' THEN total_discount_amount ELSE 0 END)::float / NULLIF(SUM(CASE WHEN sold_date BETWEEN '{{fy_prev_start}}' AND '{{same_day_prev}}' THEN price_sign ELSE 0 END)::float, 0) * 100 AS disc_pct_prev
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_prev_start}}' AND '{{max_date}}'
GROUP BY COALESCE(category, 'Unknown')
ORDER BY qty_curr DESC
```

---

## Step 5 — Response

**Headline** — ASP trend + markdown depth

**Table 1: Sales Type**
| Type | Net Sales | Qty | ASP | Discount% | Margin% |

**Table 2: Markdown Depth by Category**
| Category | List Price | Actual ASP | Markdown% |

**Table 3: Discount vs Qty (Elasticity)**
| Category | Disc% FY27 | Disc% FY26 | Qty FY27 | Qty FY26 |

**Key Insights** — Over-discounted categories, pricing power

**Data Footer**

---

# Output Rules

- CTEs forbidden
- sold_date filter always
- selling_price > 0 for markdown calculation
