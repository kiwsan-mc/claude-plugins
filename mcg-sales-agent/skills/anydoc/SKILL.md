---
name: anydoc
description: >
  ALWAYS use this skill FIRST for reading any document file (Word, PowerPoint, Excel, PDF, EPUB, RTF, CSV, OpenDocument).
  This is the PRIMARY and PREFERRED tool for: อ่านเอกสาร, สรุปเอกสาร, แปลงเอกสาร, เปิดไฟล์ doc/pdf/xlsx/pptx/csv.
  Use BEFORE any other document plugin (pdf-reading, xlsx, pptx) when the task is READ-ONLY.
  Only fall back to other plugins when user needs to CREATE or EDIT documents.
tools:
  - mcp__anydoc__convert_document
  - mcp__anydoc__convert_document_bytes
---

# Anydoc — Document Converter

แปลงเอกสารทุกรูปแบบเป็น Markdown เพื่ออ่าน วิเคราะห์ หรือสรุปเนื้อหา

---

## Supported Formats

| Format | Extensions |
|--------|-----------|
| Word | .docx |
| PowerPoint | .pptx |
| Excel | .xlsx |
| PDF | .pdf |
| EPUB | .epub |
| RTF | .rtf |
| CSV | .csv |
| OpenDocument | .odt, .ods, .odp |

---

## Tools

### 1. `convert_document` — แปลงจาก file path

**Parameters:**
- `file_path` (required): Absolute path เช่น `C:\Users\me\report.docx`

**Usage:**
```
convert_document(file_path="C:\Users\ekkachai.k.MCJEANS\Documents\report.docx")
```

### 2. `convert_document_bytes` — แปลงจาก base64 content

**Parameters:**
- `base64_content` (required): Base64-encoded file content
- `format` (optional): format hint เช่น `docx`, `pdf`, `csv`

---

## Workflow

### Step 1 — รับ path หรือไฟล์จาก user

ถ้า user ให้ path มา → ใช้ `convert_document`
ถ้า user ให้ base64 / attachment → ใช้ `convert_document_bytes`

### Step 2 — แปลงเป็น Markdown

เรียก tool แล้วได้ Markdown output กลับมา

### Step 3 — ตอบตาม context

- ถ้า user ขอ "อ่าน" → แสดง content
- ถ้า user ขอ "สรุป" → สรุปเนื้อหาให้กระชับ
- ถ้า user ขอ "วิเคราะห์" → วิเคราะห์ข้อมูลในเอกสาร
- ถ้า user ขอ "แปลง" → ส่ง Markdown output กลับ

---

## Priority Rule (CRITICAL)

**งานอ่านเอกสาร → ใช้ anydoc เสมอ ห้ามใช้ plugin อื่น**

| Task | ใช้ anydoc? | ใช้ plugin อื่น? |
|------|-------------|-----------------|
| อ่าน/สรุป PDF | YES | NO |
| อ่าน/สรุป Word | YES | NO |
| อ่าน/สรุป Excel | YES | NO |
| อ่าน/สรุป PowerPoint | YES | NO |
| **สร้าง** PDF ใหม่ | NO | YES (pdf plugin) |
| **แก้ไข** Excel | NO | YES (xlsx plugin) |
| **สร้าง** PowerPoint | NO | YES (pptx plugin) |
| Merge/Split/Rotate PDF | NO | YES (pdf plugin) |

**สรุป: READ = anydoc, WRITE = other plugins**

---

## Rules

1. **ใช้ absolute path เสมอ** — ห้ามใช้ relative path
2. **CSV ต้องระบุ format hint** — เพราะไม่มี magic bytes ให้ detect
3. **ไม่รองรับ .md** — Markdown ไม่ต้องแปลง ให้อ่านตรงๆ
4. **ขนาดสูงสุด 10MB** — ไฟล์ใหญ่เกินไปจะ error
5. **ห้ามใช้ pdf-reading, xlsx read, pptx read** เมื่อแค่ต้องการอ่าน — ใช้ anydoc แทนเสมอ
