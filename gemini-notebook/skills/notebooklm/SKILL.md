---
name: notebooklm
description: Guide for using gemini-notebook-mcp (Gemini Notebook / NotebookLM) tools effectively. Use when user wants to interact with Gemini Notebook — create notebooks, add sources, generate audio/video, query notebooks, manage sharing, or troubleshoot authentication.
tools: Bash, Read, Write
---

# Gemini Notebook MCP Guide

คู่มือการใช้งาน gemini-notebook-mcp-cli ผ่าน Claude Code สำหรับจัดการ Gemini Notebook (เดิมชื่อ Google NotebookLM)

## สิ่งสำคัญที่ต้องรู้

### Authentication

- **ต้อง login ก่อนใช้งาน**: รัน `nlm login` เพื่อดึง cookie จาก browser
- **Cookie หมดอายุทุก 2-4 สัปดาห์**: ต้อง login ใหม่เมื่อได้ error เกี่ยวกับ auth
- **ตรวจสอบสถานะ**: ใช้ `nlm login --check`
- **หลายบัญชี**: ใช้ `nlm login --profile work` / `nlm login --profile personal`
- **Auto-refresh**: Server จะ refresh token อัตโนมัติเมื่อหมดอายุ แต่ถ้า Google session หมดจริงต้อง login ใหม่

### Context Window Management

- MCP นี้มี **43 tools** ทั้งหมด — กิน context window มาก
- **ปิดเมื่อไม่ใช้**: ใน Claude Code ใช้ `@gemini-notebook-mcp` เพื่อ toggle on/off
- **เปิดเฉพาะเมื่อต้องการใช้** Gemini Notebook จริงๆ

### Troubleshooting

- ใช้ `nlm doctor` เพื่อตรวจสอบปัญหาการติดตั้งและ authentication
- ใช้ `nlm doctor auth-replay` ถ้าสงสัยปัญหา browser-bound auth

---

## MCP Tools — แบ่งตามหมวดหมู่

### 1. Notebook Management (จัดการ Notebook)

| Tool | ใช้ทำอะไร |
|------|----------|
| `notebook_list` | แสดงรายการ notebook ทั้งหมด |
| `notebook_create` | สร้าง notebook ใหม่ |
| `notebook_query` | ถาม AI เกี่ยวกับเนื้อหาใน notebook (คำถามจะบันทึกใน web UI ด้วย) |
| `notebook_share_public` | เปิด/ปิด public link |
| `notebook_share_invite` | เชิญคนเข้าดู/แก้ไข notebook |

### 2. Source Management (จัดการแหล่งข้อมูล)

| Tool | ใช้ทำอะไร |
|------|----------|
| `source_add` | เพิ่มแหล่งข้อมูล (URL, text, Google Drive, file) |
| `source_sync_drive` | Sync แหล่งข้อมูลจาก Drive ที่อัปเดตแล้ว |

### 3. Studio Content (สร้างเนื้อหา)

| Tool | ใช้ทำอะไร |
|------|----------|
| `studio_create` | สร้าง Audio podcast, Video, Briefing doc, Flashcards, Infographic, Mind map, Slide deck |
| `studio_revise` | แก้ไข/ปรับปรุง slide deck |
| `download_artifact` | ดาวน์โหลดไฟล์ที่สร้างเสร็จแล้ว |
| `download_all_artifacts` | ดาวน์โหลดทุกไฟล์จาก notebook |

### 4. Chat & Query (สนทนากับ Notebook)

| Tool | ใช้ทำอะไร |
|------|----------|
| `chat_list` | แสดงรายการ chat sessions |
| `chat_get` | ดูเนื้อหา chat session |
| `chat_export` | Export chat ออกมา |
| `cross_notebook_query` | ถามข้าม notebook หลายอัน |

### 5. Research (วิจัย)

| Tool | ใช้ทำอะไร |
|------|----------|
| `research_start` | เริ่มค้นคว้า web/Drive แล้วนำผลเข้า notebook |

### 6. Batch & Pipeline (ทำงานเป็นชุด)

| Tool | ใช้ทำอะไร |
|------|----------|
| `batch` | ทำหลายงานพร้อมกัน (query, create, delete) |
| `pipeline` | รัน multi-step workflow |

### 7. Tagging & Organization

| Tool | ใช้ทำอะไร |
|------|----------|
| `tag` | ติด tag ให้ notebook เพื่อจัดกลุ่ม/เลือกใช้งาน |

---

## Workflow ที่แนะนำ

### สร้าง Notebook + Podcast จาก URLs

```
1. notebook_create — สร้าง notebook ใหม่
2. source_add — เพิ่ม URLs เป็นแหล่งข้อมูล
3. studio_create — สร้าง audio podcast (deep dive format)
4. รอสักครู่แล้ว download_artifact — ดาวน์โหลดไฟล์เสียง
```

### วิจัยหัวข้อใหม่

```
1. notebook_create — สร้าง notebook สำหรับหัวข้อ
2. research_start — ค้นคว้า web อัตโนมัติ
3. notebook_query — ถามสรุปจากผลวิจัย
```

### สร้าง Slide Deck

```
1. notebook_create — สร้าง notebook
2. source_add — เพิ่มเนื้อหา
3. studio_create — สร้าง slide deck
4. studio_revise — ปรับปรุง slides ตามต้องการ
5. download_artifact — ดาวน์โหลด
```

---

## CLI Commands ที่มีประโยชน์

```bash
# ตรวจสอบสถานะ
nlm login --check          # เช็ค auth status
nlm doctor                 # วินิจฉัยปัญหาทั้งหมด

# จัดการ authentication
nlm login                  # login ใหม่ (เปิด browser)
nlm login --profile work   # login แยกบัญชี

# ดู notebooks
nlm notebook list

# สร้าง audio podcast
nlm audio create <notebook-id> --confirm

# ดาวน์โหลดทุกอย่าง
nlm download all <notebook-id> -d ./exports
```

---

## ข้อจำกัดที่ควรทราบ

- **Rate limit**: Free tier มีประมาณ 50 queries/วัน
- **ไม่มี official API**: ใช้ internal API ที่อาจเปลี่ยนแปลงได้
- **Cookie expiration**: ต้อง re-login ทุก 2-4 สัปดาห์
- **Studio content generation**: ใช้เวลาสร้าง ต้อง poll status ก่อน download

---

## เมื่อเจอ Error

| อาการ | วิธีแก้ |
|-------|---------|
| Auth error / 401 | รัน `nlm login` ใหม่ |
| Token expired | Server จะ auto-refresh แต่ถ้าไม่ได้ให้ `nlm login` |
| Tool ใช้ไม่ได้ | ตรวจสอบด้วย `nlm doctor` |
| Rate limited | รอสักพัก หรืออัปเกรดเป็น Pro |
| Download ไม่ได้ | ตรวจสอบว่า content สร้างเสร็จแล้วด้วย status check |
