# MCG Sales Agent

MC Group Data Analyst Agent plugin for Claude Code / Cowork.

ถามข้อมูลยอดขาย Retail/Fashion ด้วยภาษาธรรมชาติ (Thai/English) ผ่าน MCP tools ที่เชื่อมต่อ PostgreSQL (pgvector).

> 📌 **ศัพท์ MCG:** ยอดขาย = **"Sales Out"** (plugin นี้) · การสั่งซื้อเข้า/PO = **"Sales In"** → ใช้ `mcg-inventory-agent` (po-intake)

## Version

**v5.22.1** — ถอดค่าที่ปักไว้ + lint กันไม่ให้กลับมา
- **v5.22.1**: กวาดค่าที่ปักไว้ในกฎออกจาก `member-analysis` · `member-by-branch` · `sales-agent` (2026-10-05): จำนวนสาขา `~88` และข้ออ้าง "~55% vs ~16%" ⇒ เปลี่ยนเป็นข้อความที่ไม่ผูกตัวเลข พร้อมเคสจริงที่ไม่เหลือตัวเลขให้ลอก — ข้ออ้างนั้น **พิสูจน์แล้วว่า stale** เพราะตั้งแต่ 2026-08-01 คอลัมน์ member ของฝั่ง Sales Out เป็น 0
- **v5.22.1**: เพิ่ม `tools/check-pinned-values.py` + เทสต์ 15 เคส ที่ระดับ repo — กฎข้อนี้มีอยู่แล้วเป็นตัวอักษรและยังสะสมได้ 18 จุด จึงย้ายมาเป็นเครื่องมือตรวจ · ตั้งใจให้ **แคบ** (ไม่ยิงใส่แถว threshold อย่าง `≥80%=🟢`) และ **advisory เป็นค่าเริ่มต้น** เพราะยังยิงเกินใน 2 รูปที่กฎอนุญาต (ตารางหลักฐาน และ ratio ที่บรรยายรูป bug) ซึ่งเขียนเป็นเทสต์ยืนยันไว้ ไม่ใช่กลบ

**v5.22.0** — เปิดใช้ Answer Term Guard เป็น Stop hook (ยืนยันแล้วว่า Cowork รัน hook ได้)
- **v5.22.0**: ปิดคำถามค้างจาก v5.21.0 ว่า "Cowork รัน plugin hook หรือไม่" — **รันได้** หลักฐาน: สเปกปลั๊กอินของ Cowork (`cowork-plugin-management/0.2.2` → `references/component-schemas.md`) ระบุ `hooks/hooks.json` · event `Stop` = "When Claude finishes a response" · command hook คืน `{"decision":"block","reason":"..."}` ⇒ payload ที่เขียนไว้ตั้งแต่ v5.21.0 ถูกต้องอยู่แล้ว · และในเครื่องนี้มีหลักฐาน hook **ยิงจริง** — ปลั๊กอิน CockroachDB ใต้ `rpm\plugin_01J1ZUJcofzWJxiajSBsZ8US` มี `hookEvent: PostToolUse` พร้อม `blockingError` ใน transcript
- **v5.22.0**: ⚠️ **ข้อจำกัดที่พบทีหลังและสำคัญกว่า**: hook โหลดเฉพาะปลั๊กอินที่มาทาง **marketplace/plugin route** — ในเครื่องนี้ `rpm\plugin_*` มี 20+ ปลั๊กอิน (CockroachDB, Figma, Zoom, Box …) แต่ **ไม่มีปลั๊กอิน mcg ตัวใดเลย** และ manifest ของเส้นทาง Skills panel ก็ไม่มี mcg ⇒ ถ้า skill ไปถึง Desktop ทาง Skills panel อย่างเดียว hook จะไม่โหลด ⇒ **ยังไม่ยืนยันว่า hook นี้ยิงจริงใน Cowork ของเรา** ต้องพิสูจน์ด้วยการนับ `hookEvent` ใน transcript (คำสั่งอยู่ใน README หัวข้อ Answer Term Guard) · อีกกับดัก: transcript เคยบันทึก hook ที่ล้มเพราะพาธเพี้ยนเป็น `C:\c\Users\...`
- **v5.22.0**: เพิ่ม `hooks/hooks.json` (event `Stop`, `timeout` 20s) + `hooks-handlers/run-check.sh` ที่เลือก interpreter เองตามลำดับ `ANSWER_GUARD_PYTHON` → `py -3` → `python3` → `python` — เลือก `py` ก่อนเพราะบน Windows `python`/`python3` มักเป็น alias ของ Microsoft Store ที่อาจค้าง (บนเครื่องนี้ทั้งคู่เป็น stub)
- **v5.22.0**: **กัน loop** — handler ปล่อยผ่านทันทีถ้า payload มี `stop_hook_active` ⇒ false positive จะไม่วน block ซ้ำ · และ **fail open ทุกทาง** (transcript อ่านไม่ได้ · ไม่มี interpreter · ตัดสินไม่ทันใน timeout) ⇒ ไม่มีทางที่ hook ที่พังจะค้างคำตอบผู้ใช้
- **v5.22.0**: ใช้ hooks.json **แบบ flat** (event ระดับบนสุด) ตามสเปก Cowork — ต่างจาก `explanatory-output-style` ของ Anthropic ในรีโปนี้ที่ห่อด้วย key `hooks` ⇒ ถ้าฝั่ง Claude Code ไม่ยิง hook ให้สลับไปแบบห่อ
- **v5.22.0**: เทสต์ 18 เคส — เพิ่มเคส `stop_hook_active` ปล่อยผ่านแม้ข้อความสกปรก, transcript ไม่มี path, และยิง launcher จริง 3 ทาง (สกปรก → block · สะอาด → เงียบ · ไม่มี interpreter → exit 0)

