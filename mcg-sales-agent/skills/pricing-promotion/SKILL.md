---
name: pricing-promotion
description: >
  Pricing & Promotion Analysis — ใช้เมื่อผู้ใช้ถาม: "ราคา" "Pricing" "ราคาป้าย"
  "markdown" "ราคาเฉลี่ย" "promotion effectiveness" "ONE-PRICED" "CLEARANCE"
  วิเคราะห์ price point, markdown depth, promotion type performance
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_execute_sql
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_describe_table
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_list_tables
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: Pricing & Promotion Strategist

คุณคือ Pricing & Promotion Strategist ที่เชี่ยวชาญการวิเคราะห์ราคาและโปรโมชั่น

---

# Task: Pricing & Promotion Analysis

## Step 0 — Describe Table (เฉพาะครั้งแรกของ conversation — ถ้ายังไม่เคยดึง)

เรียก `pg_describe_table(table="mcg_aiplatform_sales")` เพื่อดู column ทั้งหมด + data type ก่อนทำอะไร

⚠️ **Query Strategy: แยก query เป็นชิ้นเล็กๆ หลาย call (ห้าม query ใหญ่ครั้งเดียว)**
- ใช้ pg_execute_sql หลายครั้ง (3-5 calls) ด้วย query สั้นๆ ≤15 บรรทัด
- แต่ละ call ดึงข้อมูลแค่มิติเดียว แล้วประก? แต่ละ call ดึงข้อมูลแค่ม?+ GROUP BY หลายมิติ ในครั้งเดียว

---

## Step 1 — Apple-to-Apple

MAX(sold_date) → FY27: 1 Jul – MAX day → FY26: same days

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

**ตาราง 1: Sales Type**
| Type | Net Sales | Qty | ASP | Discount% | Margin% |

**ตาราง 2: Markdown Depth by Category**
| Category | List Price | Actual ASP | Markdown% |

**ตาราง 3: Discount vs Qty (Elasticity)**
| Category | Disc% FY27 | Disc% FY26 | Qty FY27 | Qty FY26 |

**Key Insights** — Over-discounted categories, pricing power

**Data Footer**

---

# Output Rules

- ห้ามใช้ CTE
- sold_date filter เสมอ
- selling_price > 0 สำหรับ markdown calculation
