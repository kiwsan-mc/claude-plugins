# MCG Executive Agent

MC Group Executive Overview Agent plugin for Claude Code / Cowork.

สรุปภาพรวมธุรกิจเป็น executive summary เดียว — ดึง KPI จากหลาย domain (Sales Out + สต็อก/Sales In + Product + Target) แล้วสังเคราะห์เป็นภาพรวมเดียว แทนที่จะให้แต่ละ domain agent ตอบแยกกัน

รองรับทั้ง:
- **ภาพรวมครบ 4 ด้าน** ("ภาพรวม" / "overview" / "ทุกด้าน")
- **สรุปข้าม domain เฉพาะ** (เช่น "Sales + Target", "ยอดขาย + เป้า", "สรุป ... พร้อม ...") — ดึงแยก query แต่ตอบเป็น summary เดียว

## Version

**v1.1.0** — Orchestrator skill (Synapse, 4 domains + cross-domain partial summary)

## Skills

| Skill | Role | หน้าที่ |
|-------|------|---------|
| `business-overview` | Executive Overview | เรียก anchor 3 ตัว → ดึง KPI 4 ด้าน → สรุป executive summary เดียว |

## Architecture

```
skills/
└── business-overview/   ← SKILL.md (orchestrator: anchor-first + KPI checklist 4 ด้าน + synthesis template)
```

## MCP Tools (Synapse — 4 servers)

| Domain | Server | Summary tools |
|--------|--------|---------------|
| Sales Out | `synapse-sales` | `max_sold_date_synapse`, `dashboard_kpi_overall_synapse`, `dashboard_by_channel_synapse`, `regional_sales_yoy_synapse`, `member_vs_nonmember_synapse`, `subchannel_breakdown_synapse`, `dim_channel_list_synapse`, `sales_agent_synapse`, `retail_sales_schema_cheatsheet_synapse` |
| Sales In / สต็อก | `synapse-inventory` | `max_stock_date_synapse`, `stock_on_hand_synapse`, `stock_value_by_aging_synapse`, `stock_in_transit_synapse`, `po_overdue_synapse` |
| Product | `synapse-product` | `product_dimension_summary_synapse` |
| Target | `synapse-target` | `max_invoice_date_synapse`, `sales_target_vs_actual_synapse`, `sales_company_summary_synapse`, `sales_query_synapse`, `company_sales_schema_cheatsheet_synapse` |

## Usage

- "ภาพรวมธุรกิจ" / "overview" / "executive summary" / "ทุกด้าน" → `business-overview` (ครบ 4 ด้าน)
- "สรุป Sales Performance ... + Target ..." / "ยอดขาย + เป้า" / "เพิ่ม ... ด้วย" → `business-overview` (สรุปข้าม domain เป็น summary เดียว)
- คำถามเจาะลึก domain เดียว → ส่งไป agent เฉพาะ (mcg-sales-agent / mcg-inventory-agent / mcg-product-agent / mcg-target-agent)