**v5.21.0** — Answer Term Guard: ตรวจคำต้องห้ามด้วยเครื่อง ไม่ใช่ให้โมเดลตรวจตัวเอง
- **v5.21.0**: รอบที่ 2 ของเคสเดิม (2026-10-05) คำตอบยังหลุด — รอบนี้หลุด**หนักกว่าเดิม** โดยพิมพ์ `Branch_Code` · `dim_branch` · `Branch_Code_Key` · `Branch_Code_And_Text` · `Store_Name` · `Branch_Text` ใน**กล่อง Insight** และพิมพ์ `ai.poc_fact_sales_with_crm + ai.dim_branch` ใน **footer** ⇒ สรุปว่าการเพิ่มข้อความห้ามอย่างเดียวถึงเพดานแล้ว (สองรอบ สองครั้งที่หลุด) จึงเพิ่ม **ตัวตรวจที่รันได้จริง** แทนการพึ่ง self-check: `answer-guard/check_answer_terms.py` ใช้เกณฑ์จับคำ 6 ข้อเดียวกับ §1 (ขึ้นต้น `ai.` · ลงท้าย `_synapse`/`_count`/`_key`/`_model`/`_color`/`_quantity` · ฟังก์ชัน SQL · snake_case/Pascal_Snake · ชื่อ tool/MCP · ชื่อระบบ) · ยกเว้นบรรทัด 🔒 (ตารางสูตร) · CLI ใช้ได้ทั้งไฟล์และ stdin และคืน exit 1 เมื่อพบ
- **v5.21.0**: เทสต์ 16 เคส (`answer-guard/tests/`) — ฝั่ง fail ใช้**ข้อความจริงที่หลุดถึงผู้ใช้ทั้งสองรอบ** (ไม่ใช่ตัวอย่างสมมติ) ยืนยันจับได้ครบ 11 token · ฝั่ง pass ใช้ข้อความธุรกิจที่มีตัวเลข/หน่วย/฿/ไทย เหมือนคำตอบจริง เพื่อกัน false positive · ครอบคลุม edge case: token ซ้ำนับครั้งเดียว · 🔒 ยกเว้น · transcript อ่านไม่ได้ = **fail open** · ตัดสินเฉพาะ assistant turn สุดท้าย (turn เก่าที่หลุดแล้วไม่ทำให้บล็อกซ้ำ และ turn เก่าที่สะอาดไม่กลบ turn สุดท้ายที่หลุด)
- **v5.21.0**: แนบ Stop-hook handler `hooks-handlers/check_answer_terms_stop.py` **แต่ยังไม่เปิดใช้** — ต้องยืนยันก่อนว่า Cowork/Claude Desktop รัน plugin hook (เคสที่หลุดเกิดบน Desktop) และต้องแก้ชื่อ interpreter ให้ตรงเครื่อง (บน Windows `python` อาจเป็น alias ของ Microsoft Store ที่ค้าง) ⇒ วิธีเปิดและข้อควรระวังอยู่ใน README หัวข้อ "Answer Term Guard"

