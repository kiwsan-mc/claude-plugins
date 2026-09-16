# MCG Inventory Agent

MC Group Inventory Analyst Agent plugin for Claude Code / Cowork.

ถามข้อมูลสินค้าคงคลัง (stock on hand, aging, PO, STO) ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน Synapse MCP tools.

> 📌 **ศัพท์ MCG:** การสั่งซื้อเข้า/PO = **"Sales In"** (skill `po-intake`) · ยอดขาย = **"Sales Out"** → ใช้ `mcg-sales-agent`

## Version

**v1.0.0** — Synapse inventory domain (T-SQL, canned tools + raw query fallback)

## Skills

| Skill | Role | หน้าที่ |
|-------|------|---------|
| `inventory-agent` | Inventory Agent | กฎกลาง, tool priority, aging zones, snapshot rules (shared foundation) |
| `stock-health` | Stock Health Analyst | สต็อกคงเหลือปัจจุบันแยก aging/brand/region + สินค้าเสี่ยง clearance |
| `stock-trend` | Inventory Planner | สต็อกย้อนหลัง time series + เปรียบเทียบช่วงเวลา |
| `po-intake` | Procurement Analyst | **Sales In** (PR/PO/GR/open qty) แยก vendor/สาขา + fulfillment |
| `sto-transfer` | Distribution Analyst | โอนย้ายสต็อกระหว่างสาขา + open transfer |

## Architecture

```
skills/
├── inventory-agent/    ← SKILL.md หลัก (rules, tool priority, aging, snapshot pinning)
├── stock-health/       ← #[[file:../inventory-agent/SKILL.md]] + role prompt
├── stock-trend/        ← #[[file:../inventory-agent/SKILL.md]] + role prompt
├── po-intake/          ← #[[file:../inventory-agent/SKILL.md]] + role prompt
└── sto-transfer/       ← #[[file:../inventory-agent/SKILL.md]] + role prompt
```

แต่ละ skill ย่อย include กฎหลักผ่าน `#[[file:...]]` — แก้ที่เดียวมีผลทุก role.

## MCP Tools (Synapse — server: `synapse-inventory`)

| Tool | Description |
|------|-------------|
| `stock_on_hand_synapse` | สต็อกคงเหลือปัจจุบัน (auto-pin latest snapshot) แยก dimension |
| `stock_daily_trend_synapse` | สต็อกย้อนหลังตามช่วงเวลา |
| `po_summary_synapse` | Purchase Order (PR/PO/GR/open) |
| `sto_summary_synapse` | Stock Transfer Order |
| `stock_on_hand_yoy_synapse` | สต็อก YoY (snapshot ปัจจุบัน vs วันเดียวกันปีก่อน) |
| `po_summary_yoy_synapse` / `sto_summary_yoy_synapse` | PO / STO YoY (Apple-to-Apple) |
| `max_stock_date_synapse` / `max_po_date_synapse` | anchor date ของสต็อก / PO |
| `inventory_query_synapse` | Raw T-SQL (SELECT/WITH) — fallback |
| `describe_table_inventory_synapse` | Schema lookup |
| `search_columns_inventory_synapse` | Column search |

## Data Sources

- `ai.fact_MB52` — สต็อกคงเหลือ snapshot ล่าสุด (วันเดียว) — current on-hand
- `ai.fact_sales_and_stock_daily` — สต็อกย้อนหลัง + ยอดขายรายวัน (ต้องมี date range)
- `ai.fact_stock_month_ending` — สต็อกสิ้นเดือน (2022-01 … 2026-08)
- `ai.fact_po_sto` — Purchase Order + Stock Transfer Order รวมตารางเดียว → แยกด้วย `Item_Category` (PO = `<> '7'`, STO = `= '7'`)

> อัปเดต: ย้ายจาก `gold.script_stock_daily*` / `silver.sap_po` / `silver.sap_sto` มาเป็น schema `[ai]` แล้ว (ตารางเดิมยังอยู่แต่เลิกใช้)

## Usage

- "สต็อกคงเหลือแยก aging" → `stock-health`
- "แนวโน้มสต็อก 30 วันล่าสุด" → `stock-trend`
- "Sales In / PO ค้างส่งจาก vendor ไหนบ้าง" → `po-intake`
- "การโอนสต็อกระหว่างสาขาเดือนนี้" → `sto-transfer`
