---
name: notebooklm
description: Guide for using notebooklm-mcp-server (moodRobotics) to interact with Google NotebookLM. Use when user wants to ask questions, add sources, generate audio/studio content, manage notebooks, or run research.
tools: Bash, Read, Write
---

# NotebookLM MCP Server Guide

คู่มือการใช้งาน notebooklm-mcp-server (moodRobotics) สำหรับจัดการ Google NotebookLM ผ่าน MCP

GitHub: https://github.com/moodRobotics/notebooklm-mcp-server

## ข้อดีหลัก

- **Auth ง่าย**: เปิด Chromium → login Google → save cookies อัตโนมัติ
- **ไม่ต้องปิด browser ปกติ** — ใช้ Playwright Chromium แยก
- **TypeScript native** — เร็ว ไม่ต้อง Python
- **Auto-update** — ตรวจ version ใหม่อัตโนมัติ
- **18 tools** ครอบคลุม: notebooks, sources, query, research, studio

---

## Portable Paths

```
Node.js : C:\ProgramData\McGroup\Claude\mcp\node-portable\node-v22.16.0-win-x64\node.exe
npx     : C:\ProgramData\McGroup\Claude\mcp\node-portable\node-v22.16.0-win-x64\npx.cmd
```

---

## MCP Config

### Claude Desktop — `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "C:\\ProgramData\\McGroup\\Claude\\mcp\\node-portable\\node-v22.16.0-win-x64\\npx.cmd",
      "args": ["-y", "notebooklm-mcp-server", "start"]
    }
  }
}
```

### Kiro — `.kiro/settings/mcp.json`

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "C:\\ProgramData\\McGroup\\Claude\\mcp\\node-portable\\node-v22.16.0-win-x64\\npx.cmd",
      "args": ["-y", "notebooklm-mcp-server", "start"],
      "disabled": false
    }
  }
}
```

