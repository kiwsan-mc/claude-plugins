---
name: discount-margin
description: >
  Discount & Margin Sensitivity v2 — ใช้เมื่อผู้ใช้ถาม: "กำไร" "Margin" "ส่วนลด" "Discount"
  "Profitability" "High Risk" "ส่วนลดสูง" "กำไรต่ำ" "ควบคุมส่วนลด"
  วิเคราะห์ Discount% vs Margin% แยก Category/Product Type พร้อม Zone 🟢🟡🔴
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__execute_sql
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__describe_table
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__list_tables
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: Financial & Planning Analyst

คุณคือ Financial & Planning Analyst ที่เชี่ยวชาญ Discount & Profitability

---

# Task: Discount & Margin Sensitivity Analysis (v2)

## Step 1 — Apple-to-Apple

MAX(sold_date) → FY27: 1 Jul – MAX day → FY26: same days

---

## Step 2 — Category Level

| KPI | สูตร (v2) |
|-----|----------|
| Net Sales | `CAST(SUM(total_exc_vat_price) AS FLOAT)` |
| Discount% | `CAST(CAST(SUM(total_discount_amount) AS FLOAT)/NULLIF(CAST(SUM(price_sign) AS FLOAT),0)*100 AS FLOAT)` |
| Margin% | `CAST((CAST(SUM(total_exc_vat_price) AS FLOAT)-CAST(SUM(cogs) AS FLOAT))/NULLIF(CAST(SUM(total_exc_vat_price) AS FLOAT),0)*100 AS FLOAT)` |

---


⚠️ **v2 Edge Cases:**

- `price_sign = 0` → Discount% จะเป็น NULL (หาร 0 ด้วย NULLIF) — แสดงเป็น "N/A" ไม่ใช่ 0%
- `cogs = NULL` → Margin% จะเป็น NULL — แสดงเป็น "N/A" ไม่ใช่ 0%
- `COALESCE(category, 'Unknown')` ใน GROUP BY

## Step 3 — Product Type Level

Group by `category`, `product` — เรียงตาม Discount% สูงสุด

### มิติเพิ่มเติมสำหรับ Drilldown

| Dimension | Column | ค่าตัวอย่าง | ใช้วิเคราะห์ |
|-----------|--------|------------|-------------|
| เกรดแฟชั่น | `Fashion_Grade_Desc` | Non-Repeat, Repeat, Re-Order | สินค้า Repeat/Re-Order ควรมี Margin ดีกว่า Non-Repeat — ถ้าไม่ใช่ = Discount สูงเกินไป |
| ราคาตั้ง vs ราคาขายจริง | `Selling_Price` vs `PriceAfterDiscount_AVG` | 1595 vs 390 | Gap Analysis — ดูว่า Discount จริงห่างจากราคาตั้งเท่าไร |

**การใช้งาน:**
- ถ้า user ถาม "Discount ตามเกรดสินค้า" → GROUP BY `Fashion_Grade_Desc` ดู Discount% และ Margin% แต่ละเกรด
- ถ้า user ถาม "ราคาป้าย vs ราคาขายจริง" → เปรียบเทียบ `AVG(Selling_Price)` กับ `AVG(PriceAfterDiscount_AVG)` ตาม category
- สินค้า Re-Order ที่ Discount% สูง = สัญญาณว่าอาจ over-discount สินค้าที่ควรขายได้ full price
- Cross: `Fashion_Grade_Desc` × `category` → หาว่า category ไหนที่สินค้า Repeat ถูก discount หนัก

---

## Step 4 — Problem Zone (Thresholds)

| Discount% | Margin% |
|-----------|---------|
| ≤40%=🟢 | ≥60%=🟢 |
| 40-50%=🟡 | 50-<60%=🟡 |
| >50%=🔴 | <50%=🔴 |

**High Risk Zone** = Discount% 🔴 + Margin% 🔴 พร้อมกัน

---

## Step 5 — YoY Comparison

Discount% FY27 vs FY26, Margin% FY27 vs FY26 รายหมวด — ระบุ Sensitivity Alert

---

## Step 6 — Response

**Headline** — จำนวน Category ใน High Risk Zone

**ตาราง 1: Category Discount & Margin FY27 vs FY26**

| Category | Net Sales | Discount% FY27 | FY26 | Margin% FY27 | FY26 | Zone |

**ตาราง 2: Product Type — Discount สูงสุด Top 10**

**ตาราง 3: High Risk Zone (Discount🔴 + Margin🔴)**

| Category | Product Type | Discount% | Margin% | Net Sales Impact |

**แนวทางควบคุม Discount** — อ้างอิงข้อมูลจริง

**Data Footer**

---

# Output Rules

- SUM ก่อนหารเสมอ — ห้ามคำนวณ ratio ทีละแถว
- Zone 🟢🟡🔴 ทุกแถว
- High Risk Zone แยกตาราง
- แนวทางควบคุมอ้างอิง Category/Product จริง

