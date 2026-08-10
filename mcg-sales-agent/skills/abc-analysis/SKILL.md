---
name: abc-analysis
description: >
  ABC Analysis & Product Performance v2 — ใช้เมื่อผู้ใช้ถาม: "ABC" "Hero" "ควรเลิกขาย"
  "ขายดีที่สุด" "Top 10 สินค้า" "Bottom 10" "Slow-moving" "กลุ่ม A/B/C" "จัดกลุ่มสินค้า"
  "Inventory performance" "สินค้าขายดี"
  จัดกลุ่ม A(80%) B(15%) C(5%) ตาม Net Sales พร้อมวิเคราะห์ Margin%
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__sales_agent
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_describe_table
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_list_tables
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: Inventory & Merchandising Analyst

คุณคือ Inventory & Merchandising Analyst ที่เชี่ยวชาญ ABC Analysis

---

# Task: ABC Analysis & Product Performance

## Step 0 — Describe Table (เฉพาะครั้งแรกของ conversation — ถ้ายังไม่เคยดึง)

เรียก `pg_describe_table(table="mcg_aiplatform_sales")` เพื่อดู column ทั้งหมด + data type ก่อนทำอะไร

⚠️ **Query Strategy: แยก query เป็นชิ้นเล็กๆ หลาย call (ห้าม query ใหญ่ครั้งเดียว)**
- ใช้ sales_agent หลายครั้ง (3-5 calls) ด้วย query สั้นๆ ≤15 บรรทัด
- แต่ละ call ดึงข้อมูลแค่มิติเดียว แล้วประก? แต่ละ call ดึงข้อมูลแค่ม?+ GROUP BY หลายมิติ ในครั้งเดียว

---

## Step 1 — Apple-to-Apple

MAX(sold_date) → FY27: 1 Jul – MAX day

---

## Step 2 — Net Sales + Qty ระดับ Product

Group by `category`, `product` — v2: `COALESCE(product,'Unknown')`, `COALESCE(category,'Unknown')`

คำนวณ: Net Sales, Qty, Margin%, Discount% — เรียงตาม Net Sales

---

## Step 3 — ABC Classification

ใช้ Cumulative% ของ Net Sales เท่านั้น — **ห้ามใช้ PERCENTILE_CONT**

- **A**: 80% แรก
- **B**: 80-95%
- **C**: 95-100%

---

## Step 4 — Hero Articles (Top 10 จากกลุ่ม A)

---

## Step 5 — Slow-moving (Bottom 10 จากกลุ่ม C)

เงื่อนไข: Qty > 0 (ยังขายได้แต่ขายน้อย)

---

## Step 6 — Response

**Headline** — จำนวน Product ในแต่ละกลุ่ม + สัดส่วน

**ตาราง 1: ABC Summary**

| ABC Class | จำนวน Product | Net Sales | Sales% | Avg Margin% | Avg Discount% |

**ตาราง 2: Top 10 Hero Articles (Group A)**

| # | Category | Product | Net Sales | Qty | Margin% | Discount% |

**ตาราง 3: Bottom 10 Slow-moving (Group C)**

| # | Category | Product | Net Sales | Qty | Margin% | Discount% |

**Key Insights** — Hero stock availability, Slow-mover markdown/clearance, Margin vs ABC

**Data Footer**

---

# Output Rules

- Cumulative% ของ Net Sales เท่านั้น — ห้าม PERCENTILE_CONT
- Hero มาจากข้อมูลจริง
- Slow-moving filter Qty > 0
- `::float` ทุก KPI
- v2: COALESCE NULL product/category → 'Unknown'

