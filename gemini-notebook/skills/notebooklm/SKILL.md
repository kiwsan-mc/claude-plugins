---
name: notebooklm
description: Guide for using notebooklm-mcp (PleasePrompto) tools effectively. Use when user wants to interact with NotebookLM — ask questions, add sources, generate audio, manage notebook library, or troubleshoot authentication.
tools: Bash, Read, Write
---

# NotebookLM MCP Guide

คู่มือการใช้งาน notebooklm-mcp (PleasePrompto/notebooklm-mcp) สำหรับจัดการ Google NotebookLM ผ่าน MCP

GitHub: https://github.com/PleasePrompto/notebooklm-mcp

## Path ของ CLI (Portable Node.js)

ใช้ Node.js portable ที่ shared path:

```
C:\ProgramData\McGroup\Claude\mcp\node-portable\node-v22.16.0-win-x64\npx.cmd
```

รันตรง:

```powershell
& "C:\ProgramData\McGroup\Claude\mcp\node-portable\node-v22.16.0-win-x64\npx.cmd" notebooklm-mcp@latest
```

---

## MCP Config (Kiro / Claude Code)

### Kiro — `.kiro/settings/mcp.json`

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "C:\\ProgramData\\McGroup\\Claude\\mcp\\node-portable\\node-v22.16.0-win-x64\\npx.cmd",
      "args": ["notebooklm-mcp@latest"],
      "env": {
        "HEADLESS": "true",
        "NOTEBOOKLM_PROFILE": "standard"
      },
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
      "args": ["notebooklm-mcp@latest"],
      "env": {
        "HEADLESS": "true",
        "NOTEBOOKLM_PROFILE": "standard"
      }
    }
  }
}
```

---

## สิ่งสำคัญที่ต้องรู้

### Authentication

- **ต้อง login ก่อนใช้งาน**: เรียก tool `setup_auth` (show_browser=true) เพื่อเปิด Chrome แล้ว login Google
- **Chrome profile ถูกบันทึกไว้** ที่ `%APPDATA%\notebooklm-mcp\chrome_profile\` — login ครั้งเดียวใช้ได้ตลอด
- **ตรวจสอบสถานะ**: เรียก tool `get_health` → ดู `authenticated: true/false`
- **เปลี่ยนบัญชี**: เรียก tool `re_auth` เพื่อ wipe auth แล้ว login ใหม่
- **Multi-account**: ตั้ง env `NOTEBOOKLM_ACCOUNT=work` หรือ `personal` แยก Chrome profile ได้

> **ข้อจำกัด**: `setup_auth` ต้องเปิด Chrome บนเครื่อง user โดยตรง (ไม่ทำผ่าน headless ได้)
> ถ้าเจอ auth error ให้แนะนำ user:
> 1. เปิด PowerShell
> 2. รัน: `& "C:\ProgramData\McGroup\Claude\mcp\node-portable\node-v22.16.0-win-x64\npx.cmd" notebooklm-mcp@latest`
> 3. จากนั้นเรียก `setup_auth` tool อีกครั้ง หรือรัน login ผ่าน HTTP transport

### Tool Profiles

Server มี 3 profile ลดจำนวน tools ที่โหลดเข้า context:

| Profile | Tools |
|---------|-------|
| `minimal` | ask_question, get_health, list_notebooks, select_notebook, get_notebook |
| `standard` | minimal + setup_auth, list_sessions, add_notebook, update_notebook, search_notebooks |
| `full` | ทุก tool (default) |

ตั้งค่าผ่าน env `NOTEBOOKLM_PROFILE=standard` หรือรัน:

```powershell
& "C:\ProgramData\McGroup\Claude\mcp\node-portable\node-v22.16.0-win-x64\npx.cmd" notebooklm-mcp config set profile standard
```

---

## MCP Tools — แบ่งตามหมวดหมู่

### 1. Q&A (ถามคำถาม)

| Tool | ใช้ทำอะไร |
|------|----------|
| `ask_question` | ถามคำถาม notebook — รองรับ session reuse, citations (source_format), browser overrides |

**Citation modes** (ผ่าน `source_format`):

| Mode | พฤติกรรม |
|------|---------|
| `none` | ข้อความดิบ ไม่มี sources (เร็วที่สุด) |
| `inline` | แทรก [N] markers ด้วย (source name — excerpt) |
| `footnotes` | เพิ่ม Sources section ท้ายคำตอบ |
| `json` | คำตอบ + structured `sources[]` array |

### 2. Sources & Studio (แหล่งข้อมูลและเนื้อหา)

| Tool | ใช้ทำอะไร |
|------|----------|
| `add_source` | เพิ่ม source (type=url หรือ type=text) |
| `generate_audio` | สร้าง Audio Overview (podcast) — รองรับ custom_prompt |
| `download_audio` | ดาวน์โหลด Audio Overview ล่าสุด |

### 3. Library Management (จัดการ Notebook Library)

| Tool | ใช้ทำอะไร |
|------|----------|
| `add_notebook` | เพิ่ม NotebookLM share-URL เข้า library พร้อม metadata |
| `list_notebooks` | แสดงรายการ notebook ทั้งหมดใน library |
| `get_notebook` | ดูรายละเอียด notebook ตาม id |
| `select_notebook` | ตั้ง notebook เป็น active default |
| `update_notebook` | แก้ไข name, description, topics, tags |
| `remove_notebook` | ลบออกจาก local library (ไม่ลบจาก NotebookLM) |
| `search_notebooks` | ค้นหาตาม name, description, topics, tags |
| `get_library_stats` | สถิติการใช้งาน library |

### 4. Sessions (จัดการ browser sessions)

| Tool | ใช้ทำอะไร |
|------|----------|
| `list_sessions` | แสดง active sessions พร้อม age + message count |
| `close_session` | ปิด session ตาม session_id |
| `reset_session` | Reset chat history (เก็บ session_id เดิม) |

### 5. System (ระบบ)

| Tool | ใช้ทำอะไร |
|------|----------|
| `get_health` | ตรวจสอบ auth, session count, config |
| `setup_auth` | Login Google ครั้งแรก (เปิด Chrome) |
| `re_auth` | Wipe auth + login ใหม่ |
| `cleanup_data` | ลบข้อมูลทั้งหมด (preserve_library=true เก็บ library ไว้) |

---

## Workflow ที่แนะนำ

### ถามคำถามจาก Notebook

```
1. get_health — ตรวจสอบ auth status
2. list_notebooks — ดู notebooks ที่มี
3. select_notebook — เลือก notebook ที่ต้องการ
4. ask_question — ถามคำถาม (ใช้ source_format="footnotes" สำหรับ citations)
```

### เพิ่ม Notebook ใหม่เข้า Library

```
1. ให้ user สร้าง notebook ที่ notebooklm.google แล้ว Share → Copy link
2. add_notebook — เพิ่ม URL + metadata (name, description, topics)
3. select_notebook — ตั้งเป็น active
4. ask_question — เริ่มถาม
```

### เพิ่ม Source แล้วถาม

```
1. select_notebook — เลือก notebook
2. add_source — เพิ่ม URL หรือ text
3. ask_question — ถามเกี่ยวกับ source ที่เพิ่ม
```

### สร้าง Audio Podcast

```
1. select_notebook — เลือก notebook
2. generate_audio — สร้าง Audio Overview (รอนาน ≤ 10 นาที)
3. download_audio — ดาวน์โหลดไฟล์เสียง
```

### Follow-up Questions (ต่อเนื่อง)

```
1. ask_question — ถามคำถามแรก → ได้ session_id กลับมา
2. ask_question (session_id=xxx) — ถามต่อในบริบทเดิม
```

---

## Environment Variables

| Env var | Default | ใช้ทำอะไร |
|---------|---------|----------|
| `HEADLESS` | true | รัน Chrome headless (ตั้ง false เพื่อดู browser) |
| `NOTEBOOKLM_PROFILE` | full | Tool profile: minimal / standard / full |
| `NOTEBOOKLM_ACCOUNT` | (ไม่ตั้ง) | Multi-account profile slug |
| `MAX_SESSIONS` | 10 | จำนวน concurrent browser sessions |
| `SESSION_TIMEOUT` | 900 | วินาทีก่อน session หมดอายุ |
| `ANSWER_TIMEOUT_MS` | 600000 | เวลารอคำตอบจาก NotebookLM (10 นาที) |
| `BROWSER_TIMEOUT` | 30000 | Timeout ต่อ action (30 วินาที) |
| `STEALTH_ENABLED` | true | Human-like typing/mouse behavior |
| `NOTEBOOKLM_AI_MARKER` | true | เพิ่ม [AI-GENERATED] prefix ในคำตอบ |
| `NOTEBOOKLM_DISABLED_TOOLS` | (ไม่ตั้ง) | Comma-separated tool names ที่จะปิด |

---

## เมื่อเจอ Error

| อาการ | วิธีแก้ |
|-------|---------|
| `authenticated: false` | รัน `setup_auth` (show_browser=true) |
| Auth ล้มเหลวซ้ำ | `cleanup_data` (preserve_library=true) → `setup_auth` ใหม่ |
| Session timeout | เรียก `ask_question` ใหม่โดยไม่ส่ง session_id (สร้าง session ใหม่) |
| Chrome ไม่เปิด | ตั้ง env `BROWSER_CHANNEL=chromium` ใช้ bundled Chromium แทน |
| Rate limited | Free tier ~50 queries/วัน — รอหรืออัปเกรด Google AI Pro |
| Tool not found | ตรวจสอบ profile ที่ตั้งไว้ (`NOTEBOOKLM_PROFILE`) |

---

## ข้อจำกัดที่ควรทราบ

- **ไม่มี official API**: ใช้ Chrome automation (Patchright) ควบคุม NotebookLM UI
- **Rate limit**: Free tier ~50 queries/วัน, ~100 notebooks, ~50 sources/notebook
- **Audio generation**: ใช้เวลานาน (หลายนาที) ต้องรอ
- **Login ต้องทำเอง**: ไม่สามารถ automate Google login ได้ ต้องเปิด browser แล้ว login ด้วยตัวเอง
- **Chrome profile**: Cookies อาจหมดอายุ ต้อง re-auth เป็นระยะ