**v5.20.1** — แก้ 3 ต้นเหตุจากเคสจริง (Claude Desktop, 2026-10-05)
- **v5.20.1**: เคส "Top 10 % Member Sales Contribution" ที่คำตอบออกมาเป็นยอดรวมก้อนเดียว 18.4% และพิมพ์ชื่อคอลัมน์ลงคำตอบ ⇒ แก้ที่ต้นเหตุ 3 จุด (1) **กฎการจัดอันดับ** — `member-by-branch` บังคับว่าคำถามที่มี "Top N / อันดับ / สาขาไหนมากสุด" ต้องได้**ตารางที่มี 1 แถวต่อ 1 รายการ + คอลัมน์อันดับ + ระบุมิติและตัวชี้วัดที่ใช้จัดอันดับ** · 🚫 ห้ามตอบด้วยยอดรวม · ไม่ระบุมิติ/ตัวชี้วัด → ถามกลับด้วย `AskUserQuestion` (2) **กฎนิยาม member** — "สมาชิก" มี 2 ฐาน (ฐานใบเสร็จ vs ฐานยอดขาย) ที่ให้ค่าไม่ตรงกัน ต้องระบุฐานทุกครั้ง ห้ามสลับกลางคำตอบ · ถ้าค่าที่ได้ขัดกับตัวเลขที่ธุรกิจเคยรายงาน **ให้บอกว่าขัด ไม่ใช่ปรับตัวเลขให้ดูเข้าท่า** · และต้องเทียบช่วงเวลา/ขอบเขตสาขา/ฐานให้เป็นเนื้อเดียวกันก่อนสรุป (เคสจริง: 178.17M ของเดือนเดียว vs 184.5M ของทั้งไตรมาส) (3) **🔒 ปิดตารางสูตรเป็นเอกสารภายใน** — เพิ่ม fence ห้ามคัดลอกชื่อคอลัมน์/ฟังก์ชันจากตารางสูตรลงคำตอบ ใน `member-by-branch` · `member-analysis` · `sales-dashboard` (ตามบทเรียน v1.1.11 ที่แก้เฉพาะประโยคกฎ แต่ตารางสูตรยังเป็นแหล่งที่โมเดลลอกคำไปพิมพ์)
- **v5.20.1**: แก้ routing ที่ชนกัน — `sales-dashboard` มีแถว KPI สมาชิกอยู่ในตารางสูตรทั้งที่ description ประกาศว่า SALES ONLY ⇒ agent โหลด `sales-dashboard` มาถาม member · เพิ่มบรรทัดขอบเขตทั้งใน description และเหนือตารางสูตร: คำถามที่มี member เป็นแกน → `member-analysis` / `member-by-branch` และ `member-analysis` เพิ่มทางออกไป `member-by-branch` สำหรับคำถามรายสาขา/จัดอันดับ · เพิ่ม trigger eval ของ `member-by-branch` เป็น 26 เคส (positive 14) ตรวจแล้ว **178 วลีรวมทั้งปลั๊กอิน ไม่มีวลีใดชนกับ positive ของสกิลอื่น**

**v5.20.0** — เพิ่ม skill `member-by-branch` (ตารางรายสาขา member + ใบเสร็จ)
- **v5.20.0**: เพิ่มสกิลที่ 17 `member-by-branch` ปิดช่องว่างที่พบจากเคสจริง (2026-10-05): dashboard "Customer Overview" แสดงตาราง **รายสาขา** ที่มีทั้งยอดขาย ใบเสร็จ และสัดส่วนสมาชิก แต่เดิม**ไม่มีสกิลใดในปลั๊กอินนี้รับคำถามแบบนั้นเลย** (`member-analysis` = ระดับบริษัท/ช่องทาง/generation · `sales-dashboard` = SALES ONLY ไม่มี KPI สมาชิก) ⇒ สกิลใหม่กำหนด grain = สาขา และนิยาม KPI จาก `member_type` / `member_count` / `ticket_count` / `member_group` (ลูกค้าใหม่) · ยกกฎ `AND ticket_count > 0` กัน member tickets ติดลบจากแถว return มาด้วย · เพิ่ม trigger eval 20 เคส และตรวจแล้ว **ไม่มีวลีใดชนกับ positive ของสกิลอื่น** (รวมทั้งปลั๊กอิน 174 วลี) · ระบุข้อจำกัด: คอลัมน์สาขาต้องยืนยันด้วย `pg_describe_table` ก่อน raw query (ห้ามเดาชื่อคอลัมน์) และห้ามนำตัวเลขข้าม platform มาเทียบกัน

