---
name: "path-resolver"
description: "Resolves and validates file paths across Windows ↔ Linux VM sandbox environments. Use whenever Claude works with files and needs to translate paths between Read/Write/Edit tools (Windows paths) and Bash (Linux paths). Triggers on: any file-not-found or path-related errors, when the user asks \"where is my file\", \"why can't I access this\", \"check the path\", or when you're about to use a path and aren't 100% sure of the correct form. Also proactively checks paths before file operations when the target tool is different from the one last used to discover the file. Outputs a current-session path mapping table and can validate/correct any given path."
---

# Path Resolver

Resolve and validate file paths between Windows (Read/Write/Edit/Glob/Grep tools) and Linux VM (Bash tool).

---

## Why paths break

Claude Desktop runs inside a Linux VM sandbox. File tools (Read, Write, Edit, Glob, Grep) use **Windows-style absolute paths** like `C:\Users\...\Documents\Workspace\file.txt`. The Bash tool uses **Linux mount paths** like `/sessions/<session-name>/mnt/Workspace/file.txt`. Mixing them up is the #1 cause of tool failures.

Each session gets a unique session name (e.g., `compassionate-wizardly-ride`), so Linux mount paths change between sessions — never hardcode or reuse a path from a previous session.

---

## Step 1: Discover the current session

**Always** start by discovering the **current session's Linux mount point**. Run this one-liner:

```bash
for dir in /sessions/*/; do
  if [ -d "${dir}mnt/Workspace" ] && [ -d "${dir}mnt/outputs" ]; then
    echo "SESSION_ROOT=${dir%/}"; break
  fi
done
```

Save this as `$SESSION_ROOT`. Then verify:

```bash
ls $SESSION_ROOT/mnt/
# Should show: Workspace outputs uploads
```

---

## Step 2: Build the path mapping table

Using the discovered session root, construct this table. Present it to the user (or to yourself) whenever a path issue arises.

| Purpose | Windows Path (for Read/Write/Edit/Glob/Grep) | Linux Path (for Bash) |
|---|---|---|
| **Workspace** (user files) | `C:\Users\ekkachai.k.MCJEANS\Documents\Workspace\...` | `/sessions/<session>/mnt/Workspace/...` |
| **Outputs** (temp scratch) | `C:\Users\ekkachai.k.MCJEANS\AppData\Local\Claude-3p\local-agent-mode-sessions\...\outputs\...` | `/sessions/<session>/mnt/outputs/...` |
| **Uploads** (read-only) | `C:\Users\ekkachai.k.MCJEANS\AppData\Local\Claude-3p\local-agent-mode-sessions\...\uploads\...` | `/sessions/<session>/mnt/uploads/...` |
| **Skills** (read-only) | `C:\Users\ekkachai.k.MCJEANS\AppData\Local\Claude-3p\local-agent-mode-sessions\skills-plugin\...\skills\...` | `/sessions/<session>/mnt/.claude/skills/...` |

**Key rule:** The session ID (`local_6eaee125-...`) and session name (`compassionate-wizardly-ride`) change every session. Always rediscover — never reuse from memory.

---

## Step 3: Path translation logic

### Windows → Linux (for Bash)

```
Input:  C:\Users\ekkachai.k.MCJEANS\Documents\Workspace\subdir\file.txt
Steps:
  1. Identify the root: "Documents\Workspace\" → this is Workspace
  2. Strip the Windows prefix up to and including "Workspace\"
  3. Prepend: /sessions/<session>/mnt/Workspace/
  4. Replace \ with /
Output: /sessions/<session>/mnt/Workspace/subdir/file.txt
```

```
Input:  C:\Users\ekkachai.k.MCJEANS\AppData\Local\Claude-3p\local-agent-mode-sessions\909fb457\3941d10b\local_xxx\outputs\report.docx
Steps:
  1. Find "outputs\" in the path → this is the Outputs folder
  2. Strip everything up to and including "outputs\"
  3. Append the remainder to /sessions/<session>/mnt/outputs/
Output: /sessions/<session>/mnt/outputs/report.docx
```

### Linux → Windows (for Read/Write/Edit)

```
Input:  /sessions/<session>/mnt/Workspace/subdir/file.txt
Steps:
  1. Strip /sessions/<session>/mnt/Workspace/
  2. Prepend: C:\Users\ekkachai.k.MCJEANS\Documents\Workspace\
  3. Replace / with \
Output: C:\Users\ekkachai.k.MCJEANS\Documents\Workspace\subdir\file.txt
```

---

## Step 4: Validate a path before use

Before any file operation, ask these questions:

1. **Which tool am I calling?**
   - Read / Write / Edit / Glob / Grep → needs Windows path
   - Bash → needs Linux mount path
   - mcp__filesystem__\* → needs Windows path

2. **Does the path start with the expected prefix for that tool?**
   - Windows tool: must start with `C:\`
   - Bash: must start with `/sessions/`

3. **Does the file/folder actually exist at this path?**
   - Use `mcp__filesystem__get_file_info` (Windows path) to verify
   - Or use Bash: `test -f <linux-path> && echo "exists" || echo "missing"`

4. **If path fails, translate it** using Step 3 above.

---

## When to use this skill

**Proactive triggers** (use automatically, don't wait for the user):
- You're about to call Bash on a file you discovered with Read/Glob/Grep
- You're about to call Read/Write on a file you discovered with Bash
- A tool call returned "file not found" or "no such file"
- You notice a path that starts with the wrong prefix for the tool being used

**On-demand triggers** (user explicitly asks):
- "Where is my file?"
- "Why can't you access this?"
- "Check the path"
- "Fix the path"
- "Show me the path mapping"

---

## Quick reference card

When in doubt, run this one-liner to rediscover the session:

```bash
SESSION=$(dirname $(pwd)) && echo "Session root: $SESSION" && echo "Workspace: $SESSION/mnt/Workspace" && echo "Outputs: $SESSION/mnt/outputs" && echo "Uploads: $SESSION/mnt/uploads"
```

Then always present paths to the user in **Windows format** since that's what they see on their machine. Only use Linux paths internally for Bash commands.
