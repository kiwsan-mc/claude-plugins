# MCG CRM Agent

MC Group CRM & Member Analyst Agent plugin for Claude Code / Cowork.

วิเคราะห์ลูกค้า/สมาชิก (member) รายตัว, การแบ่ง segment, ส่วนลดสมาชิก, การคืนสินค้า และ ticket/ATV ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน Synapse MCP tools บนตาราง `ai.poc_fact_sales_with_crm`

## Version

**v1.1.1** — กฎหน่วยจำนวน + สูตรนับรุ่น-สี
- **v1.1.1**: กฎการนับจำนวน (รุ่น = รุ่น-สี · ถามกลับเมื่อไม่ระบุหน่วย · ระบุหน่วยทุกครั้ง) + เพิ่มสูตรนับ SKU/รุ่น-สี ใน §6 (ต้อง join `dim_article` บน `Article_Key`)
**v1.0.0** — เริ่มต้น: CRM/member domain แยกจาก sales (domain ใหม่)

## Skills

| Skill | Role | หน้าที่ |
|-------|------|---------|
| `crm-agent` | CRM & Member Agent | กฎกลาง, tool priority, anchor, caveats ข้อมูล (shared foundation) |
| `member-segmentation` | CRM Segmentation Analyst | member by channel/product, frequency segments, top members, demographic (tier/gender/generation) |
| `member-discount` | Member Benefits Analyst | ส่วนลดสมาชิก (CRM discount) + การคืนสินค้า (return analysis) |

## Architecture

```
skills/
├── crm-agent/            ← SKILL.md หลัก (rules, tool priority, anchor, caveats)
├── member-segmentation/  ← #[[file:../crm-agent/SKILL.md]] + role prompt
└── member-discount/      ← #[[file:../crm-agent/SKILL.md]] + role prompt
```

## MCP Tools (Synapse — server: `synapse-crm`)

| Tool | Description |
|------|-------------|
| `max_member_date_synapse` | Anchor: max Sold_Date + FY ranges (เรียกก่อนเสมอ) |
| `member_crm_schema_cheatsheet_synapse` | Schema ของ fact + dims (ก่อน raw query) |
| `member_kpi_overview_synapse` | KPI ภาพรวม: net sales, qty, tickets, members, ATV, CRM discount |
| `member_by_channel_synapse` | Member sales แยก channel / channel_text / branch |
| `member_by_product_synapse` | Member sales แยก category / brand / gender / aging / sales_type |
| `member_frequency_synapse` | Purchase-frequency segments (1 / 2-3 / 4-10 / 11+) |
| `member_top_members_synapse` | Top members (RFM) จัดอันดับตาม net sales |
| `member_discount_synapse` | CRM discount แยก discount_code / channel |
| `member_ticket_atv_synapse` | Ticket / ATV / UPT แยก channel / branch / month |
| `member_return_analysis_synapse` | การคืนสินค้า (return) + return rate |
| `member_by_demographic_synapse` | Member แยก tier / gender / generation (join silver CRM master) |
| `member_sales_agent_synapse` | Raw T-SQL (SELECT/WITH) — fallback |

## Data Source

- `ai.poc_fact_sales_with_crm` — grain `(Invoice_Code, Sequence_Item)` = 1 แถวต่อรายการขาย; มี `Member_Code` + `Invoice_Code` (ตารางเดียวใน [ai] ที่มี member identity + invoice key)
- joins: `ai.dim_article` (Article_Key), `ai.dim_branch` (Branch_Code), `silver.crm_member_profile` / `silver.crm_bigdata_member` (Member_Code — demographic)

## ข้อควรระวัง (ข้อมูล)

1. **ตารางคือยอดขายทั้งหมด (member + non-member)** — `Member_Code` เป็นค่าว่าง 86.7% ของแถว; member-attributed net sales ≈ 16.6% ของรวม → member vs non-member แยกได้จากตารางนี้
2. **Member penetration ต่างกันตาม channel** — OFFLINE (~64%) และ MCSHOP.COM (~62%) member-driven; TIKTOK/SHOPEE/LAZADA guest-driven (member แค่ ~4-9%) → วิเคราะห์ member ต้องแยก channel เสมอ
3. **ไม่มี YoY** — ตารางเริ่ม 2025-07-01 (ยังไม่มีปีก่อนครบ) → YoY ได้ตั้งแต่ 2026-07
4. **ไม่มี COGS** → ไม่มี margin%
5. ครอบคลุม ~88 สาขา (Bangkok + ecommerce) — ไม่ใช่ national
6. **คำถามรายคน** — รหัสลูกค้าเป็น exact identifier: `M2603-013482` ≠ `M2502-013482` → ห้ามใช้ LIKE/prefix match (จะได้ยอดของสมาชิกคนอื่นโดยไม่ error); รหัสรูปแบบ `M` + YYMM + `-` + เลข 6 หลัก

## Usage

- "ใครคือลูกค้าของเรา / สมาชิกซื้อบ่อยแค่ไหน" → `member-segmentation`
- "ส่วนลดสมาชิกเท่าไหร่ / คืนสินค้าเยอะไหม" → `member-discount`
- "ลูกค้า M2603-013482 มียอดซื้อเท่าไหร่" → `crm-agent` (สมาชิกรายคน — exact match รหัสลูกค้า)
