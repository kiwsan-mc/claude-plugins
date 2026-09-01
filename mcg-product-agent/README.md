# MCG Product Agent

MC Group Product Master Analyst Agent plugin for Claude Code / Cowork.

ถามข้อมูล master สินค้า (assortment) — จำนวน SKU/model, แบรนด์, หมวดหมู่, ราคา, margin — ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน Synapse MCP tools.

## Version

**v1.0.0** — Synapse product master domain (T-SQL, canned tools + raw query fallback)

> ⚠️ นี่คือ **master data ของสินค้า** ไม่ใช่ยอดขาย/สต็อก — ถามยอดขายใช้ `mcg-sales-agent`, ถามสต็อกใช้ `mcg-inventory-agent`

## Skills

| Skill | Role | หน้าที่ |
|-------|------|---------|
| `product-agent` | Product Master Agent | กฎกลาง, tool priority, product dimensions, ขอบเขต (shared foundation) |
| `assortment-summary` | Merchandise Planner | SKU/model count + ราคา + margin แยก dimension |
| `attribute-explorer` | Catalog Specialist | list distinct values + drill SKU รายตัว |
| `pricing-structure` | Pricing Analyst | โครงสร้างราคา + margin ตาม price band/category |

## Architecture

```
skills/
├── product-agent/          ← SKILL.md หลัก (rules, tool priority, dimensions, scope)
├── assortment-summary/     ← #[[file:../product-agent/SKILL.md]] + role prompt
├── attribute-explorer/     ← #[[file:../product-agent/SKILL.md]] + role prompt
└── pricing-structure/      ← #[[file:../product-agent/SKILL.md]] + role prompt
```

## MCP Tools (Synapse — server: `synapse-product`)

| Tool | Description |
|------|-------------|
| `product_dimension_summary_synapse` | SKU/model count + avg tag/selling price + margin% แยก dimension |
| `product_attribute_values_synapse` | list distinct values ของ attribute (+ SKU count) |
| `product_list_synapse` | list SKU รายตัว + attributes |
| `product_query_synapse` | Raw T-SQL (SELECT/WITH) — fallback |
| `describe_table_product_synapse` | Schema lookup |
| `search_columns_product_synapse` | Column search |

## Data Source

- `silver.sap_article` — product master (brand, Level1-5, gender, season, color, size, aging, sales type, vendor, price, cost)
- ไม่มีตัวเลขยอดขาย/สต็อกในตารางนี้

## Usage

- "มีกี่ SKU แยกตามแบรนด์" → `assortment-summary`
- "มีสีอะไรบ้าง / list สินค้ายีนส์" → `attribute-explorer`
- "โครงสร้างราคาแยก price band" → `pricing-structure`
