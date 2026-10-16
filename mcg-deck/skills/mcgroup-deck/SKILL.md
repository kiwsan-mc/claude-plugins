---
name: mcgroup-deck
description: สร้างไฟล์ .pptx ใหม่ตาม MC Group house style — มี 6 deck style (house default, executive, kpi-wall, catalog, roadmap, dark) คงแม่สี MC Group ผ่าน build_deck.js + templates*.json หรือ replicate จาก template .pptx ใด ๆ ที่ผู้ใช้แนบมา (Mode B: extract_spec.py แล้ว build ตามโครงเดิม) ใช้เมื่อผู้ใช้สั่ง "สร้าง/ทำ/ออกแบบ presentation, slide, deck, พาวเวอร์พอย เป็นไฟล์ pptx" ที่ไม่มีไฟล์ต้นฉบับมาให้แก้ ห้ามใช้ skill นี้ อ่าน/แก้/แปลงไฟล์ pptx เดิม — งานนั้นใช้ pptx skill แทน
---

# mcgroup-deck — MC Group PPTX builder skill

สร้างไฟล์ .pptx ตาม MC Group house style โดย generate จาก content JSON ผ่าน pptxgenjs.
Design token / grid / archetype ถอดมาจาก `AI_Training_Roadmap_FY27_Final.pptx` ตัวจริง (ตรวจแล้วด้วย validate.py + audit_layout.py + thumbnail)

## Routing — กันชนกับ pptx skill (สำคัญมาก)

| งาน | ใช้ |
|---|---|
| **สร้างไฟล์ .pptx ใหม่** (user สั่ง "สร้าง/ทำ/ออกแบบ deck" ให้เนื้อหาเป็น text/table/KPI/chart) | **mcgroup-deck (skill นี้)** |
| ผู้ใช้แนบ .pptx มาเป็น template ที่อยาก replicate ทั้งโครง (Mode B) | **mcgroup-deck** (run extract_spec.py บนไฟล์นั้นก่อน) |
| **อ่าน / สรุป / แก้ไข / เติม / รวม / แยก / split / merge / แปลงเป็น pdf / speaker notes / comments** ของไฟล์ .pptx เดิม | **pptx skill** |
| .pptx แนบมาให้แก้เนื้อหาในสไลด์เดิม | **pptx skill** (unzip → edit XML → zip) |

กติกา: ถ้า prompt มี อ่าน/สรุป/แก้/แปลง/รวม/แยก ประกอบไฟล์ .pptx เดิม → pptx skill.
ถ้า prompt มี สร้าง/ทำ/ออกแบบ ใหม่ + ไฟล์ pptx → mcgroup-deck.
ถ้าคลุมเครือ (เช่น "แก้แล้วบันทึกเป็นไฟล์ใหม่") → ทำสองรอบ: อ่านด้วย pptx skill, สร้างด้วย mcgroup-deck.

## Assets

ทุก path อ้างอิงจาก root skill dir (โฟลเดอร์ที่มีไฟล์ SKILL.md นี้):

```
SKILL.md                              ไฟล์นี้
reference/templates.json              house style (default)
reference/templates-executive.json    Executive Brief
reference/templates-kpi-wall.json     Data / KPI Wall
reference/templates-catalog.json      Product Catalogue
reference/templates-roadmap.json      Timeline / Roadmap (horizontal)
reference/templates-dark.json         Dark Premium
scripts/extract_spec.py               .pptx → spec JSON (Mode B / QA)
scripts/archetypes.js                 builder ต่อ archetype + ต่อ style
scripts/build_deck.js                 CLI: content.json → deck.pptx (auto-pick style)
scripts/make_style_specs.js           regenerate 5 style specs จาก base
scripts/audit_layout.py               layout QA: off-canvas / overflow / overlap / txt-clip
examples/demo*.json                   ตัวอย่าง content ต่อ style
examples/out/demo-*.pptx              ตัวอย่างผลลัพธ์ (ทุก style ผ่าน audit+validate)
```

