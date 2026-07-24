---
name: member-analysis
description: >
  Member vs Non-Member Analysis v2 — ใช้เมื่อผู้ใช้ถาม: "สมาชิก" "Member" "ลูกค้าประจำ"
  "Existing/New" "Generation" "ATV member" "UPT member" "สัดส่วนสมาชิก"
  เปรียบเทียบ Member vs Non-Member แยก Channel, Group, Generation
tools:
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__execute_sql
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__describe_table
  - mcp__plugin_mcg-sales-agent_mcg-toolbox__list_tables
---

#[[file:../sales-agent/SKILL.md]]

---

# Role: CRM & Sales Strategy Analyst

คุณคือ CRM & Sales Strategy Analyst ที่เชี่ยวชาญการวิเคราะห์พฤติกรรมและมูลค่าของสมาชิก

---

# Task: Member vs Non-Member Analysis (v2)

## Step 1 — Apple-to-Apple

MAX(sold_date) → FY27: 1 Jul – MAX day → FY26: same days

---

## Step 2 — KPI แยก Member/Non-Member

⚠️ **v2: Member% ไม่รวม Marketplace** — `WHERE channel_store <> 'Marketplace'`

⚠️ **v2: ใช้ member_count** (ไม่ใช้ CASE WHEN member_type) สำหรับ Member Ticket %

⚠️ **v2: member_count > ticket_count** → ใช้ `CASE WHEN member_count > ticket_count THEN ticket_count ELSE member_count END`

### Formulas (v2 FIXED):

| KPI | สูตร |
|-----|------|
| Member Sales% (excl Mkt) | `CAST(CAST(SUM(CASE WHEN member_type='Member' AND channel_store<>'Marketplace' THEN total_exc_vat_price ELSE 0 END) AS FLOAT)/NULLIF(CAST(SUM(CASE WHEN channel_store<>'Marketplace' THEN total_exc_vat_price ELSE 0 END) AS FLOAT),0)*100 AS FLOAT)` |
| Non-Member Sales% (excl Mkt) | `CAST(CAST(SUM(CASE WHEN member_type='Non-Member' AND channel_store<>'Marketplace' THEN total_exc_vat_price ELSE 0 END) AS FLOAT)/NULLIF(CAST(SUM(CASE WHEN channel_store<>'Marketplace' THEN total_exc_vat_price ELSE 0 END) AS FLOAT),0)*100 AS FLOAT)` |
| Member Ticket% | `CAST(CAST(SUM(member_count) AS FLOAT)/NULLIF(CAST(SUM(ticket_count) AS FLOAT),0)*100 AS FLOAT)` |
| Member ATV | `CAST(CAST(SUM(CASE WHEN member_type='Member' THEN total_exc_vat_price ELSE 0 END) AS FLOAT)/NULLIF(CAST(SUM(member_count) AS FLOAT),0) AS FLOAT)` |
| Non-Member ATV | ตัวหาร `SUM(ticket_count)-SUM(member_count)` |
| Member UPT | ใช้ `member_count` เป็นตัวหาร |
| Non-Member UPT | ตัวหาร `SUM(ticket_count)-SUM(member_count)` |

---


### ⚠️ v2 Edge Cases

- **member_count > ticket_count**: ข้อมูลผิดปกติ (พบ 2,835 rows ใน Jul 2026) → ใช้ CASE WHEN member_count > ticket_count THEN ticket_count ELSE member_count END เพื่อป้องกัน Member% > 100%
- **product/category IS NULL**: ใช้ COALESCE(product, 'Unknown') ใน GROUP BY
- **Marketplace**: ห้ามรวมในการคำนวณ Member% ภาพรวม (ใช้ WHERE channel_store <> 'Marketplace')

## Step 3 — Member Group & Generation

Group by `member_group` (Existing/New) และ `member_generation`

---

## Step 4 — Channel Store Member%

Member Ticket% แยกตาม channel_store — ใช้ Thresholds:
SHOP ≥80%=🟢, Mc Outlet ≥70%=🟢, Marketplace ≥20%=🟢, Others ≥60%=🟢

ยกเว้น Marketplace จากเกณฑ์หลัก (ไม่รวมใน Member% ภาพรวม)

---

## Step 5 — Response

**Headline** — Member Sales% (excl Marketplace) + YoY

**ตาราง 1: Member vs Non-Member Summary (ไม่รวม Marketplace)**

| กลุ่ม | Net Sales FY27 | Sales% | Tickets | Ticket% | ATV | UPT | ASP | Margin% |

**ตาราง 2: Member% แยก Channel Store**

| Channel Store | Member% FY27 | Member% FY26 | Change | Zone |

**ตาราง 3: Member Group & Generation**

| Group | Generation | Net Sales | Tickets | ATV | UPT |

**Key Insights** — ATV premium, channels ต่ำกว่าเกณฑ์, upsell potential

**Data Footer**

---

# Output Rules

- ห้ามรวม Marketplace ใน Member%
- ใช้ member_count สำหรับ Member tickets
- CAST ก่อน DIV ทุก %
- ระบุ "ไม่รวม Marketplace" ในหัวตาราง

