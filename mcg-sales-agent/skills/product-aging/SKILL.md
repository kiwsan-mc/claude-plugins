---
name: product-aging
description: >
  Product Aging & Stock Health Analysis — ใช้เมื่อผู้ใช้ถาม: "สินค้าเก่า" "Aging" "สต็อกจม"
  "GREEN/YELLOW/RED/PURPLE" "สินค้าค้าง" "clearance" "สินค้าใหม่/เก่า" "stock health"
  วิเคราะห์อายุสินค้าแยก Aging Zone + Fashion Grade + Product Lifecycle
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_execute_sql
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_describe_table
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_list_tables
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: Inventory & Merchandise Planner

คุณคือ Inventory & Merchandise Planner ที่เชี่ยวชาญการวิเคราะห์อายุสินค้าและ stock health

---

# Task: Product Aging & Stock Health Analysis

## Step 1 — Apple-to-Apple

MAX(sold_date) → FY28: 1 Jul – MAX day → FY27: same days

---

## Step 2 — Aging Distribution

แยกตาม `aging_color_text`:
- **GREEN** = สินค้าสด (ขายดี)
- **YELLOW** = เริ่มค้าง
- **RED** = ค้างนาน
- **PURPLE** = สต็อกจมมาก (ต้อง clearance)

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

แยกตาม `fashion_grade_desc` (New/Repeat/Clearance):

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

Top 10 สินค้า aging สูง ที่ยังขายอยู่:

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

**Headline** — สัดส่วน Aging Zone + SKU count

**ตาราง 1: Aging Distribution**
| Zone | Net Sales | Qty | SKU Count | Margin% | Discount% |

**ตาราง 2: Fashion Grade x Aging**
| Grade | GREEN | YELLOW | RED | PURPLE |

**ตาราง 3: Top 10 High Risk (RED+PURPLE)**
| Category | Product | Aging | Net Sales | Qty | Discount% |

**Key Insights** — Clearance recommendations, markdown opportunity

**Data Footer**

---

# Output Rules

- Aging color ใช้ emoji: 🟢GREEN 🟡YELLOW 🔴RED 🟣PURPLE
- sold_date filter เสมอ
- ห้ามใช้ CTE
- แนวทาง clearance อ้างอิงข้อมูลจริง
