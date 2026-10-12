# MCG Artifact

MC Group Artifact Builder plugin for Claude Code / Cowork / Claude Desktop.

สร้าง dashboard / monitor ยอดขายเป็น **Cowork artifact** ที่ดึงข้อมูลสดผ่าน MCP, cache ไว้ใน `localStorage` และวาดกราฟด้วย Chart.js — รวบแพตเทิร์นที่ผ่านการใช้งานจริงมาแล้ว ไม่ใช่ตัวอย่างบนกระดาษ

## Skills

| Skill | ทำอะไร |
|---|---|
| `artifact-creator` | แพตเทิร์นเชิงเทคนิค 12 หัวข้อสำหรับสร้าง artifact: ถามรูปแบบผลลัพธ์ก่อนเริ่ม · ประตูความซับซ้อน · `callMcpWithTimeout` · แบ่ง query เล็กแล้ว merge ใน JS · ช่วงวันที่แบบ dynamic + Apple-to-Apple · รูปแบบวันที่/ตัวเลข · Chart.js · cache + invalidation · debug box · CSS มาตรฐาน · checklist 20 ข้อ · E2E validation |

## ลำดับการทำงาน

1. **ถามก่อนเสมอ** — ตอบในแชต หรือสร้าง artifact (Step 0)
2. **ถามขอบเขต** ถ้าคำขอคลุมเครือ (Step 0B)
3. **ประตูความซับซ้อน** — ถ้าชนเกณฑ์ ให้แยกเป็นหลาย artifact ไม่ยัดรวม (Step 0C)
4. เลือก skill ของ `mcg-sales-agent` ให้ตรงคำถาม แล้วดึงสูตร KPI/เกณฑ์จาก skill นั้น **ห้ามเดาสูตรเอง**
5. สร้าง artifact ตามแพตเทิร์นในสกิลนี้

## Setup

Plugin นี้ **ไม่ประกาศ MCP server ของตัวเอง** — ข้อมูลมาจาก connector ของ MC Group ที่ติดตั้งอยู่แล้ว (เช่นชุดเดียวกับ `mcg-sales-agent`) ถ้ายังไม่เห็น connector ให้เพิ่มก่อนใช้งาน

## ข้อจำกัดที่สกิลจะบอกผู้ใช้เสมอเมื่อเกี่ยวข้อง

- **`window.cowork.callMcpTool`** — artifact ที่เปิดนอก Cowork จะเรียกไม่ได้ ต้องแสดงข้อความบอกผู้ใช้ ไม่ใช่เงียบ
- **query ใหญ่จะ timeout แบบเงียบ** (~20–25 วินาที) — เพดานจริงคือช่วงข้อมูลราว 1 เดือนต่อ query
- **ไม่เกิน 4 query ต่อ artifact** — เกินกว่านั้นแปลว่า artifact ใหญ่เกิน ต้องแยก
- **cache หมดอายุข้ามวัน** — วันที่เปลี่ยนจะล้าง cache แล้วรอผู้ใช้กด Refresh เอง
- **ห้าม auto-load ตอนเปิดหน้า** — ต้นเหตุอันดับหนึ่งของ permission popup ที่ผู้ใช้ไม่ต้องการ

## กฎที่สกิลยึด

- ห้ามเดาตัวเลขหรือสูตร KPI — ทุกตัวต้องมาจากผลการเรียก tool ในบทสนทนานั้น หรือจาก skill ของ `mcg-sales-agent`
- วันที่ทุกตัวที่ผู้ใช้เห็นต้องผ่านฟังก์ชันจัดรูปแบบแล้ว — ห้ามหลุดเป็น ISO string
- `saveCache()` ต้องเรียก **ก่อน** `renderAll()` เพราะ `renderAll()` แก้ข้อมูลในที่ (เติม `margin`, `abc`, `cumPct`)
- ES5 เท่านั้น (`var`, `function`) — sandbox ของ artifact ไม่รับ `const`/`let`/arrow
- artifact ที่ชนเกณฑ์ความซับซ้อน **ห้ามฝืนสร้าง** ให้แยกเป็นชุดที่มี prefix ตรงกัน

## Version

**v1.0.0** — เปิดตัว พร้อม skill `artifact-creator` v3
- รวม 12 หัวข้อ: ขั้นตอนถาม/คัดกรอง 4 ขั้น, แพตเทิร์นเทคนิค 8 หัวข้อ, ตารางปัญหาที่พบบ่อยและวิธีแก้, checklist 20 ข้อ, E2E validation
- cache + auto-invalidation เป็นข้อบังคับ ไม่ใช่ตัวเลือก — เพราะเป็นตัวกัน permission popup โดยตรง
- CSS มาตรฐานชุดเดียว (Fashion Island Clean Style) แทน header สีเข้มแบบเดิม