ถ้า path ข้างต้นหาไม่เจอ ให้แจ้งผู้ใช้ว่า assets หาย — อย่าสร้าง script ขึ้นมาใหม่ทั้งฉบับ

**Dependencies:** Node.js + `pptxgenjs` (preinstalled ใน Claude environment — ห้าม `npm install pptxgenjs` ก่อน ให้ require ตรง). Validation ต้องมี pptx skill ในเครื่อง (ใช้ `scripts/office/validate.py` + `scripts/thumbnail.py` ของ skill นั้น)

## Deck styles (6) — แม่สี MC Group เดียวกันทุกแบบ

คงที่ทุก style: canvas 16:9 (13.333×7.5), palette (navy `001245` / blue `003DA5` / gold `E6A82D` / slate `667085`,`677794` / ink `151922` / bg `F7F9FC`,`F2F6FB` / line `E8ECF3`,`DCE2EC` / gold_tint `FFF8EA` / red `C00000`), ฟอนต์ Aptos, margin 0.5, footer chrome.

| style key | ไฟล์ spec | ใช้เมื่อ | archetype หลัก |
|---|---|---|---|
| (default) | `templates.json` | เด็คทั่วไปตาม house style | cover, kpi-bar, timeline, table, two-col, bullets, chart, section, closing, image |
| `executive` | `templates-executive.json` | รายงานผู้บริหาร/board, text-heavy | **exec-brief**, cover, table, bullets, chart |
| `kpi-wall` | `templates-kpi-wall.json` | dashboard, ยอดขาย, KPI หลายตัว | **kpi-wall** (6 cards + chart band), cover, chart |
| `catalog` | `templates-catalog.json` | เสนอสินค้า/assortment | **catalog** (3×2 cards + price band), cover, two-col |
| `roadmap` | `templates-roadmap.json` | แผนงาน, milestone | **roadmap-h** (แถบเวลานอน), cover, bullets |
| `dark` | `templates-dark.json` | pitch ระดับสูง, partner proposal | **dark-cover**, kpi-bar, section, chart, closing |

### วิธีเลือก style

`build_deck.js` เลือก spec อัตโนมัติ ตามลำดับ:
1. `--spec <file>` (บังคับ)
2. `content.style` (เช่น `"style": "catalog"`)
3. ชื่อไฟล์ content มี style key (เช่น `q4-catalog.json` → catalog)
4. ไม่ตรง → `templates.json` (default)

## Workflow (ทำตามลำดับ)

1. **เลือก Mode + Style**
   - Mode A (default): ไม่มีไฟล์แนบ → เลือก style จากตารางข้างบน
   - Mode B: ผู้ใช้แนบ .pptx เป็น template → รัน extract_spec.py แล้วรายงาน token ที่ถอดได้ (สี/ฟอนต์/กริด) ให้ผู้ใช้ยืนยันก่อน build
2. **ร่าง content JSON** ในแชทก่อนเสมอ (กติกาองค์กร: draft ในแชทก่อนสร้างไฟล์) ตาม schema `content_contract` ใน spec แล้วจึงเขียนไฟล์
3. **Build:**
   ```bash
   node scripts/build_deck.js content.json -o Out.pptx                                     # style from content.style / filename
   node scripts/build_deck.js content.json -o Out.pptx --spec reference/templates-catalog.json  # force style
   ```
4. **Validate (ห้ามข้าม):** สองด่าน
   ```bash
   python3 -I scripts/audit_layout.py Out.pptx                       # off-canvas / overflow / overlap / txt-clip
   python3 <pptx skill dir>/scripts/office/validate.py Out.pptx      # OOXML schema/rels/content-type
   ```
   ต้องได้ `No layout problems found.` และ `All validations PASSED!` ก่อนส่งมอบ
   validate.py ต้องรันจาก directory ของมันเอง (helpers import พึ่ง cwd) — ห้ามใส่ `-I`
5. **Visual check:** รัน thumbnail.py ของ pptx skill → Read ภาพ เทียบ grid
6. **ส่งมอบ:** copy .pptx สู่โฟลเดอร์ที่ผู้ใช้เข้าถึง แล้วให้ link `computer://` ในคำตอบสุดท้าย

