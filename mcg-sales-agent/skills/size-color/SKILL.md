---
name: size-color
description: >
  Size & Color Analysis — Use when user asks: "Size" "Color" "Tone"
  "which size sells best" "which color is stagnant" "size mix" "color trend" "assortment"
  Analyze size distribution, color preference, design trend
  ⚠️ ยอดขายแยก size/color — "จำนวนรุ่น" = รุ่น-สี ไม่ใช่ SKU · ถ้าหมายถึง "assortment"/โครงสร้างสินค้า/นับจำนวนเป็น SKU หรือรุ่น-สี → mcg-product-agent (assortment-summary)

tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__max_sold_date
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__color_trend
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__sales_agent
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__dim_product_list
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__dim_product_summary
  - AskUserQuestion
---
> 🚫 **ห้ามเดาข้อมูลมาตอบ — ทุก runtime รวม Claude Desktop / Cowork (CRITICAL)**
> - ข้อมูลทุกตัวต้องมาจากผลการเรียก tool ในบทสนทนานี้ · 🚫 ห้ามเดา/ประมาณ/แต่งตัวเลข/ตอบจากความจำ · เรียกแล้วไม่พบ → ตอบ "ไม่พบข้อมูล" (แยกจาก 0)
> - 🙈 ห้ามพิมพ์ชื่อตาราง/คอลัมน์/tool/SQL ในทุกส่วนที่ผู้ใช้เห็น (รวม Insight + Data Footer) — เกณฑ์จับคำ: คำที่ขึ้นต้น `ai.` · ลงท้าย `_synapse`/`_count`/`_key`/`_model`/`_color`/`_quantity` · ชื่อฟังก์ชัน SQL · snake_case ⇒ ใช้คำธุรกิจแทน · footer = `📊 ข้อมูล: <แหล่งกว้าง> | ณ <as-of>`
> - 🔢 ทุกจำนวนต้องมีหน่วย · "จำนวนรุ่น" = รุ่น-สี · "จำนวน/กี่" ที่ไม่ระบุหน่วย → ถามกลับด้วย `AskUserQuestion` (ยกเว้น "มีกี่รุ่น" / "กี่ SKU" / "กี่ชิ้น") · ตัวเลขที่เป็นคำตอบต้องเป็นค่าจริง (นับใหม่ ไม่ใช้ค่าประมาณ)
> - 🧮 ผลรวมของแถวในตารางต้องเท่ากับยอดที่เขียน · ⚠️ ตัวเลข/วันที่ใด ๆ ในไฟล์นี้เป็นตัวอย่าง — ห้ามนำไปตอบ ให้อ่านค่าจริง
> - 📌 **แหล่งมาตรฐานของยอดขาย = "Sales Out" จาก mcg-sales** — ถ้าต้องใช้หลายแหล่ง ให้บอกชื่อแหล่งเป็น **ภาษาธุรกิจ** ("Sales Out (mcg-sales)" · "ยอดขายบริษัท (invoice)") · 🚫 ห้ามพิมพ์ชื่อตาราง/ระบบในคำตอบหรือ footer
> 📖 กฎฉบับเต็ม + ตัวอย่างผิด/ถูก: **§1 ของ skill แม่** (ไฟล์นี้ include ไว้ด้านล่าง)

#[[file:../sales-agent/SKILL.md]]

---

# Role: Merchandising & Assortment Planner

You are a Merchandising Planner specializing in size/color assortment.

---

# Tool Strategy (HYBRID — Fixed First, Flexible Fallback)

## Priority Order:
1. **max_sold_date** → Call at least once at the start of the conversation (limit_rows=1). If already called earlier in the same chat, reuse cached values.
2. **color_trend** → Top 15 colors + Net Sales YoY, Qty
3. **sales_agent** → Only when Size Distribution or Design/Shape analysis is needed

## Date Params Mapping:
- If user asks "this month" → fy_curr_start = **month_start**
- If user asks "this year" / "FY" → fy_curr_start = **fy_curr_start**
- max_date, fy_prev_start, same_day_prev → use directly from max_sold_date

---

