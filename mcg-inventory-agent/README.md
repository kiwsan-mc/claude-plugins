# MCG Inventory Agent

MC Group Inventory Analyst Agent plugin for Claude Code / Cowork.

ถามข้อมูลสินค้าคงคลัง (stock on hand, aging, PO, STO) ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน Synapse MCP tools.

> 📌 **ศัพท์ MCG:** การสั่งซื้อเข้า/PO = **"Sales In"** (skill `po-intake`) · ยอดขาย = **"Sales Out"** → ใช้ `mcg-sales-agent`

## Version

**v1.3.2** — กฎหน่วยจำนวน + รับของเข้าตอบเป็นชิ้น
**v1.3.2** — กฎหน่วยจำนวน ("จำนวนรุ่น" = รุ่น-สี) + กฎ **"รับของเข้า → ตอบจำนวนชิ้น"**: ตอบ GR Qty เป็นตัวเลขหลัก ไม่ยกมูลค่าขึ้นนำ · `po-intake` ปรับ Headline/ตารางให้เป็นชิ้น + มีหน่วยทุกคอลัมน์ · tool ฝั่ง stock/PO/STO เพิ่ม `model_color_count` และเรียงตามจำนวนชิ้น

- **v1.3.1**: **ปลายทางโอน** เพิ่มขั้น **T3 (รุ่นเดียวกัน คนละสี)** ปิดช่องที่ตอบ "ไม่มีปลายทางโอน" ผิด ๆ (ตรวจ 2026-09-25: **17,212 คู่ / 310 รุ่น-สี** ที่ T1/T2 ว่างแต่ T3 เจอ) · ปลายทาง T3 ที่**ถือสีเดียวกันค้างอยู่จะถูกตัดออก** · เตือน **`Salesman_Employee_Code = 999999` ("OTHERS") ใช้ร่วม 1,070 สาขา** ⇒ "salesman เดียวกัน" ของกลุ่มนี้ไม่ใช่พื้นที่จริง ต้องกำกับ · **ห้ามเขียน query เองเพื่อกรองแคบกว่า tool** (เคสจริง: กรอง "ไม่เคยขาย ≥180 วัน" แล้วได้กลุ่มที่ไม่มีใครขายเลย ⇒ ตารางปลายทางว่างทั้งกระดาน) · ถ้าไม่มีปลายทางทั้ง T1–T3 **ต้องมีประโยค fallback (clearance / คืน vendor)** · ห้ามพิมพ์ชื่อตาราง/คอลัมน์ในคำตอบรวมทั้ง Data Footer
- **v1.3.0**: สต็อกมี **2 ฐาน** — default ของธุรกิจคือ**ฐานคงเหลือ** (`Stock_Quantity`) ตอบคู่กับ**ฐานรวมทั้งหมด** (`Stock_Total_*`) เสมอ · **"ของค้าง" นิยามใหม่ = ไม่มีขายที่ร้าน OFFLINE ≥30/60/90 วัน** (แยกจาก aging สี) และ **ต้องแนบตาราง Stock QTY by TOP 10 Model Color** ใน 3 คำถาม (ของค้างมีเยอะไหม / เงินจมในสต็อกเท่าไหร่ / ของค้างเกิน 6 เดือนมีไหม) · **PO ค้างส่ง = `Still_To_Delivery_*`** ไม่ใช่ `Open_Quantity` · เพิ่ม skill `po-analysis` (มุมรวม PO+STO) · แก้คำเตือน "ตารางรายวันล่าช้า" ซึ่งหมดจริงแล้ว (ข้อมูลถึง 2026-09-23)
- **v1.2.0**: ย้ายจาก `gold.script_stock_daily*` / `silver.sap_po` / `silver.sap_sto` ไป `ai.fact_MB52` / `ai.fact_sales_and_stock_daily` / `ai.fact_stock_month_ending` / `ai.fact_po_sto`; เพิ่มกฎต้อง filter `Item_Category` สำหรับ PO/STO
- **v1.1.0**: เพิ่ม freshness + validation rules
- **v1.0.0**: เริ่มต้น — inventory domain

## Skills