**v5.19.21** — เลิก hardcode ช่วงปี FY ในตัวอย่าง SQL
- **v5.19.21**: กวาดทั้งชุดหาค่าที่ "ผูกตาย" ตามบทเรียนจากเคสภูมิภาค: พบตัวอย่าง SQL ที่ hardcode ช่วงปี FY (`'2026-07-01' AND '2026-07-27'`) 8 จุดใน `sales-agent` (6) + `artifact-creator` (2) ซึ่ง **ขัดกับกฎของไฟล์เอง** (ห้าม hardcode ปี) ⇒ เปลี่ยนเป็น placeholder `<fy_curr_start>` / `<max_date>` / `<fy_prev_start>` / `<same_day_prev>` ⇒ ถ้า agent คัดลอกไปใช้ จะดึงจาก anchor เสมอ ไม่ค้างปีเก่า
- **v5.19.20**: เพิ่มกฎ **ห้าม hardcode ค่าภูมิภาค** (ค่ามัน dynamic): ให้ดึงค่าจริงจากระบบก่อนจัดกลุ่ม/รายงาน · ถ้าชื่อที่ผู้ใช้ถามไม่มีในผลลัพธ์ ให้ **เตือนว่าป้ายชื่อถูกจัดกลุ่มใหม่** ไม่ใช่ตอบ 0 · 🚫 ห้ามสรุป "ยอดตก" จากชื่อที่จับคู่ไม่ตรง (ชื่อเปลี่ยน ≠ ยอดหาย) · แนบหลักฐานประกอบแบบระบุวันที่ (2026-09-30): ชุดภูมิภาคเป็นชื่อรวมกลุ่ม กลุ่ม Mobile มี 1–2 สาขา/ภูมิภาค จึงไม่ใช่สาเหตุของยอดตกก้อนใหญ่
- **v5.19.19**: ปิดเคส "ยอดหาย 2.9M" ตามที่ธุรกิจสั่ง: กำหนด **แหล่งมาตรฐานของยอดขาย = "Sales Out" จาก mcg-sales** ในกฎของทุกสกิล (38 ไฟล์) — ถ้าใช้หลายแหล่งต้องเรียกชื่อเป็นภาษาธุรกิจ ("Sales Out (mcg-sales)" · "ยอดขายบริษัท (invoice)") และ **ห้ามพิมพ์ชื่อตาราง/ระบบในคำตอบหรือ footer** (เคสจริง: footer หลุด `mcg_aiplatform_sales` และคำตอบสลับระหว่างฝั่ง invoice 294.02M กับ Sales Out 296.94M) · `target-achievement` เพิ่มกฎ: ยอดขายจริงสำหรับเทียบเป้าใช้ Sales Out + กฎ VAT (เป้า incl VAT vs Sales Out excl VAT ต้องกำกับฐาน) + ห้ามสลับแหล่งกลางคำตอบ + ทุกตารางใช้ช่วงวันที่เดียวกับ Headline
- **v5.19.18**: ใช้ข้อเสนอ P6: เพิ่ม **trigger eval ให้ครบ 38/38 สกิล** (เดิมมีแค่ 5 ของ inventory) — รวม **655 เคส** (positive 427 · negative 228) · ตรวจแล้ว: JSON ถูกต้องทุกไฟล์ · ไม่มีคำถามซ้ำในไฟล์ · **ไม่มีวลีใดเป็น positive ของมากกว่า 1 สกิล** (ข้อกำหนดสำคัญของการทดสอบ routing) · วลี negatives อ้างสกิลพี่น้อง/ข้ามโดเมนตามจริง · ไม่มีชื่อคอลัมน์/ตาราง/SQL/ตัวเลขสมมติในคำถาม
- **v5.19.17**: ใช้ข้อเสนอ P1: ย่อบล็อกกฎใน **27 สกิลลูก** จาก ~21 บรรทัด (8 KB) → 5 บรรทัด (~1.4 KB) โดย **คงกฎที่ใช้งานจริงครบทุกข้อ** (ห้ามเดา · ห้ามเปิดไส้ใน + เกณฑ์จับคำ + footer · หน่วย/ถามกลับ/ค่าจริง · กระทบยอด + ตัวอย่างห้ามใช้ตอบ) แล้วชี้ไปที่ "§1 ของ skill แม่" ซึ่ง include อยู่แล้ว ⇒ ไฟล์แม่ 6 ไฟล์และไฟล์ที่ไม่มี include (5 ไฟล์ office/software) ยังพกฉบับเต็มไว้
- **v5.19.16**: แก้ตามผลรีวิวความซ้ำ: (1) **ฐานสต็อก** — `business-overview` สอนให้ใช้ Stock_Total_* และห้าม Stock_Quantity ซึ่ง **ตรงข้ามกับกฎธุรกิจ** (คงเหลือ = Stock_Quantity) ⇒ แก้ให้ตรง inventory-agent (2) **footer 3 จุดยังพิมพ์ชื่อตาราง** `mcg_aiplatform_sales` (ขัดกฎห้ามเปิดไส้ใน) ⇒ เปลี่ยนเป็น "Sales Out (Postgres)" (3) **schema ปลดระวาง** `gold`/`silver` ในตารางแหล่งข้อมูล ⇒ `ai` (4) บล็อกกฎของ `sales-agent` ถูกตัดขาดกลาง (มีบรรทัดลอยแทรก) ⇒ ต่อกลับเป็นบล็อกเดียว (5) `generate-srs` เพิ่ม `AskUserQuestion` ใน allowed-tools (เดิมกฎสั่งให้เรียกแต่ tool ไม่อยู่ใน allowlist) (6) ตัวอย่าง "หน่วยผิด" ในบล็อกทุกไฟล์ใช้เลขจริง 126,395/31,418 ⇒ เปลี่ยนเป็นเลขสมมติ (7) เติมสถานะล่าสุดของตารางรายวันใน business-overview
- **v5.19.15**: ตามผลรีวิว: (1) คำเตือนเทียบ GP ข้ามฐาน (sales-agent) อ้างคอลัมน์เก่า `Moving_Cost_Amount` และตัวเลขที่ล้าสมัย ⇒ เปลี่ยนเป็นเกณฑ์ 2026-09-28 และห้ามอ้างเลขเทียบข้ามฐานจากความจำ (2) `channel-regional` เลิก hardcode ปี (`2026-07-01`/`2025-07-01`) → ใช้ `{{fy_curr_start}}`/`{{fy_prev_start}}` + แก้ alias ที่ติดป้าย FY ผิด off-by-one
- **v5.19.14**: เพิ่ม tool `sales_out_vs_target_base` — ยอด Sales Out (excl VAT) + ค่าแปลง ×1.07 สำหรับเทียบกับเป้า ทั้งแบบทั้งบริษัทและ OFFLINE · skill แม่ระบุกฎ: เป้าเป็นยอดรวม VAT ⇒ ใช้ค่า `*_comparable_incl_vat` และต้องกำกับว่าแปลง 1.07 · ห้าม join ข้าม platform
- **v5.19.13**: เพิ่ม 2 กฎจากเคสจริงรอบล่าสุด: (1) 🚫 **ห้ามวงเล็บชื่อทางเทคนิคต่อท้ายคำธุรกิจ** — รูปแบบที่หลุดซ้ำ ๆ คือ "รุ่น-สี (ชื่อคอลัมน์)" / "Product Master (ชื่อตาราง)" ⇒ ห้ามวงเล็บคำที่ขึ้นต้น `ai.` หรือ snake_case ต่อท้ายคำธุรกิจ (2) 🧮 **กระทบยอดก่อนส่ง** — ผลรวมของแถวในตารางต้องเท่ากับยอดรวมที่เขียน ถ้าไม่ตรงให้หาสาเหตุ/ระบุขอบเขต/แก้ตัวเลข และห้ามสร้างกลุ่ม "อื่น ๆ" ที่ยอดเกินส่วนที่เหลือ (เคสจริง: ตารางรายแบรนด์บวกได้ 27,141 แต่ยอดที่เขียน 26,541)
- **v5.19.12**: ตัดชื่อคอลัมน์ออกจาก **ประโยคกฎ** 29 บรรทัดใน 14 ไฟล์ (เหลือไว้เฉพาะใน SQL/mapping ที่ต้องใช้เขียน query) เพราะโมเดลลอกคำจากประโยคกฎไปพิมพ์ในคำตอบ · และ `product-agent` สั่งห้ามถามกลับสำหรับ "มีกี่รุ่น"/"จำนวนรุ่น"/"กี่รุ่น" โดยตรง — ให้ตอบจำนวนรุ่น-สีทันที ถ้าจะถามให้ถามเรื่องขอบเขต (ทั้งระบบ vs กรองแบรนด์/หมวด) แทน
- **v5.19.11**: แก้ root cause ของการเปิดไส้ใน: **template footer ในไฟล์เองมีคำต้องห้าม** — ลบ "(Synapse)" ออกจาก footer ทุกจุด (12 จุดใน 5 ปลั๊กอิน) เพราะโมเดลลอกตาม template ของไฟล์ · และย้ายกฎ 🙈 ห้ามพิมพ์ชื่อตาราง/คอลัมน์/tool/SQL ขึ้นเป็น **ข้อแรกสุดของบล็อกกฎ** ในทุก skill (จากเดิมอยู่ข้อ 6) ให้ความสำคัญสูงสุด
- **v5.19.10**: เพิ่มการตีความตามที่ผู้ใช้เลือก: **ถามกลับเฉพาะเมื่อกำกวมจริง** — "มีกี่รุ่น"/"จำนวนรุ่น" (ระบุหน่วยแล้ว) ตอบเป็นรุ่น-สีได้เลย · ที่ต้องถามคือ "จำนวน/กี่/เท่าไหร่" ที่ไม่ระบุหน่วย หรือคำถามที่ขาดช่วงเวลา/มิติที่จำเป็น — ระบุตัวอย่างทั้งสองฝั่งไว้ในบล็อกกฎทุก skill
- **v5.19.9**: ประกาศ **`AskUserQuestion`** ใน frontmatter `tools:` ของทุก skill ที่มีรายการ tools อยู่แล้ว (34 ไฟล์) ตามที่ผู้ใช้เลือก — เพื่อให้เรียก tool ได้แน่นอนเมื่อต้องถามกลับ · ไฟล์ที่ไม่มี `tools:` (artifact-creator, email-digest, email-template, generate-srs) ไม่เติม key ใหม่ เพราะการสร้าง allowlist ขึ้นมาอาจตัด tool MCP อื่นของสกิลนั้น · แก้ frontmatter ที่พังจริง 2 ไฟล์: `sales-agent` (บรรทัด note หลุดเข้าไปใน description block จน YAML พัง — ย้ายไปไว้ในเนื้อไฟล์) และ `ms-excel` (description เป็นบรรทัดเดียวมี ": " ทำให้ YAML ไม่ผ่าน — เปลี่ยนเป็น folded block) ⇒ ตอนนี้ frontmatter ทั้ง 38 ไฟล์ parse ผ่านหมด
- **v5.19.8**: เปลี่ยนกฎ "ห้ามเปิดเผยภายใน" จากรายชื่อคำ (ซึ่งโมเดลลอกคำจากไฟล์มาพิมพ์เอง) เป็น **เกณฑ์จับคำ** — ห้ามคำที่ขึ้นต้น `ai.` · ลงท้าย `_synapse`/`_count`/`_key`/`_model`/`_color`/`_quantity` · ชื่อฟังก์ชัน SQL · snake_case · ชื่อ tool พร้อมเตือนให้ตรวจซ้ำก่อนส่ง (รวม Insight + footer) · เพิ่ม check นี้เข้า Final Validation ของทุกไฟล์แม่ (product/inventory/sales/crm/target + business-overview §7)
- **v5.19.7**: เพิ่มกฎ 🔢 **หน่วยต้องตรงประเภท** (SKU ≠ ชิ้น · รุ่น-สี ≠ ชิ้น — ห้ามเขียน "SKU 126,395 ชิ้น") และ **ตัวเลขที่นับได้ต้องเป็นค่าจริง (COUNT(DISTINCT)) ไม่ใช่ค่าประมาณ (APPROX_)** เพราะพบเคสจริงที่ตอบ 32,147 (ค่าประมาณ) ขณะที่ค่าจริงคือ 31,418 = คลาด 2.3% และคำตอบเดียวกันให้เลขไม่ตรงกันคนละรอบ · `product-agent` เพิ่มกฎสัดส่วน: ต้องใช้เศษและส่วนขอบเขตเดียวกัน (เคสจริง "MC = 53.8% ของทั้งหมด" มาจาก 17,291÷32,147 คนละขอบเขต ที่ถูกคือ 65% ในบรรดาที่ระบุแบรนด์)
- **v5.19.6**: เพิ่ม **รายการคำต้องห้าม** ในบล็อกกฎทุก skill — ห้ามปรากฏในคำตอบที่ผู้ใช้เห็นเด็ดขาด: `ai.dim_article` · `ai.fact_*` · `Article_Key` · `Article_Model` · `Article_Model_Color` · `item_code` · `model_color` · `sku_count` · `model_color_count` · ชื่อ tool/MCP · SQL พร้อมคำธุรกิจที่ให้ใช้แทน (จำนวน SKU / จำนวนรุ่น (รุ่น-สี) / จำนวนชิ้น · "ข้อมูลสินค้าในระบบ" · footer = แหล่งกว้าง + as-of) — เพราะ agent ยังพิมพ์ชื่อคอลัมน์ในตารางคำตอบแม้มีกฎห้ามแล้ว
- **v5.19.5**: เพิ่มบรรทัดบังคับในบล็อกกฎทุก skill: 🚫 ห้ามพิมพ์ชื่อตาราง/คอลัมน์/tool/SQL ในคำตอบที่ผู้ใช้เห็น **รวมทั้งกล่อง Insight และ Data Footer** · แก้ความขัดแย้ง "มีกี่รุ่น": คำว่า "รุ่น" = หน่วยที่ระบุแล้ว ⇒ ตอบเป็นรุ่น-สีได้เลย ไม่ต้องถามกลับ (ฝั่ง sales/pricing แก้ให้ตรงกับ product/inventory) · `stock-health` เพิ่มวลีนำทางจำนวน ("สต็อกมีกี่รุ่น-สี") · `assortment-summary` เตือนว่า "รวม" ของตาราง ≠ ยอดทั้ง master
- **v5.19.4**: เวลาถามกลับ/ยืนยันกับผู้ใช้ ให้เรียก tool **`AskUserQuestion`** เสมอ (ตัวเลือก 2–4 ข้อที่เลือกได้จริง · header สั้น + คำถามชัด) — 🚫 ห้ามพิมพ์คำถามลอย ๆ ในคำตอบ · ทั้ง 38 skill มีข้อกำหนดนี้ในบล็อกกฎ และไฟล์แม่ของแต่ละปลั๊กอินมีสเปกวิธีเรียก · ตัวอย่าง "ถาม: ..." ในไฟล์ = เนื้อหาที่ใส่ใน tool call
- **v5.19.3**: แก้ตามผลตรวจ: ถามกลับแบบ 3 ตัวเลือก (SKU / รุ่น (รุ่น-สี) / ชิ้น) แทนการแยก «รุ่น» ออกมา · ติดหน่วย Tickets (ใบเสร็จ) และตาราง Member (฿/ใบ/ชิ้น) · `total_quantity` = จำนวนชิ้น · `pricing-promotion` ให้ถามกลับก่อนค่อยรัน SQL · `category-hierarchy` นับ SKU/รุ่น-สี เฉพาะช่วง FY ปัจจุบัน (FILTER) ให้ตรงหัวตาราง · ระบุกฎตอบ "รับของเข้า" เป็นจำนวนชิ้นในไฟล์แม่
- **v5.19.2**: ย้ำกฎ **ห้ามเดาข้อมูลมาตอบ** (ใช้กับทุก runtime โดยเฉพาะ Claude Desktop / Cowork) ใน **ทุก skill** ของปลั๊กอิน — ทุกตัวเลข/ข้อเท็จจริงต้องมาจากผลการเรียก tool จริงในบทสนทนาและอ้างอิงกลับได้ · เรียกแล้วไม่พบข้อมูลให้ตอบว่า "ไม่พบข้อมูล" ตามจริง (แยกจาก 0) · ห้ามเดา/ประมาณ/แต่งตัวเลข/ตอบจากความจำของโมเดล
- **v5.19.1**: กฎการนับจำนวน — "จำนวนรุ่น" = **รุ่น-สี** (ไม่ใช่รุ่น ไม่ใช่ SKU) · "จำนวน/กี่" ที่ไม่ระบุหน่วยต้อง **ถามกลับ** (SKU / รุ่น-สี / ชิ้น) · ทุกคำตอบที่เป็นจำนวนต้องระบุหน่วย — วางกฎที่ `sales-agent` (ไฟล์แม่) และปรับหน่วย/ตารางในสกิลลูก