### Claude Code — `~/.claude.json` หรือ `.mcp.json`

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "C:\\ProgramData\\McGroup\\Claude\\mcp\\node-portable\\node-v22.16.0-win-x64\\npx.cmd",
      "args": ["-y", "notebooklm-mcp-server", "start"]
    }
  }
}
```

---

## Authentication

### Login ครั้งแรก

```powershell
& "C:\ProgramData\McGroup\Claude\mcp\node-portable\node-v22.16.0-win-x64\npx.cmd" -y notebooklm-mcp-server auth
```

1. Chromium จะเปิดขึ้นมา (ใช้ Playwright — ไม่ใช่ Chrome ปกติของ user)
2. Login Google account
3. รอจน detect สำเร็จ → cookies ถูก save ที่ `~/.notebooklm-mcp/auth.json`
4. Browser ปิดเอง → ใช้งานได้เลย

### Refresh Auth (session หมดอายุ)

ถ้า tools เริ่ม fail ให้เรียก tool `refresh_auth` หรือรัน:

```powershell
& "C:\ProgramData\McGroup\Claude\mcp\node-portable\node-v22.16.0-win-x64\npx.cmd" -y notebooklm-mcp-server auth
```

> **ข้อดี**: ไม่ต้องปิด Chrome/Edge ของ user เพราะใช้ Chromium ของ Playwright แยกต่างหาก

### Session Storage

- Windows: `C:\Users\<user>\.notebooklm-mcp\auth.json`
- Session ใช้ได้ ~2-4 สัปดาห์

---

## MCP Tools (18 tools)

### 1. Notebook Management

| Tool | ใช้ทำอะไร |
|------|----------|
| `notebook_list` | แสดงรายการ notebook ทั้งหมด |
| `notebook_create` | สร้าง notebook ใหม่ |
| `notebook_rename` | เปลี่ยนชื่อ notebook |
| `notebook_delete` | ลบ notebook (ระวัง: ลบถาวร) |

### 2. Source Management

| Tool | ใช้ทำอะไร |
|------|----------|
| `notebook_add_url` | เพิ่ม website/YouTube URL เป็น source |
| `notebook_add_text` | เพิ่ม text เป็น source |
| `notebook_add_local_file` | อัพโหลดไฟล์ PDF/Markdown/Text |
| `notebook_add_drive` | เพิ่มไฟล์จาก Google Drive |
| `source_delete` | ลบ source ออกจาก notebook |
| `source_sync` | Sync Drive source ให้เป็นเวอร์ชันล่าสุด |

### 3. Research & Query

| Tool | ใช้ทำอะไร |
|------|----------|
| `notebook_query` | ถามคำถาม notebook (grounded answer) |
| `research_start` | เริ่ม web/drive research task |
| `research_poll` | ตรวจสอบสถานะ research |
| `research_import` | นำเข้าผล research เป็น sources |

### 4. Studio & Generation

| Tool | ใช้ทำอะไร |
|------|----------|
| `audio_overview_create` | สร้าง Audio Overview (podcast) |
| `studio_poll` | ตรวจสถานะ audio/video ที่กำลังสร้าง |
| `mind_map_generate` | สร้าง Mind Map JSON |

### 5. System

| Tool | ใช้ทำอะไร |
|------|----------|
| `refresh_auth` | เปิด browser เพื่อ renew Google session |

---

## Workflow ที่แนะนำ

### ถามคำถามจาก Notebook

```
1. notebook_list — ดู notebooks ทั้งหมด
2. notebook_query — ถามคำถาม (ใส่ notebook_id + question)
```

### สร้าง Notebook + เพิ่ม Sources

```
1. notebook_create — สร้าง notebook ใหม่
2. notebook_add_url — เพิ่ม URLs
3. notebook_add_text — เพิ่ม text content
4. notebook_query — ถามคำถามจาก sources
```

### Research อัตโนมัติ

```
1. notebook_create — สร้าง notebook
2. research_start — เริ่มค้นคว้า web
3. research_poll — รอผล
4. research_import — นำเข้าเป็น sources
5. notebook_query — ถามจากผลวิจัย
```

### สร้าง Audio Podcast

```
1. เลือก notebook ที่มี sources พร้อม
2. audio_overview_create — สร้าง podcast
3. studio_poll — รอจนเสร็จ
4. ดาวน์โหลดจาก NotebookLM web UI
```

### Auth หมดอายุ

```
User: "tools ใช้ไม่ได้ / auth error"
→ เรียก refresh_auth → browser เปิดให้ login ใหม่
```

---

## เมื่อเจอ Error

| อาการ | วิธีแก้ |
|-------|---------|
| Auth error / session expired | เรียก `refresh_auth` หรือรัน `npx -y notebooklm-mcp-server auth` |
| Server ไม่เริ่ม | ตรวจสอบว่า Node.js >= 18 |
| Rate limited | Free tier ~50 queries/วัน — รอหรืออัปเกรด |
| Playwright ติดตั้งไม่ได้ | ตรวจสอบ internet connection, ลอง `npx -y notebooklm-mcp-server auth` อีกครั้ง |

---

## ข้อจำกัดที่ควรทราบ

- **ไม่มี official API**: ใช้ internal API ของ NotebookLM
- **Rate limit**: Free tier ~50 queries/วัน
- **Session ~2-4 สัปดาห์**: หลังนั้นต้อง refresh auth
- **Playwright Chromium**: ครั้งแรกต้องดาวน์โหลด Chromium (~200MB)
- **Auto-update**: Server ตรวจ version ทุกครั้งที่เริ่ม

---

## เทียบกับ MCP อื่น

| | moodRobotics (ตัวนี้) | notebooklm-connector | PleasePrompto | notebooklm-mcp-cli |
|---|---|---|---|---|
| Auth | Playwright Chromium แยก ✅ | อ่าน cookies (Windows ใช้ไม่ได้) | Chrome profile แยก (ต้องปิด Chrome) | CDP browser profile |
| Runtime | Node.js (npx) | Python 3.12 (uvx) | Node.js (npx) | Python (uvx) |
| Tools | 18 | 13 | ~20 | 43 |
| ต้องปิด Chrome | ❌ | ✅ (Windows) | ✅ | ❌ |
| Windows support | ✅ ดี | ❌ cookie decrypt fail | มีปัญหา | ✅ |
| Auto-update | ✅ | ❌ | ❌ | ❌ |
