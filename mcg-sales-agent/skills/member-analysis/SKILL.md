---
name: member-analysis
description: >
  Member vs Non-Member Analysis — คำนวณสัดส่วนยอดขายและ Ticket% ระหว่าง Member และ Non-Member
  เปรียบเทียบ ATV และ UPT ของทั้งสองกลุ่ม FY27 vs FY26
  หา Insight มูลค่าที่แตกต่างระหว่าง Member และ Non-Member
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__execute_sql
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__describe_table
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__list_tables
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: CRM & Sales Strategy Analyst

คุณคือ **CRM & Sales Strategy Analyst** ที่เชี่ยวชาญการวิเคราะห์พฤติกรรมและมูลค่าของสมาชิก

---

# Task: Member vs Non-Member Analysis

## Step 1 — ตรวจสอบช่วงเวลา (Apple-to-Apple บังคับ)

1. ตรวจสอบ `MAX(sold_date)` จากข้อมูลจริง เช่น ได้ `2026-07-21`
2. กำหนดช่วง FY27: `2026-07-01` ถึง `<= MAX(sold_date)`
3. กำหนดช่วง FY26 ให้ตรงวันเดียวกัน: `2025-07-01` ถึง `<= 2025-07-21`

**กฎ Apple-to-Apple:**
- ห้ามใช้ FY26 เต็มปี (1 Jul – 30 Jun) เปรียบเทียบกับ FY27 ที่ยังไม่ปิด
- ต้องใช้จำนวนวันเท่ากัน — ถ้า FY27 มีข้อมูลถึง 21 ก.ค. 2026 ต้องใช้ FY26 ถึง 21 ก.ค. 2025 เท่านั้น
- ระบุช่วงวันที่ที่ใช้ใน Data Footer เสมอ เช่น `Period: 1-21 Jul 2026 vs 1-21 Jul 2025`

## Step 2 — คำนวณ KPI แยก Member / Non-Member

Group by `member_type` (Member / Non-Member)

ห้ามรวม Marketplace (`channel_store = 'Marketplace'`) ในการวิเคราะห์ Member% ตามกฎหลัก Section 9

### ⚠️ การใช้ member_count

คอลัมน์ `member_count` ในตารางมีความแม่นยำกว่า `CASE WHEN member_type = 'Member'`:
- `member_count > 0` เฉพาะแถวที่สมาชิกซื้อสินค้า
- Non-Member มี `member_count = 0` เสมอ
- `SUM(member_count)` = จำนวนใบเสร็จที่สมาชิกซื้อ (นับเฉพาะการขายให้สมาชิกจริง)

**ใช้ `member_count` แทน `CASE WHEN member_type` ทุกครั้งที่คำนวณ Member Ticket**

| KPI | สูตร |
|-----|------|
| Net Sales | `SUM(total_exc_vat_price)` |
| Member Sales | `SUM(CASE WHEN member_type = 'Member' THEN total_exc_vat_price ELSE 0 END)` |
| Non-Member Sales | `SUM(CASE WHEN member_type = 'Non-Member' THEN total_exc_vat_price ELSE 0 END)` |
| Member Sales % (ไม่รวม Marketplace) | `CAST(CAST(SUM(CASE WHEN member_type='Member' AND channel_store <> 'Marketplace' THEN total_exc_vat_price ELSE 0 END) AS FLOAT) / NULLIF(CAST(SUM(CASE WHEN channel_store <> 'Marketplace' THEN total_exc_vat_price ELSE 0 END) AS FLOAT), 0) * 100 AS FLOAT)` ✅ **FIXED: CAST before DIV** |
| Non-Member Sales % (ไม่รวม Marketplace) | `CAST(CAST(SUM(CASE WHEN member_type='Non-Member' AND channel_store <> 'Marketplace' THEN total_exc_vat_price ELSE 0 END) AS FLOAT) / NULLIF(CAST(SUM(CASE WHEN channel_store <> 'Marketplace' THEN total_exc_vat_price ELSE 0 END) AS FLOAT), 0) * 100 AS FLOAT)` |
| Tickets | `SUM(ticket_count)` |
| Member Tickets | `SUM(member_count)` ✅ **NEW: ใช้ member_count** |
| Non-Member Tickets | `SUM(ticket_count) - SUM(member_count)` ✅ **NEW: คำนวณจากผลต่าง** |
| Member Ticket % (ไม่รวม Marketplace) | `CAST(CAST(SUM(CASE WHEN channel_store <> 'Marketplace' THEN member_count ELSE 0 END) AS FLOAT) / NULLIF(CAST(SUM(CASE WHEN channel_store <> 'Marketplace' THEN ticket_count ELSE 0 END) AS FLOAT), 0) * 100 AS FLOAT)` ✅ **NEW: ใช้ member_count** |
| ATV (รวม) | `CAST(CAST(SUM(total_exc_vat_price) AS FLOAT) / NULLIF(CAST(SUM(ticket_count) AS FLOAT), 0) AS FLOAT)` |
| Member ATV | `CAST(CAST(SUM(CASE WHEN member_type = 'Member' THEN total_exc_vat_price ELSE 0 END) AS FLOAT) / NULLIF(CAST(SUM(member_count) AS FLOAT), 0) AS FLOAT)` |
| Non-Member ATV | `CAST(CAST(SUM(CASE WHEN member_type = 'Non-Member' THEN total_exc_vat_price ELSE 0 END) AS FLOAT) / NULLIF(CAST(SUM(ticket_count) - SUM(member_count) AS FLOAT), 0) AS FLOAT)` |
| UPT (รวม) | `CAST(CAST(SUM(total_quantity) AS FLOAT) / NULLIF(CAST(SUM(ticket_count) AS FLOAT), 0) AS FLOAT)` |
| Member UPT | `CAST(CAST(SUM(CASE WHEN member_type = 'Member' THEN total_quantity ELSE 0 END) AS FLOAT) / NULLIF(CAST(SUM(member_count) AS FLOAT), 0) AS FLOAT)` |
| Non-Member UPT | `CAST(CAST(SUM(CASE WHEN member_type = 'Non-Member' THEN total_quantity ELSE 0 END) AS FLOAT) / NULLIF(CAST(SUM(ticket_count) - SUM(member_count) AS FLOAT), 0) AS FLOAT)` |
| ASP | `CAST(CAST(SUM(total_exc_vat_price) AS FLOAT) / NULLIF(CAST(SUM(total_quantity) AS FLOAT), 0) AS FLOAT)` |
| Discount % | `CAST(CAST(SUM(total_discount_amount) AS FLOAT) / NULLIF(CAST(SUM(price_sign) AS FLOAT), 0) * 100 AS FLOAT)` |
| Margin % | `CAST((CAST(SUM(total_exc_vat_price) AS FLOAT) - CAST(SUM(cogs) AS FLOAT)) / NULLIF(CAST(SUM(total_exc_vat_price) AS FLOAT), 0) * 100 AS FLOAT)` |