| Skill | Role | หน้าที่ |
|-------|------|---------|
| `inventory-agent` | Inventory Agent | กฎกลาง, tool priority, aging zones, snapshot rules (shared foundation) |
| `stock-health` | Stock Health Analyst | สต็อกคงเหลือปัจจุบันแยก aging/brand/region + สินค้าเสี่ยง clearance + ของค้าง/เงินจม + **ตารางบังคับ TOP 10 Model Color** |
| `stock-trend` | Inventory Planner | สต็อกย้อนหลัง time series + เปรียบเทียบช่วงเวลา |
| `po-intake` | Procurement Analyst | **Sales In** (PR/PO/GR/open qty) แยก vendor/สาขา + fulfillment — **PO เท่านั้น** |
| `sto-transfer` | Distribution Analyst | โอนย้ายสต็อกระหว่างสาขา + open transfer — **STO เท่านั้น** |
| `po-analysis` | Procurement & Transfer Analyst | **มุมรวม PO+STO** — ค้างส่ง, ตามรอบเวลา, Vendor Performance แยกชั้น PO/STO |

## Architecture

```
skills/
├── inventory-agent/    ← SKILL.md หลัก (rules, tool priority, aging, snapshot pinning)
├── stock-health/       ← #[[file:../inventory-agent/SKILL.md]] + role prompt
├── stock-trend/        ← #[[file:../inventory-agent/SKILL.md]] + role prompt
├── po-intake/          ← #[[file:../inventory-agent/SKILL.md]] + role prompt
├── sto-transfer/       ← #[[file:../inventory-agent/SKILL.md]] + role prompt
└── po-analysis/        ← #[[file:../inventory-agent/SKILL.md]] + role prompt (มุมรวม PO+STO)
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

## Stock on Hand Measures (สต็อกคงเหลือ)

`stock_on_hand_synapse` และ `stock_value_by_aging_synapse` คืน 4 measure มาตรฐานนี้:

**⚠️ สต็อกมี 2 ฐาน (basis) — ตอบคู่กันเสมอ** (ดู §5.2 ของ inventory-agent)

| ฐาน | จำนวน | ต้นทุน MV | ต้นทุน STD | ราคาขาย |
|-----|--------|-----------|------------|---------|
| **คงเหลือ** ← default ของธุรกิจ | `Stock_Quantity` | `Stock_Amount` | `Stock_Amount_Standard` | คำนวณ `Selling_Price × Stock_Quantity` |
| **รวมทั้งหมด** | `Stock_Total_Quantity` | `Stock_Total_Amount` | `Stock_Total_Amount_Standard` | `Stock_Total_Selling_Price` |

> ✅ สมการที่พิสูจน์แล้ว: `Stock_Total_Quantity` = `Stock_Quantity` + `Intransit_Quantity` + `Blocked_Quantity` (2026-09-22: 4,949,274 + 83,413 + 7,706 = **5,040,393**)
>
> ⚠️ `stock_on_hand_synapse` / `stock_value_by_aging_synapse` คืน **ฐานรวมทั้งหมด** — ถ้า user ถาม "สต็อกคงเหลือ" ต้องดึงฐานคงเหลือด้วย `inventory_query_synapse` (ถ้าไม่ จะเกินจริง 91,119 ชิ้น / +1.84%)
>
> ⚠️ `Stock_Total_*` มีเฉพาะ `ai.fact_MB52` และ `ai.fact_stock_month_ending` — `ai.fact_sales_and_stock_daily` **ไม่มี** → trend/YoY ทำได้เฉพาะ**ฐานคงเหลือ** (`Stock_Quantity` + `Stock_Amount_Standard`) ซึ่งตรงกับ default พอดี
>
> ✅ `stock_on_hand_yoy_synapse` **ใช้ได้แล้ว** (ตรวจ 2026-09-24) — เคยคืน `qty_curr` = 0 ตอนตารางรายวันหยุดที่ 2026-08-13 แต่ถูกเติมครบถึง 2026-09-23 แล้ว

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
- "PO+STO ค้างส่งรวมเท่าไหร่" / "vendor performance ทั้ง PO และ STO" → `po-analysis`