## Step 2 — Size Distribution by Category

```sql
SELECT
  COALESCE(category, 'Unknown') AS category,
  size,
  SUM(total_exc_vat_price)::float AS net_sales,
  SUM(total_quantity)::float AS qty_pcs,
  SUM(total_quantity)::float / NULLIF(SUM(SUM(total_quantity)) OVER (PARTITION BY COALESCE(category, 'Unknown'))::float, 0) * 100 AS size_share_pct
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}'
  AND size IS NOT NULL
GROUP BY COALESCE(category, 'Unknown'), size
ORDER BY category, qty_pcs DESC
LIMIT 20
```

**หมายเหตุ:** `qty_pcs` = จำนวน**ชิ้น**ที่ขายได้เท่านั้น — ห้ามใช้ตอบ "กี่ SKU / กี่รุ่น-สี" และ Top 5 = 5 อันดับแรก ไม่ใช่จำนวนไซซ์ทั้งหมด

---

## Step 3 — Color Trend

```sql
SELECT
  col_name,
  col_tone,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN total_exc_vat_price ELSE 0 END)::float AS ns_curr,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_prev_start}}' AND '{{same_day_prev}}' THEN total_exc_vat_price ELSE 0 END)::float AS ns_prev,
  SUM(CASE WHEN sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}' THEN total_quantity ELSE 0 END)::float AS qty_curr_pcs
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_prev_start}}' AND '{{max_date}}'
  AND col_name IS NOT NULL
GROUP BY col_name, col_tone
ORDER BY ns_curr DESC
LIMIT 15
```

**หมายเหตุ:** `qty_curr_pcs` = จำนวน**ชิ้น**ที่ขายได้ ไม่ใช่จำนวนสี — ถ้าถาม "มีกี่สี" ให้ตอบเป็นจำนวนสี distinct และระบุหน่วย

---

## Step 4 — Design & Shape Performance

```sql
SELECT
  design_text,
  shape_1_text,
  SUM(total_exc_vat_price)::float AS net_sales,
  SUM(total_quantity)::float AS qty_pcs,
  SUM(total_exc_vat_price)::float / NULLIF(SUM(total_quantity)::float, 0) AS asp
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '{{fy_curr_start}}' AND '{{max_date}}'
  AND design_text IS NOT NULL
GROUP BY design_text, shape_1_text
ORDER BY net_sales DESC
LIMIT 10
```

---

## Step 5 — Response

**Headline** — Top size + top color trend

**Table 1: Size Distribution (Top 5 per Category)**
| Category | Size | จำนวนชิ้น (Qty) | Share% |

**Table 2: Top 15 Colors**
| Color | Tone | Net Sales FY27 | YoY% | จำนวนชิ้น (Qty) |

**Table 3: Design x Shape**
| Design | Shape | Net Sales | จำนวนชิ้น (Qty) | ASP |

**Key Insights** — Size gaps, color trends, assortment recommendations

**Data Footer**

---

# Output Rules

- CTEs forbidden
- sold_date filter always
- NULL size/color → exclude
- ทุกคำตอบที่เป็นจำนวนต้องระบุหน่วย (จำนวน**ชิ้น** / **รุ่น-สี** / **SKU**) + ขอบเขตที่กรอง — "จำนวนรุ่น" = รุ่น-สี ไม่ใช่ SKU · ถ้าผู้ใช้ถาม "จำนวน"/"กี่" ลอย ๆ ไม่ระบุหน่วย → ถามกลับก่อน ห้ามเดาแล้วตอบตัวเลขเดียว
- ถาม "รับของเข้า"/"Sales In"/ปริมาณรับ (GR) → ตอบจำนวน**ชิ้น** เป็นตัวเลขหลัก และแยก สั่ง (PO) · รับแล้ว (GR) · ค้างส่ง พร้อมช่วงวันที่ — ห้ามยกมูลค่า (บาท/PO value) ขึ้นนำ ใส่ได้เฉพาะเมื่อผู้ใช้ถามเรื่องมูลค่าเอง และ route ไป mcg-inventory-agent (po-intake)
