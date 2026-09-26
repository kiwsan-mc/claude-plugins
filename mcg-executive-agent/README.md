# MCG Executive Agent

MC Group Executive Overview Agent plugin for Claude Code / Cowork.

สรุปภาพรวมธุรกิจเป็น executive summary เดียว — ดึง KPI จากหลาย domain (Sales Out + สต็อก/Sales In + Product + Target + Member/CRM) แล้วสังเคราะห์เป็นภาพรวมเดียว แทนที่จะให้แต่ละ domain agent ตอบแยกกัน

รองรับทั้ง:
- **ภาพรวมครบ 5 ด้าน** ("ภาพรวม" / "overview" / "ทุกด้าน")
- **สรุปข้าม domain เฉพาะ** (เช่น "Sales + Target", "ยอดขาย + เป้า", "สรุป ... พร้อม ...") — ดึงแยก query แต่ตอบเป็น summary เดียว

## Version

**v3.0.2** — ย้ำกฎห้ามเดาข้อมูลมาตอบทุก skill
- **v3.0.2**: ย้ำกฎ **ห้ามเดาข้อมูลมาตอบ** (ใช้กับทุก runtime โดยเฉพาะ Claude Desktop / Cowork) ใน **ทุก skill** ของปลั๊กอิน — ทุกตัวเลข/ข้อเท็จจริงต้องมาจากผลการเรียก tool จริงในบทสนทนาและอ้างอิงกลับได้ · เรียกแล้วไม่พบข้อมูลให้ตอบว่า "ไม่พบข้อมูล" ตามจริง (แยกจาก 0) · ห้ามเดา/ประมาณ/แต่งตัวเลข/ตอบจากความจำของโมเดล
- **v3.0.1**: กฎการนับจำนวน ("จำนวนรุ่น" = รุ่น-สี) และกฎ **"รับของเข้า → ตอบจำนวนชิ้น"** (ไม่ยกมูลค่าขึ้นนำ) ใช้กับด้าน Sales In/สต็อกของ overview

- **v3.0.0**: เพิ่ม `synapse-crm` — ภาพรวมครอบคลุม Member/CRM top-line (member sales share + CRM discount); การเจาะลึก member ยัง route ไป `mcg-crm-agent`
- **v2.0.0**: ย้ายแหล่งข้อมูลจาก `gold.` / `silver.` ไป schema `[ai]`; ถอด member / ticket / ATV ออกจาก KPI checklist เพราะไม่มีในแหล่งข้อมูลใหม่ (route ไป `mcg-sales-agent` แทน)
- **v1.2.0**: เพิ่ม freshness + validation rules
- **v1.1.0**: รองรับ cross-domain executive summary
- **v1.0.0**: เริ่มต้น — executive overview plugin

## Skills

| Skill | Role | หน้าที่ |
|-------|------|---------|
| `business-overview` | Executive Overview | เรียก anchor 4 ตัว → ดึง KPI 5 ด้าน → สรุป executive summary เดียว |

## Architecture

```
skills/
└── business-overview/   ← SKILL.md (orchestrator: anchor-first + KPI checklist 5 ด้าน + synthesis template)
```

## MCP Tools (Synapse — 5 servers)

| Domain | Server | Summary tools |
|--------|--------|---------------|
| Sales Out | `synapse-sales` | `max_sold_date_synapse`, `dashboard_kpi_overall_synapse`, `dashboard_by_channel_synapse`, `regional_sales_yoy_synapse`, `subchannel_breakdown_synapse`, `dim_channel_list_synapse`, `sales_agent_synapse`, `retail_sales_schema_cheatsheet_synapse` |
| Sales In / สต็อก | `synapse-inventory` | `max_stock_date_synapse`, `stock_on_hand_synapse`, `stock_value_by_aging_synapse`, `stock_in_transit_synapse`, `po_overdue_synapse` |
| Product | `synapse-product` | `product_dimension_summary_synapse` |
| Target | `synapse-target` | `max_invoice_date_synapse`, `sales_target_vs_actual_synapse`, `sales_company_summary_synapse`, `sales_query_synapse`, `company_sales_schema_cheatsheet_synapse` |
| Member/CRM (top-line) | `synapse-crm` | `max_member_date_synapse`, `member_kpi_overview_synapse`, `member_by_channel_synapse` |

## Usage

- "ภาพรวมธุรกิจ" / "overview" / "executive summary" / "ทุกด้าน" → `business-overview` (ครบ 5 ด้าน)
- "สรุป Sales Performance ... + Target ..." / "ยอดขาย + เป้า" / "เพิ่ม ... ด้วย" → `business-overview` (สรุปข้าม domain เป็น summary เดียว)
- คำถามเจาะลึก domain เดียว → ส่งไป agent เฉพาะ (mcg-sales-agent / mcg-inventory-agent / mcg-product-agent / mcg-target-agent / mcg-crm-agent)

## ขอบเขตข้อมูล (อัปเดต)

- ใช้ schema `[ai]` ของ Synapse (ย้ายจาก `gold.` / `silver.` แล้ว)
- ⚠️ **member/CRM มี 2 แหล่ง ห้ามเทียบกัน**: ภาพรวมนี้ดึง top-line member จาก `synapse-crm` (⚠️ **subset ~88 สาขา = กทม.+ออนไลน์**) ส่วน member ratio ทั้งบริษัท + YoY → **mcg-sales-agent** (`member-analysis`, Postgres ครอบคลุมทุกสาขา); เจาะลึก member รายตัว/RFM/tier → **mcg-crm-agent**
- ⚠️ **Tickets / ATV / UPT ไม่มีใน synapse sales fact** → ทั้งบริษัทใช้ **mcg-sales-agent**; เฉพาะ member subset ใช้ `member_ticket_atv_synapse`
- ⚠️ ยอดขาย POS รายวัน กับยอดขาย invoice-level เป็นคนละ population — ไม่บวก/เทียบกันตรง ๆ