## Answer Term Guard

ตัวตรวจคำต้องห้ามในคำตอบ — แทนการให้โมเดลตรวจตัวเอง (ซึ่งหลุดซ้ำ 2 ครั้งในวันที่ 2026-10-05)

```bash
python answer-guard/check_answer_terms.py draft.md   # หรือ cat draft.md | python answer-guard/check_answer_terms.py
python -m unittest discover -s answer-guard/tests -v # 16 เคส
```

- ตรวจตาม**เกณฑ์จับคำ 6 ข้อ**เดียวกับบล็อกกฎ §1: ขึ้นต้น `ai.` · ลงท้าย `_synapse`/`_count`/`_key`/`_model`/`_color`/`_quantity` · ชื่อฟังก์ชัน SQL · snake_case/Pascal_Snake · ชื่อ tool/MCP · ชื่อระบบ
- เคสทดสอบเป็น**ข้อความจริงที่หลุดถึงผู้ใช้** (ชื่อคอลัมน์ในกล่อง Insight, ชื่อตารางใน footer) + ข้อความธุรกิจที่ต้องผ่าน (ไทย · ฿ · หน่วย) ⇒ กันทั้งการพลาดและการจับผิด
- บรรทัดที่ขึ้นต้นด้วย 🔒 (ตารางสูตร) ได้รับยกเว้น