## Archetypes ทั้งหมด

**base (ใช้ได้ทุก style):** `cover`, `closing`, `section`, `kpi-bar`, `timeline`, `table`, `two-col`, `bullets`, `chart`, `image`
**style-specific:** `exec-brief` (executive), `kpi-wall` (kpi-wall), `catalog` (catalog), `roadmap-h` (roadmap), `dark-cover` (dark)

ทุก archetype ได้ frame: top band navy h=0.09, header MC GROUP ซ้าย-ขวา, footer rule y=6.86 + text y=6.98.
cover/closing/dark-cover พิมพ์บน dark slide background; content พื้นขาว (ยกเว้น slide.dark=true)

## กติกา pptxgenjs (footguns — ห้ามละเมิด)

1. `pres.layout` ก่อน `addSlide` เสมอ
2. hex 6 หลัก ไม่มี `#` ไม่มี alpha
3. option object ใหม่ต่อการเรียกทุกครั้ง (library mutates in place)
4. `isTextBox: true` ทุก addText ที่ไม่มี placeholder
5. `margin: 0` เมื่อ text ต้อง align กับ shape
6. bullets: rows array + `bullet:{code:"25CF"}` ต่อ paragraph — ห้าม bullet:true ซ้ำ (double bullet), ห้ามพิมพ์ `•` เองในข้อความ
7. chart: series เดียว → สีเดียว; หลาย series → cycle palette; stacked ใช้ `dataLabelPosition` ∈ {ctr,inEnd,inBase} เท่านั้น
8. chart ที่ฝังใน slide อื่น (kpi-wall) → ส่ง `_embedded: true` เพื่อไม่วาด chrome ซ้ำ (header/footer จะซ้อนกัน ไม่งั้น audit จับ overlap)
9. notes → `slide.addNotes()` เท่านั้น
10. ค่าที่ user ไม่ได้ระบุ → เว้น field นั้น + รายงาน "ไม่มีข้อมูล" — ห้าม fake ข้อมูล
11. build เสร็จ → audit + validate ต้องผ่านก่อนส่งมอบ; ไม่ผ่าน → แก้ generator ห้ามแก้ packed XML ด้วยมือ

## Extract spec (Mode B / QA)

```bash
python3 -I scripts/extract_spec.py deck.pptx -o /tmp/spec.json --pretty
```
คืนค่า: canvas, theme colors+fonts, palette histogram (top-30), grid (margin/footer/top-band), archetype ต่อสไลด์.
Classification rules:
- `p:bg` navy ∈ {001245,142A60,...} → cover (มี THANK YOU → closing)
- gold side-rule (h≥1.5, w≤0.2) + shapes≤14 → section
- dots ≥3 (0.14–0.26 sq) → timeline
- cards 2.8–3.2 × 0.85–1.15 ≥3 → kpi-bar
- zebra rows ≥4 หลาย fill → table
- pic ไม่มี text → image

## ตัวอย่างสั่ง

- "ทำ ppt เสนอขาย FY27" → Mode A, default style
- "ทำ deck dashboard ยอดขาย 6 KPI" → style `kpi-wall`
- "ทำ catalogue สินค้า 6 ตัว" → style `catalog`
- "ทำ roadmap แนวนอน" → style `roadmap`
- "ทำ pitch partner โทนเข้ม" → style `dark`
- "ทำ presentation ใหม่ ให้โครงเหมือนไฟล์แนบนี้" (แนบ .pptx) → Mode B: extract → ยืนยัน spec → build
- "สรุป/แก้ ไฟล์ pptx นี้" → ส่งต่อไป pptx skill

## Pre-flight checklist

- content.json ครบ fields ตาม contract ของ style ที่เลือก
- ไม่มีข้อมูลปลอม — ทุกตัวเลข/ชื่อ/วันที่ อ้างอิง source จริงของ user
- audit_layout.py → No layout problems found.
- validate.py → All validations PASSED!
- thumbnail → สี ตำแหน่ง ถูกต้อง
- ไฟล์สุดท้ายพร้อม computer:// link