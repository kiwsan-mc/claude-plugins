# MCG Deck

MC Group Deck Builder plugin for Claude Code / Cowork / Claude Desktop.

สร้างไฟล์ **.pptx ใหม่** ตาม MC Group house style — generate จาก content JSON ผ่าน `pptxgenjs` โดยคงแม่สี ฟอนต์ และกริดของ MC Group ทุกสไตล์ · design token ถอดมาจาก `AI_Training_Roadmap_FY27_Final.pptx` ตัวจริง

## Skills

| Skill | ทำอะไร |
|---|---|
| `mcgroup-deck` | สร้างเด็คใหม่ 6 สไตล์จาก content JSON (Mode A) หรือ replicate โครงจาก .pptx ที่ผู้ใช้แนบ (Mode B) แล้ว QA สองด่านก่อนส่งมอบ |

## 6 deck styles — แม่สีเดียวกันหมด

| style key | ใช้เมื่อ | archetype หลัก |
|---|---|---|
| (default) | เด็คทั่วไปตาม house style | cover, kpi-bar, timeline, table, two-col, bullets, chart, section, closing, image |
| `executive` | รายงานผู้บริหาร/board, text-heavy | exec-brief |
| `kpi-wall` | dashboard, ยอดขาย, KPI หลายตัว | kpi-wall (6 cards + chart band) |
| `catalog` | เสนอสินค้า/assortment | catalog (3×2 cards + price band) |
| `roadmap` | แผนงาน, milestone | roadmap-h (แถบแนวนอน) |
| `dark` | pitch ระดับสูง, partner proposal | dark-cover |

`build_deck.js` เลือก spec เองตามลำดับ: `--spec` → `content.style` → ชื่อไฟล์ content → `templates.json`

## Routing — กันชนกับ pptx skill

| งาน | ใช้ |
|---|---|
| สร้าง .pptx **ใหม่** (เนื้อหาเป็น text/table/KPI/chart) | `mcgroup-deck` |
| แนบ .pptx มาให้ replicate ทั้งโครง | `mcgroup-deck` (Mode B) |
| อ่าน / สรุป / แก้ / เติม / รวม / แยก / แปลงเป็น pdf / speaker notes | `pptx` skill |

กติกา: มีคำว่า อ่าน/สรุป/แก้/แปลง/รวม/แยก คู่กับไฟล์ .pptx เดิม → `pptx` skill · มีคำว่า สร้าง/ทำ/ออกแบบ ใหม่ + ไฟล์ pptx → `mcgroup-deck` · คลุมเครือ → ทำสองรอบ (อ่านด้วย `pptx`, สร้างด้วย `mcgroup-deck`)

## Setup

Plugin นี้ **ไม่ประกาศ MCP server ของตัวเอง** — ทำงานกับไฟล์ในเครื่องล้วน

- **Node.js + `pptxgenjs`** — environment ของ Claude มีมาให้แล้ว **ห้าม `npm install pptxgenjs`** ให้ `require` ตรง
- **`pptx` skill** — ด่าน QA สองข้อท้าย (`scripts/office/validate.py`, `scripts/thumbnail.py`) ยืม script ของ skill นั้น ต้องติดตั้งไว้ก่อน ไม่งั้นเหลือแค่ `audit_layout.py`

## ข้อจำกัดที่ skill จะบอกผู้ใช้เสมอเมื่อเกี่ยวข้อง

- **validate.py ต้องรันจาก directory ของมันเอง** — helper import พึ่ง cwd ห้ามใส่ `-I` (ต่างจาก `audit_layout.py` ที่ต้องใส่ `-I`)
- **ค่าที่ผู้ใช้ไม่ได้ระบุ → เว้น field + รายงาน "ไม่มีข้อมูล"** — ห้ามแต่งตัวเลข ชื่อ หรือวันที่
- **แก้ generator เท่านั้น** — ถ้า audit/validate ไม่ผ่าน ห้ามแก้ XML ที่ pack แล้วด้วยมือ
- **Mode B ต้องยืนยัน token ก่อน build** — สี/ฟอนต์/กริดที่ถอดได้ต้องให้ผู้ใช้ดูก่อน ไม่ build ต่อทันที

## กฎที่ skill ยึด

- แม่สีคงที่ทุก style: navy `001245` · blue `003DA5` · gold `E6A82D` · slate `667085`/`677794` · ink `151922` · bg `F7F9FC`/`F2F6FB` · line `E8ECF3`/`DCE2EC` · gold_tint `FFF8EA` · red `C00000`
- canvas 16:9 (13.333×7.5) · ฟอนต์ Aptos · margin 0.5 · footer chrome ทุกสไลด์
- ผ่าน `audit_layout.py` (`No layout problems found.`) **และ** `validate.py` (`All validations PASSED!`) ก่อนส่งมอบเสมอ
- ร่าง content JSON ในแชทก่อนเขียนไฟล์

## Version

**v1.0.0** — เปิดตัว พร้อม skill `mcgroup-deck`
- 6 style spec + archetype builder · Mode A (สร้างใหม่) และ Mode B (replicate จากไฟล์แนบ)
- มีตัวอย่าง content JSON ครบทั้ง 6 style และไฟล์ผลลัพธ์ .pptx 5 ไฟล์ (style default ยังไม่มีตัวอย่างผลลัพธ์) ใน `examples/`