**ติดตั้งเป็น Stop hook แล้ว — แต่ยังไม่ยืนยันว่ายิงจริงใน Cowork ของเรา** — `hooks/hooks.json` เรียก `hooks-handlers/run-check.sh` ซึ่งเลือก interpreter เอง (`ANSWER_GUARD_PYTHON` → `py -3` → `python3` → `python`) แล้วส่งต่อให้ `hooks-handlers/check_answer_terms_stop.py`

- ✅ สเปกปลั๊กอินของ Cowork ระบุ `hooks/hooks.json` · event `Stop` = "When Claude finishes a response" · command hook คืน `{"decision":"block","reason":"..."}` ตรงกับ payload ที่ handler ส่งอยู่แล้ว
- 🚫 **hook โหลดเฉพาะปลั๊กอินที่มาทาง marketplace/plugin route** — ตรวจในเครื่องนี้ (2026-10-05): ปลั๊กอินที่ materialize ใต้ `rpm\plugin_*` (CockroachDB, Figma, Zoom …) มี hook ครบและเคยยิงจริง (`PostToolUse` ×7 · `UserPromptSubmit` ×2) แต่ **ไม่มีปลั๊กอิน mcg ตัวใดอยู่ใต้ `rpm\`** และ manifest ของเส้นทาง Skills panel (`skills-plugin\...\manifest.json`) ก็ไม่มี mcg ⇒ ถ้า skill ไปถึง Desktop ทาง Skills panel อย่างเดียว `hooks\hooks.json` จะ **ไม่ถูกโหลด**
- 🔍 **วิธีพิสูจน์ (ground truth เร็วกว่าเอกสาร)** — เปิด session ที่ปลั๊กอินติดตั้งแล้ว ถามคำถามที่ล่อให้พิมพ์ชื่อคอลัมน์ แล้วนับ event ใน transcript: `grep -rho '"hookEvent":"[A-Za-z]*"' "$APPDATA/Claude/local-agent-mode-sessions" --include=*.jsonl | sort | uniq -c` · ไม่เห็น `Stop` = hook ไม่ยิง
- ⚠️ **กับดัก path บน Windows** — transcript ในเครื่องนี้เคยบันทึก hook ที่ล้มเหลวเพราะพาธเพี้ยนเป็น `C:\c\Users\...` (`${CLAUDE_PLUGIN_ROOT}` ถูกแทนที่ถูก แต่พาธต่อท้ายเพี้ยน) ถ้าเจออาการนี้ ให้เลิกเรียกผ่าน `bash` แล้วเรียก interpreter ตรง ๆ ใน `command`
- ⚠️ **Cowork ใช้ hooks.json แบบ flat** (event อยู่ระดับบนสุด) ต่างจากปลั๊กอินของ Anthropic ในรีโปนี้ (`explanatory-output-style`) ที่ห่อด้วย key `hooks` — ที่นี่ใช้แบบ flat ตามสเปก Cowork ถ้าฝั่ง Claude Code ไม่ยิง hook ให้สลับไปแบบห่อ
- ✅ **กัน loop** — ถ้า payload มี `stop_hook_active` จะปล่อยผ่านทันที ⇒ false positive ไม่วน block ซ้ำ
- ✅ **fail open ทุกทาง** — อ่าน transcript ไม่ได้ · ไม่มี interpreter · hook ไม่ทันใน 20 วินาที ⇒ ปล่อยคำตอบผ่าน ไม่ค้างงานผู้ใช้
- ⚠️ เลือก `py -3` ก่อน `python` เพราะบน Windows `python`/`python3` มักเป็น alias ของ Microsoft Store (บนเครื่องนี้ทั้งคู่เป็น stub ที่อาจค้าง) · ตั้ง `ANSWER_GUARD_PYTHON` เพื่อล็อก interpreter เช่นตัวที่แถมมาใต้ `C:\ProgramData\McGroup\Claude\mcp\python3-standalone`
- ⚠️ handler อ่าน transcript รูปแบบ `{"type":"assistant","message":{...}}` ต่อบรรทัด — ถ้าเปลี่ยนรูปแบบจะ fail open (ไม่บล็อก) ไม่ใช่บล็อกผิด
- 🚫 ปิดได้โดยลบ `hooks/hooks.json`

### Changelog
- **v3.0.0**: Migrated to PostgreSQL + pgvector. New tools: `sales_agent`, `pg_describe_table`, `pg_list_tables`. SQL syntax updated to PostgreSQL. Added `FY_Year` column support. SQM threshold ≥50.
- **v2.2.5**: MSSQL version (deprecated)

## Skills

| Skill | Role | หน้าที่ |
|-------|------|---------|
| `sales-agent` | MC Group Sales Agent | กฎ สูตร KPI และ SQL rules หลัก (shared foundation) |
| `sales-dashboard` | Data Analyst | สรุปภาพรวม Sales Performance FY28 vs FY27 แยก Channel |
| `sales-sqm` | Retail Operations Expert | วิเคราะห์ Sales per Sqm. แยกสาขา/จังหวัด Top 5 / Bottom 5 |
| `discount-margin` | Financial & Planning Analyst | วิเคราะห์ Discount% vs Margin% แยก Category/Product |
| `member-analysis` | CRM & Sales Strategy Analyst | สัดส่วน Member vs Non-Member, ATV, UPT |
| `channel-regional` | Supply Chain & Retail Planner | สัดส่วนยอดขายแยก Regional x Channel + Stock Allocation |
| `abc-analysis` | Inventory & Merchandising Analyst | ABC Analysis + Hero/Slow-moving Articles |

## Architecture

```
skills/
├── sales-agent/         ← SKILL.md หลัก (rules, SQL, KPIs, thresholds)
├── sales-dashboard/     ← #[[file:../sales-agent/SKILL.md]] + role prompt
├── sales-sqm/           ← #[[file:../sales-agent/SKILL.md]] + role prompt
├── discount-margin/     ← #[[file:../sales-agent/SKILL.md]] + role prompt
├── member-analysis/     ← #[[file:../sales-agent/SKILL.md]] + role prompt
├── channel-regional/    ← #[[file:../sales-agent/SKILL.md]] + role prompt
└── abc-analysis/        ← #[[file:../sales-agent/SKILL.md]] + role prompt
```

แต่ละ skill ย่อย include กฎหลักผ่าน `#[[file:...]]` — ไม่ซ้ำซ้อน แก้ที่เดียวมีผลทุก role.

## MCP Tools (PostgreSQL)

| Tool | Description |
|------|-------------|
| `sales_agent` | Execute PostgreSQL SELECT queries |
| `pg_describe_table` | Get table schema |
| `pg_list_tables` | List approved tables |

## Database

- **Engine**: PostgreSQL 16 (Azure Flexible Server)
- **Table**: `mcg_aiplatform_sales` (~13M rows, 20GB)
- **Features**: pgvector extension enabled
- **Connection**: Via MCP Toolbox v1.8.0

## Usage

พิมพ์คำถามตรงๆ:
- "สรุปภาพรวมยอดขาย" → triggers `sales-dashboard`
- "Sales per sqm สาขาไหนดีสุด" → triggers `sales-sqm`
- "Category ไหน discount สูงเกินไป" → triggers `discount-margin`
- "สัดส่วน Member เป็นเท่าไหร่" → triggers `member-analysis`
- "ยอดขายแยกตามภาค" → triggers `channel-regional`
- "สินค้าขายดี/สต็อกจม" → triggers `abc-analysis`
