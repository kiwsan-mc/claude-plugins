# MCG Executive Agent

MC Group Executive Overview Agent plugin for Claude Code / Cowork.

สรุปภาพรวมธุรกิจครบทุกด้าน (Sales Out + สต็อก/Sales In + Product + Target) เป็น executive summary เดียว — ดึง KPI จาก 4 โดเมนแล้วสังเคราะห์เป็นภาพรวมเดียว แทนที่จะให้แต่ละ domain agent ตอบแยกกัน

## Version

**v1.0.0** — Orchestrator skill (Synapse, 4 domains)

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
| Sales Out | `synapse-sales` | `max_sold_date_synapse`, `dashboard_kpi_overall_synapse`, `dashboard_by_channel_synapse`, `regional_sales_yoy_synapse`, `member_vs_nonmember_synapse` |
| Sales In / สต็อก | `synapse-inventory` | `max_stock_date_synapse`, `stock_on_hand_synapse`, `stock_value_by_aging_synapse`, `stock_in_transit_synapse`, `po_overdue_synapse` |
| Product | `synapse-product` | `product_dimension_summary_synapse` |
| Target | `synapse-target` | `max_invoice_date_synapse`, `sales_target_vs_actual_synapse`, `sales_company_summary_synapse` |

## Usage

- "ภาพรวมธุรกิจ" / "overview" / "executive summary" / "ทุกด้าน" → `business-overview`
- คำถามเจาะลึก domain เดียว → ส่งไป agent เฉพาะ (mcg-sales-agent / mcg-inventory-agent / mcg-product-agent / mcg-target-agent)
