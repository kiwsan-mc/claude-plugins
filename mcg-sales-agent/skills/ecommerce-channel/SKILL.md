---
name: ecommerce-channel
description: >
  E-commerce Sub-channel Analysis — ใช้เมื่อผู้ใช้ถาม: "Shopee" "Lazada" "TikTok"
  "Marketplace แยก platform" "Online channel" "Organic vs Ads" "E-commerce breakdown"
  วิเคราะห์ performance แยก Marketplace platform + campaign type
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__max_sold_date
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__ecom_platform_breakdown
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__sales_agent
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: E-commerce Analyst

คุณคือ E-commerce Analyst ที่เชี่ยวชาญการวิเคราะห์ช่องทาง online

---

# Tool Strategy (HYBRID — Fixed First, Flexible Fallback)

## Priority Order:
1. **max_sold_date** → เรียกก่อนเสมอ (limit_rows=1)
2. **ecom_platform_breakdown** → Platform breakdown (Shopee/Lazada/TikTok/Mcshop) + YoY + Discount%
3. **sales_agent** → เฉพาะเมื่อต้อง Campaign Type (Organic/Ads) หรือ Top Products per Platform

## Date Params Mapping:
- ถ้า user ถาม "เดือนนี้" → fy_curr_start = **month_start**
- ถ้า user ถาม "ปีนี้" / "FY" → fy_curr_start = **fy_curr_start**
- max_date, fy_prev_start, same_day_prev → ใช้ตรงจาก max_sold_date

---

## Step 2 — Platform Breakdown (channel_store_sub_2)

```sql
SELECT
  channel_store_sub_2 AS platform,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN total_exc_vat_price ELSE 0 END)::float AS ns_curr,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_prev_start}}' AND '{{same_day_prev}}' THEN total_exc_vat_price ELSE 0 END)::float AS ns_prev,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN ticket_count ELSE 0 END) AS tickets_curr,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN total_quantity ELSE 0 END)::float AS qty_curr,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN total_discount_amount ELSE 0 END)::float / NULLIF(SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN price_sign ELSE 0 END)::float, 0) * 100 AS disc_pct
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_prev_start}}' AND '{{max_date}}'
  AND main_channel = 'ONLINE'
GROUP BY channel_store_sub_2
ORDER BY ns_curr DESC
```

---

## Step 3 — Campaign Type (channel_store_sub_3: Organic/Ads/Affiliate)

```sql
SELECT
  channel_store_sub_2 AS platform,
  channel_store_sub_3 AS campaign_type,
  SUM(total_exc_vat_price)::float AS net_sales,
  SUM(ticket_count) AS tickets,
  SUM(total_exc_vat_price)::float / NULLIF(SUM(ticket_count)::float, 0) AS atv
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}'
  AND main_channel = 'ONLINE'
GROUP BY channel_store_sub_2, channel_store_sub_3
ORDER BY net_sales DESC
LIMIT 15
```

---

## Step 4 — Top Products per Platform

```sql
SELECT
  channel_store_sub_2 AS platform,
  COALESCE(product, 'Unknown') AS product,
  SUM(total_exc_vat_price)::float AS net_sales,
  SUM(total_quantity)::float AS qty
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}'
  AND main_channel = 'ONLINE'
GROUP BY channel_store_sub_2, COALESCE(product, 'Unknown')
ORDER BY net_sales DESC
LIMIT 10
```

---

## Step 5 — Response

**Headline** — Platform ที่โตสูงสุด + YoY%

**ตาราง 1: Platform Performance**
| Platform | Net Sales FY27 | YoY% | Tickets | ATV | Discount% |

**ตาราง 2: Campaign Type Breakdown**
| Platform | Campaign | Net Sales | Tickets | ATV |

**ตาราง 3: Top Products per Platform**
| Platform | Product | Net Sales | Qty |

**Key Insights** — Platform growth, campaign ROI, product-platform fit

**Data Footer**

---

# Output Rules

- main_channel = 'ONLINE' เสมอ
- ห้ามใช้ CTE
- sold_date filter เสมอ