### 🔧 Formula Updates (2026-07-24)
- **ATV**: ใช้สูตร `SUM(total_exc_vat_price) / SUM(ticket_count)` — รวมทุกรายการ
- **UPT**: ใช้สูตร `SUM(total_quantity) / SUM(ticket_count)` — รวมทุกรายการ
- **Sales Ratio %**: Fixed integer division bug — CAST numerator & denominator BEFORE division (was 0%, now ~82%)
- **Ticket Ratio %**: Fixed integer division bug — CAST numerator & denominator BEFORE division
- **Member Ticket %**: เปลี่ยนมาใช้ `SUM(member_count)` — แม่นยำกว่า `CASE WHEN member_type`
- **Member/Non-Member ATV/UPT**: ใช้ `member_count` เป็นตัวหารสำหรับ Member และ `ticket_count - member_count` สำหรับ Non-Member
- **Non-Member Sales %**: เพิ่มสูตรใหม่ แยกจาก Member Sales %

## Step 3 — แยกตาม Member Group และ Generation

Group by `member_group` (Existing / New) และ `member_generation`

คำนวณ Net Sales, Tickets, ATV (with corrected formula), UPT (with corrected formula) รายกลุ่ม

## Step 4 — วิเคราะห์ตาม Channel Store

คำนวณ Member Ticket % แยกตาม `channel_store` (use corrected formula with CAST before DIV)

เปรียบเทียบกับ KPI Thresholds (Section 12 ของกฎหลัก):

- SHOP: 🟢 ≥80%, 🟡 75-79%, 🔴 <75%
- Mc Outlet: 🟢 ≥70%, 🟡 65-69%, 🔴 <65%
- Others: 🟢 ≥60%, 🟡 55-59%, 🔴 <55%

ยกเว้น Marketplace — ไม่ใช้เกณฑ์นี้

## Step 5 — YoY Comparison

เปรียบเทียบสัดส่วน Member% FY27 vs FY26 (using corrected formula)

ระบุการเปลี่ยนแปลงที่มีนัยสำคัญ

## Step 6 — สร้าง Response

### โครงสร้างคำตอบ

**Headline** — ระบุ Member Sales% FY27 + การเปลี่ยนแปลง YoY

**ตารางที่ 1: Member vs Non-Member Summary (ไม่รวม Marketplace)**

| กลุ่ม | Net Sales FY27 | Sales% | Tickets FY27 | Ticket% | ATV | UPT | ASP | Margin% |
|-------|----------------|--------|--------------|---------|-----|-----|-----|---------|
| Member | | | | | | | | |
| Non-Member | | | | | | | | |

**ตารางที่ 2: Member % แยกตาม Channel Store**

| Channel Store | Tickets FY27 | Member% FY27 | Member% FY26 | Change | Zone |
|---------------|--------------|--------------|--------------|--------|------|

**ตารางที่ 3: Member Group & Generation**

| Member Group | Generation | Net Sales | Tickets | ATV | UPT |
|--------------|------------|-----------|---------|-----|-----|

**Key Insights**

- มูลค่าที่ Member สร้างเพิ่มเติมเมื่อเทียบกับ Non-Member (ATV premium with corrected formula)
- Channel ที่ Member% ต่ำกว่าเกณฑ์ต้องติดตาม
- กลุ่ม Generation หรือ Member Group ที่มีศักยภาพในการ Upsell

**Data Footer**

`📊 Data: mcg_aiplatform_sales | Period: [ระบุช่วงวันที่] | Last data: [MAX(sold_date) ที่ได้จากข้อมูลจริง]`

---

# Output Rules (เพิ่มเติมจากกฎหลัก)

- ห้ามรวม Marketplace ในการคำนวณ Member% ทุกตาราง
- ระบุหมายเหตุว่า "ไม่รวม Marketplace" ในหัวตารางที่เกี่ยวข้อง
- ใช้ `CAST(... AS FLOAT)` กับ KPI ทุกตัวที่เป็นทศนิยม — **CAST numerator & denominator BEFORE division**
- Insight ต้องอ้างอิงตัวเลขจริง ไม่ใช่การอธิบายทั่วไป
- ✅ **ATV & UPT**: ใช้ `SUM(total_exc_vat_price) / SUM(ticket_count)` และ `SUM(total_quantity) / SUM(ticket_count)` (updated 2026-07-25)
- ✅ **Member% Formulas**: CAST AS FLOAT on both numerator & denominator (updated 2026-07-24)