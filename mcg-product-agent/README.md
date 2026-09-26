# MCG Product Agent

MC Group Product Master Analyst Agent plugin for Claude Code / Cowork.

ถามข้อมูล master สินค้า (assortment) — จำนวน SKU / รุ่น (รุ่น-สี), แบรนด์, หมวดหมู่, ราคา, margin — ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน Synapse MCP tools.

> ⚠️ **"จำนวนรุ่น" = รุ่น-สี** (ไม่ใช่รุ่น และไม่ใช่ SKU) · "จำนวน"/"กี่" ที่ไม่ระบุหน่วย → **ถามกลับก่อน** (SKU / รุ่น (รุ่น-สี) / ชิ้น) ห้ามเดาแล้วตอบตัวเลขเดียว · ทุกจำนวนต้องมีหน่วยกำกับ

## Version

**v1.2.1** — กฎหน่วยจำนวน: "จำนวนรุ่น" = รุ่น-สี
- **v1.2.1**: กฎการนับจำนวน — **"จำนวนรุ่น" = รุ่น-สี** ไม่ใช่รุ่น ไม่ใช่ SKU · "จำนวน/กี่" ที่ไม่ระบุหน่วยต้อง **ถามกลับ** (SKU / รุ่น-สี / ชิ้น) · ทุกคำตอบที่เป็นจำนวนต้องระบุหน่วย · เพิ่มคอลัมน์ `model_color_count` ในตาราง Assortment (ตรวจ 2026-09-26: SKU 128,121 · รุ่น 23,815 · รุ่น-สี 31,418)

- **v1.2.0**: ย้ายจาก `silver.sap_article` ไป `ai.dim_article` (ตัด prefix `S_ATC_` ออก, join ด้วย `Article_Key`); ระบุว่า `Grade` / `Color_Tone` ว่างทั้งหมด
- **v1.1.0**: เพิ่ม freshness + validation rules
- **v1.0.0**: เริ่มต้น — product master domain

> ⚠️ นี่คือ **master data ของสินค้า** ไม่ใช่ยอดขาย/สต็อก — ถามยอดขายใช้ `mcg-sales-agent`, ถามสต็อกใช้ `mcg-inventory-agent`

## Skills

| Skill | Role | หน้าที่ |
|-------|------|---------|
| `product-agent` | Product Master Agent | กฎกลาง, tool priority, product dimensions, ขอบเขต (shared foundation) |
| `assortment-summary` | Merchandise Planner | จำนวน SKU / รุ่น (รุ่น-สี) + ราคา + margin แยก dimension (ระบุหน่วยทุกตัวเลข) |
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
| `product_dimension_summary_synapse` | จำนวน SKU / รุ่น / รุ่น-สี + avg tag/selling price + margin% แยก dimension (ต้องระบุหน่วยของจำนวนทุกครั้ง) |
| `product_attribute_values_synapse` | list distinct values ของ attribute (+จำนวน SKU เท่านั้น — ไม่ใช่จำนวนรุ่น/รุ่น-สี) |
| `product_list_synapse` | list SKU รายตัว + attributes |
| `product_query_synapse` | Raw T-SQL (SELECT/WITH) — fallback |
| `describe_table_product_synapse` | Schema lookup |
| `search_columns_product_synapse` | Column search |

## Data Source

- `ai.dim_article` — product master (brand, Level1-5, gender, season, color, size, aging, sales type, vendor, price, cost)
- ไม่มีตัวเลขยอดขาย/สต็อกในตารางนี้

> อัปเดต: ย้ายจาก `silver.sap_article` มาเป็น schema `[ai]` แล้ว (ตารางเดิมยังอยู่แต่เลิกใช้) — คอลัมน์ตัด prefix `S_ATC_` ออก และ join ด้วย `Article_Key`
> ⚠️ `Grade` / `Color_Tone` ว่างทั้งหมด (100% NULL) — ใช้ `Fashion_Grade_Text` / `Color` แทน
> 📌 จำนวน ณ 2026-09-26: SKU 128,121 · รุ่น 23,815 · รุ่น-สี 31,418 — สามหน่วยนี้ไม่เท่ากัน (ต่างกัน ~32%) · "จำนวนรุ่น" = รุ่น-สี

## Usage

- "มีกี่ SKU แยกตามแบรนด์" → `assortment-summary`
- "มีกี่รุ่น-สี แยกตามแบรนด์" → `assortment-summary` (ถาม "กี่รุ่น" ไม่ต้องถามกลับ — ตอบเป็นรุ่น-สี)
- "มีสินค้ากี่ตัว" (ไม่ระบุหน่วย) → **ถามกลับก่อน** ว่า SKU / รุ่น (รุ่น-สี) / ชิ้น
- "มีสีอะไรบ้าง / list สินค้ายีนส์" → `attribute-explorer`
- "โครงสร้างราคาแยก price band" → `pricing-structure`
