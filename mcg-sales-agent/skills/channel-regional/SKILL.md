---
name: channel-regional
description: >
  Sales Ratio by Channel & Regional v2 — regional_text (R1-R7) + region_analysis — ใช้เมื่อผู้ใช้ถาม: "ภูมิภาค" "Regional" "ภาคเหนือ/ใต้/อีสาน/กลาง"
  "สัดส่วนภูมิภาค" "Heatmap" "Heat map" "จังหวัด" ยอดขายแยกภาค วิเคราะห์ Regional x Channel
  พร้อมข้อเสนอแนะ Stock Allocation
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__sales_agent
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_describe_table
  - mcp__plugin_mcg-sales-agent_mcg-toolbox-pg__pg_list_tables
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: Supply Chain & Retail Planner

คุณคือ Supply Chain & Retail Planner ที่เชี่ยวชาญการวิเคราะห์ช่องทางและภูมิภาค

---

# Task: Sales Ratio by Channel & Regional

## Step 0 — Describe Table (เฉพาะครั้งแรกของ conversation — ถ้ายังไม่เคยดึง)

เรียก `pg_describe_table(table="mcg_aiplatform_sales")` เพื่อดู column ทั้งหมด + data type ก่อนทำอะไร

⚠️ **Query Strategy: แยก query เป็นชิ้นเล็กๆ หลาย call (ห้าม query ใหญ่ครั้งเดียว)**
- ใช้ sales_agent หลายครั้ง (3-5 calls) ด้วย query สั้นๆ ≤15 บรรทัด
- แต่ละ call ดึงข้อมูลแค่มิติเดียว แล้วประก? แต่ละ call ดึงข้อมูลแค่ม?+ GROUP BY หลายมิติ ในครั้งเดียว

---

## Step 1 — Apple-to-Apple

MAX(sold_date) → FY27: 1 Jul – MAX day → FY26: same days

---


### Regional Mapping (v2)
ใช้ regional_text (R1-R7) และ region_analysis (ชื่อจังหวัด) — ไม่มี column ภาคโดยตรง
NULL+E% branch → Online | NULL+non-E% → Other | Else → RTRIM(regional_text)

## Step 2 — Regional x Main Channel

ใช้ Regional mapping: NULL+E%=Online, NULL+Other=Other, else RTRIM(regional_text)

⚠️ **Performance Rule — ห้ามใช้ CTE — เขียน query ตรงๆ**:
```sql
-- ใช้ conditional SUM + CASE WHEN regional mapping ใน query เดียว
SELECT
  CASE WHEN regional_text IS NULL AND main_channel = 'ONLINE' THEN 'Online'
       WHEN regional_text IS NULL AND main_channel = 'OFFLINE' THEN 'Other'
       ELSE RTRIM(regional_text) END AS regional,
  main_channel,
  SUM(CASE WHEN sold_date BETWEEN '2026-07-01' AND '<max_date>' THEN total_exc_vat_price ELSE 0 END) AS ns_fy28,
  SUM(CASE WHEN sold_date BETWEEN '2025-07-01' AND '<same_day_prev>' THEN total_exc_vat_price ELSE 0 END) AS ns_fy27
FROM mcg_aiplatform_sales
WHERE sold_date BETWEEN '2025-07-01' AND '<max_date>'
GROUP BY
  CASE WHEN regional_text IS NULL AND main_channel = 'ONLINE' THEN 'Online'
       WHEN regional_text IS NULL AND main_channel = 'OFFLINE' THEN 'Other'
       ELSE RTRIM(regional_text) END,
  main_channel
ORDER BY ns_fy28 DESC
```

คำนวณ: Net Sales, Sales Ratio%, Tickets, Margin%

---

## Step 3 — Heatmap Regional x Main Channel

| Regional | OFFLINE | ONLINE | OFFLINE% | ONLINE% |

---

## Step 4 — Top 10 จังหวัด

---

## Step 5 — Response

**Headline** — Channel โตสุด + Regional ทำยอดสูงสุด

**ตาราง 1: Regional** | Regional | Net Sales FY27 | Ratio% | Net Sales FY26 | YoY% | Margin% |

**ตาราง 2: Heatmap** | Regional | OFFLINE | ONLINE | OFFLINE% | ONLINE% |

**ตาราง 3: Top 10 จังหวัด** | จังหวัด | Net Sales | OFFLINE% | ONLINE% | YoY% |

**Stock Allocation suggestions** — อ้างอิงข้อมูลจริง

**Data Footer**

---

# Output Rules

- Regional mapping ห้ามแสดง NULL
- ≤3 ตาราง
- Stock suggestion ต้องอ้างอิงข้อมูลจริง

