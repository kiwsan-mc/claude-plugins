---
name: "email-digest"
description: "Summarize unread Outlook emails, categorize by priority (urgent/high/normal/low), and suggest response actions. Use whenever the user asks for \"email summary\", \"what's in my inbox\", \"check my email\", \"inbox digest\", \"email triage\", or wants to know what needs their attention in Outlook."
---

# Email Digest Skill

Summarize unread Outlook emails, categorize them by priority, and suggest which ones need action first.

**MCP Tools Needed:**
- `mcp__ms-outlook__outlook_list_mails` — to fetch unread emails
- `mcp__ms-outlook__outlook_get_mail` — to read full email content when needed
- `mcp__ms-outlook__outlook_whoami` — to identify the current mailbox

## Workflow

### Step 1: Fetch Unread Emails

Call `outlook_list_mails` with these filters to get unread messages from the inbox:

```
mcp__ms-outlook__outlook_list_mails(
  folder="Inbox",
  unread=true,
  limit=30,
  order_by="receivedDateTime DESC"
)
```

### Step 2: Categorize by Priority

For each email, classify into one of these priority levels based on subject line and sender analysis:

| Priority | Criteria | Icon |
|----------|----------|------|
| **Urgent** | Contains "urgent", "ASAP", deadline today, from direct manager, system alerts, meeting within 2 hours | 🔴 |
| **High** | Action required from you, specific request, meeting invites, client/vendor communication | 🟡 |
| **Normal** | Informational, newsletters, FYI, CC-only, automated reports | 🟢 |
| **Low** | Promotional, spam-like, no action needed | ⚪ |

### Step 3: Generate Digest

Produce a markdown table with these columns:
- Priority (emoji)
- Sender name
- Subject (keep brief)
- Suggested action (e.g., "Reply today", "Review before 3pm meeting", "Archive", "Read later")

### Step 4: Key Insights

At the bottom of the digest, add 2-3 bullet points of key insights:
- Patterns noticed (e.g., "3 emails about Project X — this needs attention")
- Time-sensitive items (e.g., "2 meeting invites for today")
- Any senders who emailed multiple times

## Output Format

```markdown
# Inbox Digest — {date} {time}

{mailbox_name} — {unread_count} unread emails

## Priority

| | Sender | Subject | Action |
|---|---|---|---|
| 🔴 | ... | ... | ... |
| 🟡 | ... | ... | ... |
| 🟢 | ... | ... | ... |
| ⚪ | ... | ... | ... |

## Key Insights
- ...
- ...

## Suggested Next Actions
1. ...
2. ...
3. ...
```

## Tips
- For urgent items, offer to draft a reply immediately
- If an email has attachments, note them in the "Action" column
- If the inbox has very few unread items (<5), suggest the user might want to see calendar events instead
- Use `outlook_get_mail` only for emails where the subject alone isn't enough to categorize — save token usage by categorizing most from the list view
