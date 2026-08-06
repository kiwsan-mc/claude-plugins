---
name: "artifact-creator-v3"
description: "[v3] Use this skill whenever creating Cowork artifacts for MC Group sales dashboards. Mandatory localStorage cache pattern prevents unwanted permission popups. Includes E2E validation step (Step 12) that verifies artifact integrity before and after create_artifact. Covers all 11 technical sections + validation checklist."
---

# Artifact Creator - Technical Patterns (v3)

Build live monitoring dashboards as Cowork artifacts with MCP data fetching, localStorage caching, and Chart.js charts. This skill contains proven patterns from real production artifacts.

---

## Step 0 - AskUserQuestion (MANDATORY - before anything else)

**Every time this skill is invoked - always ask the user which output format they want FIRST**

Use AskUserQuestion tool before querying data or creating files:

**Question 1: Output Format**
- Header: "Format"
- Question: "Which output format do you want?"
- Options:
  1. "Reply in chat" - analyze data and respond as text in chat, no artifact
  2. "Create Artifact" - build interactive dashboard, open in sidebar, self-refreshable

If user chooses "Reply in chat": query data, analyze in chat normally (skip Step 0B)

If user chooses "Create Artifact": proceed to Step 0B

---

## Step 0B - Clarify Scope (only if creating Artifact)

If the user request is ambiguous - ask 1-3 follow-up questions:

- Data scope: "Which time period? This FY vs last year? Full year?"
- Perspective: "What drill-down level? Region/Province/Branch?"
- Metrics: "Which numbers matter most? Net Sales / Margin% / Tickets / YoY?"
- Filter: "Filter by channel? (Online/Offline/All)"

Examples of when to ask:

| Request | Ambiguous? | Should ask |
|---------|-----------|------------|
| "Create 4-region sales monitor" | No | Don't ask |
| "Create sales dashboard" | Yes | Ask: which angle? Overview/ABC/Regional/Discount? |
| "Make a monitor" | Yes | Ask: what topic? which dimension? |
| "Monitor margin" | Yes | Ask: Margin by Region/Category/Channel? |

Rule of thumb: if you can pick the right mcg-sales-agent skill without guessing = clear enough. If uncertain which skill to use = ask.

---

## Step 0C - Complexity Gate (MANDATORY - before building Artifact)

**If the request scope is too broad or data volume risks refresh failure - DO NOT squash into one artifact. Split into multiple artifacts.**

### Complexity Thresholds - if ANY condition is met, do NOT build a single artifact:

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Too many dimensions | >=4 dimensions in one dashboard (e.g. Region + Category + Member + Discount + Pricing) | Split: 1 artifact per dimension |
| Too many skills | Requires >=3 mcg-sales-agent skills | Split: 1 artifact per skill |
| Query count | Artifact needs >=5 queries to get complete data | Split into smaller artifacts or reduce scope |
| Row count | 1 query returns >500 rows (need large table) | Use LIMIT or paginate |
| User asks for "everything" | "show everything" "full dashboard" "all at once" | Ask user to pick 1-2 most important dimensions first |

### Split Strategy:

WRONG - 1 giant artifact:
"Create full sales dashboard"
  -> 1 artifact with: Overview + Regional + ABC + Margin + Member + E-commerce
  -> 6 sections, 10+ queries, guaranteed timeout

RIGHT - multiple small artifacts:
  -> artifact 1: "Overview + Main KPIs" (sales-dashboard)
  -> artifact 2: "4 Regions" (channel-regional)
  -> artifact 3: "ABC Product" (abc-analysis)
  -> artifact 4: "Margin and Discount" (discount-margin)
  -> artifact 5: "Member Analysis" (member-analysis)
  -> artifact 6: "E-commerce" (ecommerce-channel)

### Naming Convention for multiple artifacts:

Use consistent prefix so they form a set:
- sales-overview-dashboard - overview
- sales-regional-4regions - by region
- sales-abc-analysis - ABC
- sales-discount-margin - discount/margin

### If user insists on one big artifact:

Be upfront about the risk - then offer alternatives:
1. "Split into 3-4 small artifacts - guaranteed to refresh"
2. "Build a big artifact but reduce detail - only main KPIs, no drill-down"

**Never force-build a single artifact that hits complexity thresholds - it will break just like the regional monitor Q1 timeout**

---

## Data Source: MCG Sales Agent Plugin (MANDATORY)

When building monitors for MC Group sales data - always use mcg-sales-agent skills first:

1. Identify which specialized skill matches the question (sales-dashboard, abc-analysis, channel-regional, discount-margin, member-analysis, etc.)
2. Call that skill to get KPI formulas, business rules, thresholds
3. Use mcp__mcg-toolbox__pg_execute_sql with query patterns from the skill
4. Build artifact following technical patterns in this skill

Never guess KPI formulas or thresholds - always follow mcg-sales-agent skills.

---

## Architecture: Hybrid (Live MCP + localStorage Cache)

```
Open artifact -> has cache in localStorage?
  YES -> check dateKey matches today?
    YES -> render from cache immediately (no permission needed)
    NO -> clear cache -> show "press button to load data"
  NO -> show "press button to load data"

User clicks refresh button
  -> callMcpTool (request allow once, with Promise.race timeout 25s)
  -> query data source (split into small queries <=1 month scope)
  -> merge/aggregate in JavaScript (avoid complex GROUP BY/CASE WHEN in SQL)
  -> full re-render
  -> save to localStorage with dateKey
```

---

## 1. callSql with Timeout (CRITICAL)

callMcpTool in artifact sandbox has silent timeout problem - large queries hang without returning or throwing:

```javascript
function callMcpWithTimeout(toolName, params, timeoutMs) {
  timeoutMs = timeoutMs || 25000;
  if (!window.cowork || !window.cowork.callMcpTool) {
    return Promise.reject(new Error('window.cowork.callMcpTool not available'));
  }
  var timeoutId;
  var timeoutPromise = new Promise(function(_, reject) {
    timeoutId = setTimeout(function() {
      reject(new Error('TIMEOUT: callMcpTool did not respond within ' + (timeoutMs/1000) + 's'));
    }, timeoutMs);
  });
  return Promise.race([
    timeoutPromise,
    window.cowork.callMcpTool(toolName, params)
  ]).then(function(result) {
    clearTimeout(timeoutId);
    return result;
  }).catch(function(err) {
    clearTimeout(timeoutId);
    throw err;
  });
}

async function callSql(toolName, params) {
  var r;
  try { r = await callMcpWithTimeout(toolName, params, 25000); } catch(e) { throw e; }
  if (r.isError) {
    var msg = 'Query error';
    if (r.content && r.content[0] && r.content[0].text) msg = r.content[0].text;
    throw new Error(msg);
  }
  if (r.structuredContent != null) {
    if (Array.isArray(r.structuredContent)) return r.structuredContent;
    if (typeof r.structuredContent === 'object') return [r.structuredContent];
  }
  var allText = '';
  if (r.content && r.content.length > 0) {
    for (var i = 0; i < r.content.length; i++) {
      var c = r.content[i];
      if (typeof c === 'string') { allText += c + '\n'; }
      else if (c && typeof c.text === 'string') { allText += c.text + '\n'; }
      else if (c && typeof c === 'object') { allText += JSON.stringify(c) + '\n'; }
    }
  }
  allText = allText.trim();
  if (!allText) return [];
  try { var j = JSON.parse(allText); return Array.isArray(j) ? j : [j]; } catch(e) {}
  var rows = [];
  var lines = allText.split('\n');
  for (var li = 0; li < lines.length; li++) {
    var t = lines[li].trim();
    if (!t) continue;
    try { rows.push(JSON.parse(t)); } catch(e) {}
  }
  return rows;
}
```

Important: use var (ES5), not const/let

---

## 2. Query Strategy: Small + Sequential + JS Merge

CRITICAL - large queries cause silent timeout in sandbox (~20-25s)

- Split scope as narrow as possible - 1 query per 1 month - never scan 13 months in one query
- Move GROUP/map logic from SQL to JavaScript
- Use simplest GROUP BY - no nested CASE WHEN in GROUP BY
- Maximum 4 queries per artifact - more than that = artifact too big, should split

**Pattern for comparing FY27 vs FY26 — split into separate queries, merge in JS:**

```javascript
// WRONG: 1 query scanning 13 months with CASE WHEN
"SELECT ... SUM(CASE WHEN fy27 THEN ... WHEN fy26 THEN ...) FROM ... WHERE sold_date BETWEEN '2025-07-01' AND '2026-08-05'"

// RIGHT: 2 small queries, each scanning ~1 month, merge in JS
"SELECT ... SUM(...) FROM ... WHERE sold_date BETWEEN '2026-07-01' AND '2026-08-05'"  // FY27
"SELECT ... SUM(...) FROM ... WHERE sold_date BETWEEN '2025-07-01' AND '2025-08-05'"  // FY26

// Then merge in JavaScript:
var fy26Map = {};
for (var i = 0; i < dataFy26.length; i++) {
  fy26Map[dataFy26[i].key] = dataFy26[i].ns || 0;
}
for (var j = 0; j < dataFy27.length; j++) {
  dataFy27[j].ns_fy26 = fy26Map[dataFy27[j].key] || 0;
}
```

Never use Promise.all - Sequential + per-query try/catch + error accumulation

---

## 3. Dynamic Date Range + Apple-to-Apple (CRITICAL)

Never hard-code dates in SQL - use JavaScript Date object:

```javascript
function getDateRange() {
  var now = new Date();
  var endFY27 = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
  var fyStart = new Date(now.getFullYear(), 6, 1);
  if (now.getMonth() < 6) fyStart = new Date(now.getFullYear() - 1, 6, 1);
  var days = Math.round((endFY27 - fyStart) / 86400000) + 1;
  var fy26Start = new Date(fyStart.getFullYear() - 1, fyStart.getMonth(), fyStart.getDate());
  var endFY26 = new Date(fy26Start.getFullYear(), fy26Start.getMonth(), fy26Start.getDate() + days - 1);
  function fmtDate(d) {
    return d.getFullYear() + '-' + ('0'+(d.getMonth()+1)).slice(-2) + '-' + ('0'+d.getDate()).slice(-2);
  }
  return { fy27Start: fmtDate(fyStart), fy27End: fmtDate(endFY27), fy26Start: fmtDate(fy26Start), fy26End: fmtDate(endFY26) };
}
```

---

## 4. Date & DateTime Formatting (MANDATORY — End-User Readability)

**All dates/datetimes shown to the user MUST be formatted for readability. Never show raw ISO strings like `2026-08-05T14:30:00Z` or `2026-08-05`.**

### Standard Formats:

| Data Type | Format Pattern | Example Output | Use Case |
|-----------|---------------|----------------|----------|
| Date only | `DD MMM YYYY` | `05 Aug 2026` | Report dates, sold_date, period labels |
| Date short | `DD MMM YY` | `05 Aug 26` | Table cells where space is tight |
| DateTime | `DD MMM YYYY HH:mm` | `05 Aug 2026 14:30` | Last updated, timestamp displays |
| DateTime with seconds | `DD MMM YYYY HH:mm:ss` | `05 Aug 2026 14:30:45` | Debug log, precise timestamps |
| Period/Month | `MMM YYYY` | `Aug 2026` | Monthly charts, period headers |
| Period/FY | `FY{YY}` | `FY27` | Fiscal year labels |

### Required Functions:

```javascript
// Format date (date only) — Gregorian (ค.ศ.)
function formatDate(d) {
    if (!d) return '-';
    var s = String(d).replace('T00:00:00Z','').replace('T00:00:00','');
    var parts = s.split('-');
    if (parts.length === 3) {
      var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      return parts[2] + ' ' + months[parseInt(parts[1])-1] + ' ' + parts[0];
    }
    return s;
}

// Format date short — for tight table cells
function formatDateShort(d) {
    if (!d) return '-';
    var s = String(d).replace('T00:00:00Z','').replace('T00:00:00','');
    var parts = s.split('-');
    if (parts.length === 3) {
      var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      var shortYear = String(parts[0]).slice(-2);
      return parts[2] + ' ' + months[parseInt(parts[1])-1] + ' ' + shortYear;
    }
    return s;
}

// Format datetime — Gregorian (ค.ศ.) + time (HH:mm)
function formatDateTime(d) {
    if (!d) return '-';
    var s = String(d);
    var datePart = s.substring(0, 10);
    var timePart = '';
    if (s.length > 10) {
      var t = s.substring(11);
      timePart = t.substring(0, 5); // HH:mm
    }
    var parts = datePart.split('-');
    if (parts.length === 3) {
      var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      var formatted = parts[2] + ' ' + months[parseInt(parts[1])-1] + ' ' + parts[0];
      if (timePart) formatted += ' ' + timePart;
      return formatted;
    }
    return s;
}

// Format datetime with seconds — for debug/precision displays
function formatDateTimeFull(d) {
    if (!d) return '-';
    var s = String(d);
    var datePart = s.substring(0, 10);
    var timePart = '';
    if (s.length > 10) {
      var t = s.substring(11);
      timePart = t.substring(0, 8); // HH:mm:ss
    }
    var parts = datePart.split('-');
    if (parts.length === 3) {
      var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      var formatted = parts[2] + ' ' + months[parseInt(parts[1])-1] + ' ' + parts[0];
      if (timePart) formatted += ' ' + timePart;
      return formatted;
    }
    return s;
}

// Format month/period label — for chart axes and period headers
function formatPeriod(yearMonth) {
    // Accepts "2026-08" or "2026-08-01"
    if (!yearMonth) return '-';
    var parts = String(yearMonth).split('-');
    if (parts.length >= 2) {
      var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      return months[parseInt(parts[1])-1] + ' ' + parts[0];
    }
    return String(yearMonth);
}

// Format "last updated" — human-friendly absolute
function formatLastUpdated() {
    var now = new Date();
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var day = ('0' + now.getDate()).slice(-2);
    var mon = months[now.getMonth()];
    var year = now.getFullYear();
    var hh = ('0' + now.getHours()).slice(-2);
    var mm = ('0' + now.getMinutes()).slice(-2);
    return day + ' ' + mon + ' ' + year + ' ' + hh + ':' + mm;
}
```

### Usage Rules:

| Where | Use Function | Example |
|-------|-------------|---------|
| Table column "วันที่ขาย" | `formatDate(row.sold_date)` | `05 Aug 2026` |
| Table column with tight space | `formatDateShort(row.sold_date)` | `05 Aug 26` |
| Header "Last Updated" | `formatLastUpdated()` | `05 Aug 2026 14:30` |
| Header "Data Period" | `formatDate(dr.fy27Start) + ' - ' + formatDate(dr.fy27End)` | `01 Jul 2026 - 04 Aug 2026` |
| Chart X-axis (monthly) | `formatPeriod(row.month)` | `Aug 2026` |
| Debug log timestamps | `formatDateTimeFull(row.created_at)` | `05 Aug 2026 14:30:45` |
| Footer "ข้อมูล ณ วันที่" | `formatLastUpdated()` | `05 Aug 2026 14:30` |

### NEVER show to end user:

| Bad (raw) | Good (formatted) |
|-----------|------------------|
| `2026-08-05` | `05 Aug 2026` |
| `2026-07-02T00:00:00Z` | `02 Jul 2026` |
| `2026-08-05T14:30:00Z` | `05 Aug 2026 14:30` |
| `2026-08-05T14:30:00.000Z` | `05 Aug 2026 14:30` |
| `2026-08` | `Aug 2026` |
| `1722849000000` (epoch) | `05 Aug 2026 14:30` |

### Rendering Guard (CRITICAL — #1 cause of raw date leaks)

**The most common bug: building table rows with `row.sold_date` or `row.some_date` directly in innerHTML without calling formatDate().**

WRONG — raw date leaks into UI:
```javascript
// BAD: This shows "2026-07-02T00:00:00Z" to user
html += '<td>' + row.sold_date + '</td>';
html += '<td>' + row.created_at + '</td>';
html += '<td>' + row.period + '</td>';
```

RIGHT — always wrap date fields:
```javascript
// GOOD: Shows "02 Jul 2569" to user
html += '<td>' + formatDate(row.sold_date) + '</td>';
html += '<td>' + formatDateTime(row.created_at) + '</td>';
html += '<td>' + formatPeriod(row.period) + '</td>';
```

**Rule: ANY field from SQL that contains a date/datetime/period MUST pass through the appropriate format function before being placed in innerHTML, textContent, or any visible DOM element.**

Common date fields in mcg-sales-agent queries that MUST be formatted:
- `sold_date` → `formatDate()`
- `created_at` / `updated_at` → `formatDateTime()`
- `period` / `month` / `year_month` → `formatPeriod()`
- `start_date` / `end_date` → `formatDate()`
- Any field ending in `_date`, `_at`, `_time` → format it

### Quick Detection Pattern (for self-review before create_artifact):

Search your artifact HTML for these patterns — if found, it's a bug:
- `row.sold_date` NOT wrapped in `formatDate()`
- `row.*_date` NOT wrapped in `formatDate()`
- `row.*_at` NOT wrapped in `formatDateTime()`
- Any `+ row.` followed by a date field name without format wrapper

---

## 5. Number Formatting

```javascript
function fmt(n) {
  if (n == null || isNaN(n)) return '-';
  if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(2) + 'M';
  if (Math.abs(n) >= 1e3) return (n / 1e3).toFixed(1) + 'K';
  return Number(n).toLocaleString('en-US', {maximumFractionDigits: 0});
}

function pctStr(a, b) {
  if (!b || b === 0) return '-';
  return ((a - b) / b * 100).toFixed(1) + '%';
}

function yoyPct(a, b) {
  if (!b || b === 0) return {v:'-', cls:'yoy-flat'};
  var p = (a - b) / b * 100;
  return {v: (p >= 0 ? '+' : '') + p.toFixed(1) + '%', cls: p > 0 ? 'yoy-up' : p < 0 ? 'yoy-down' : 'yoy-flat'};
}
```

---

## 6. Chart.js - Destroy Before Recreate

```javascript
var barInst = null, doughInst = null;

// In render function, before creating chart:
setTimeout(function() {
  if (barInst) barInst.destroy();
  var ctx = document.getElementById('chartId').getContext('2d');
  barInst = new Chart(ctx, { type: 'bar', data: {...}, options: {...} });
}, 200);
```

Create charts in setTimeout(function() {...}, 200) after innerHTML — DOM must exist before Chart.js binds.

---

## 7. localStorage Cache + Auto-Invalidation (CRITICAL — MANDATORY)

**Every artifact MUST implement this exact pattern. No exceptions.**

Without proper cache, Cowork's artifact framework may auto-trigger `callMcpTool` on page open to revalidate — causing unwanted permission popups. This pattern prevents that by rendering from cache immediately when data is already fresh.

### Required functions (paste these into EVERY artifact):

```javascript
var CACHE_KEY = 'your-artifact-id-v1';  // unique per artifact

function getDateKey() {
  var d = new Date();
  return d.getFullYear() + '-' + ('0'+(d.getMonth()+1)).slice(-2) + '-' + ('0'+d.getDate()).slice(-2);
}

function tryLoadCache() {
  try {
    var raw = localStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    var cache = JSON.parse(raw);
    if (cache.dateKey === getDateKey() && cache.data) {
      dlog('Cache hit: ' + cache.dateKey);
      return cache.data;
    }
    dlog('Cache stale, clearing');
    localStorage.removeItem(CACHE_KEY);
    return null;
  } catch(e) { dlog('Cache error: ' + e.message); return null; }
}

function saveCache(data) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify({dateKey: getDateKey(), data: data}));
    dlog('Cache saved: ' + getDateKey());
  } catch(e) { dlog('Cache write error: ' + e.message); }
}
```

### Required in loadData() — save BEFORE render:

```javascript
function loadData() {
  var btn = document.getElementById('refreshBtn');
  btn.disabled = true;
  btn.textContent = 'Loading...';
  fetchData().then(function(results) {
    saveCache(results);       // <-- MUST call saveCache BEFORE renderAll
    renderAll(results);       // renderAll modifies data in-place (adds calculated fields)
    btn.disabled = false;
    btn.textContent = 'Refresh Data';
  }).catch(function(err) {
    dlog('ERROR: ' + err.message);
    btn.disabled = false;
    btn.textContent = 'Refresh Data';
  });
}
```

### Required init block — try cache first, NEVER auto-call MCP:

```javascript
// INIT — MUST be at bottom of <script> tag, replacing any window.addEventListener('load', ...)
// Try cache first → if fresh, render instantly (zero MCP calls)
// If stale/missing → show placeholder, user must click Refresh
dlog('Init — checking cache...');
var cached = tryLoadCache();
if (cached) {
  dlog('Rendering from cache');
  document.getElementById('refreshBtn').textContent = 'Refresh Data (cached)';
  renderAll(cached);
} else {
  // Show placeholder — DO NOT call loadData() or any MCP tool here
  document.getElementById('YOUR_MAIN_CONTAINER').innerHTML = '<div style="text-align:center;padding:40px;color:#95a5a6;">Click <strong>Refresh Data</strong> to load</div>';
  document.getElementById('periodInfo').textContent = 'Ready to load';
}
```

### Cache rules:

| Rule | Why |
|------|-----|
| **NEVER call `loadData()` on page open** | No `window.addEventListener('load', loadData)`, no `<body onload>`, no auto-execute — prevents unwanted permission popups |
| **CACHE_KEY unique per artifact** | Use pattern `sales-{topic}-v1` — prevents cache collision |
| **`saveCache(results)` BEFORE `renderAll(results)`** | renderAll modifies data in-place (adds `margin`, `abc`, `cumPct` fields) — cache raw query results |
| **Same-day cache = instant render** | Zero MCP calls, zero permission popups, zero network requests |
| **Cross-day cache auto-invalidates** | dateKey changes → localStorage cleared → placeholder shown → user clicks Refresh |
| **`tryLoadCache()` returns null on any error** | Try/catch guards against corrupted localStorage |

---

## 8. Debug Box (MANDATORY)

Always include for troubleshooting:

```html
<div class="debug-box" id="debugBox"></div>
```

```css
.debug-box { margin-top:16px; padding:12px; background:#f8f9fa; border-radius:8px; font-size:11px; color:#666; max-height:200px; overflow-y:auto; font-family:monospace; display:none; }
```

```javascript
function dlog(msg) {
  var db = document.getElementById('debugBox');
  db.style.display = 'block';
  db.innerHTML += '[' + new Date().toLocaleTimeString() + '] ' + msg + '<br>';
  db.scrollTop = db.scrollHeight;
}
```

---

## 9. CSS Base Template

```css
:root { color-scheme: light; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Tahoma, sans-serif; background: #f5f6fa; color: #2c3e50; padding: 20px; }
.header { background: linear-gradient(135deg, #2c3e50, #34495e); color: #fff; padding: 24px 30px; border-radius: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.header h1 { font-size: 22px; font-weight: 700; }
.header .period { font-size: 14px; opacity: 0.85; }
.btn { background: #3498db; color: #fff; border: none; padding: 10px 24px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
.btn:hover { background: #2980b9; }
.btn:disabled { background: #bdc3c7; cursor: not-allowed; }
.section { background: #fff; border-radius: 10px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.section h2 { font-size: 16px; font-weight: 700; color: #2c3e50; margin-bottom: 14px; padding-bottom: 8px; border-bottom: 2px solid #ecf0f1; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { background: #f8f9fa; padding: 10px 12px; text-align: left; font-weight: 600; color: #555; border-bottom: 2px solid #dee2e6; }
td { padding: 10px 12px; border-bottom: 1px solid #ecf0f1; }
tr:hover td { background: #f8f9fa; }
.text-right { text-align: right; }
.chart-wrap { height: 320px; position: relative; }
.footer { font-size: 12px; color: #95a5a6; text-align: center; padding: 16px 0; }
.yoy-up { color: #27ae60; }
.yoy-down { color: #e74c3c; }
.yoy-flat { color: #95a5a6; }
```

---

## 10. Known Issues and Troubleshooting Flow

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Popup on open without clicking Refresh | Missing localStorage cache pattern → framework auto-revalidates | Implement Section 7 cache pattern |
| Silent timeout (>25s, no response) | Query scanning >3 months of data | Split FY27/FY26 into separate queries, each scanning ~1 month |
| "T00:00:00Z" in date displays | PostgreSQL date cast without formatting | Use `formatDate()` function from Section 4 |
| Raw ISO date like "2026-08-05" shown | Date not formatted before display | Use `formatDate()` for date, `formatDateTime()` for datetime |
| Raw datetime like "2026-08-05T14:30:00Z" | Datetime not formatted | Use `formatDateTime()` — shows `05 Aug 2026 14:30` |
| Month shown as "2026-08" | Period not formatted | Use `formatPeriod()` — shows `Aug 2026` |
| Chart not rendering | Chart created before DOM ready | Use `setTimeout(function(){...}, 200)` after `innerHTML` |
| "window.cowork.callMcpTool not available" | Artifact opened outside Cowork | Show friendly message, artifact only works in Cowork sidebar |
| Cache not saving | `saveCache()` called AFTER `renderAll()` which modified data | Move `saveCache(results)` BEFORE `renderAll(results)` |

---

## 11. Checklist: Building a New Artifact (20 items)

1. Step 0: AskUserQuestion - ask chat reply or artifact first
2. Step 0B: Clarify if needed - if request ambiguous, ask more
3. Step 0C: Complexity Gate - check >=4 dimensions? >=3 skills? >=5 queries? -> split artifacts
4. Pick right mcg-sales-agent skill - get KPI formulas + business rules
5. Dynamic date range - getDateRange() never hard-code
6. Split queries small - <=1 month scope per query - JS merge (especially FY27/FY26 separate)
7. Max 4 queries per artifact - more = split
8. callMcpWithTimeout - Promise.race 25s - never Promise.all
9. localStorage cache (Section 7) - **MANDATORY**: CACHE_KEY, getDateKey, tryLoadCache, saveCache, cache-init block, NO auto-load, saveCache BEFORE renderAll
10. Debug box - dlog() every step
11. ES5 only - var + function - never const/let/arrow
12. callSql() - structuredContent, JSON array, NDJSON
13. fmt() / pctStr() / yoyPct() / formatDate() / formatDateTime() / formatPeriod() / formatLastUpdated()
14. **Date/DateTime formatting (Section 4)** — NEVER show raw ISO dates to user, always use formatted Gregorian (ค.ศ.) year
15. Chart.js - destroy -> setTimeout 200ms -> recreate
16. CSS - Section 9 base template
17. Refresh button - disabled while loading, show "(cached)" label when from cache
18. Cache init block - tryLoadCache() first, placeholder if no cache, NEVER auto-call loadData()
19. Never share file path inside artifact - artifact only
20. Naming convention - if multiple artifacts, use consistent prefix


---

## 12. E2E Validation (MANDATORY — before AND after create_artifact)

**Run validation TWICE: once before `create_artifact` and once after. Never skip.**

This step catches the bugs that would otherwise surface as runtime errors in the user's browser:
- Wrong MCP parameter names (`query` instead of `sql`)
- Missing required functions or DOM elements
- ES6 syntax leaking into ES5-only sandbox
- Cache ordering bugs (save after render)
- Chart.js init timing issues

### 12A — Pre-Create Validation (before `create_artifact`)

After writing the HTML file but BEFORE calling `create_artifact`, run this bash validation script:

```bash
python3 << 'VALIDEOF'
import re, sys

with open('ARTIFACT_PATH', 'r') as f:
    html = f.read()

errors = []
warnings = []

# === 1. STRUCTURE CHECKS ===
if '<!DOCTYPE html>' not in html:
    errors.append('MISSING: <!DOCTYPE html>')
if '</html>' not in html:
    errors.append('MISSING: closing </html>')
if '<script>' not in html or '</script>' not in html:
    errors.append('MISSING: <script> tags')

# === 2. REQUIRED DOM ELEMENTS ===
required_ids = ['refreshBtn', 'periodInfo', 'debugBox', 'summaryGrid', 'tablesArea']
for rid in required_ids:
    if f'id="{rid}"' not in html and f"id='{rid}"' not in html:
        errors.append(f'MISSING DOM element: id="{rid}"')

# === 3. REQUIRED JS FUNCTIONS (check function signatures) ===
required_funcs = [
    'function dlog(', 'function getDateKey(', 'function tryLoadCache(',
    'function saveCache(', 'function fmt(', 'function yoyPct(',
    'function callMcpWithTimeout(', 'function callSql(', 'function getDateRange(',
    'function loadData(', 'function renderAll(', 'function fetchData('
]
for func in required_funcs:
    if func not in html:
        errors.append(f'MISSING function: {func}')

# === 4. ES5 COMPLIANCE (no const/let/arrow) ===
script_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if script_match:
    script = script_match.group(1)
    const_matches = re.findall(r'\bconst\s+\w+\s*=', script)
    let_matches = re.findall(r'\blet\s+\w+\s*=', script)
    arrow_matches = re.findall(r'=>\s*\{', script)
    if const_matches:
        errors.append(f'ES6 const found ({len(const_matches)} instances): {const_matches[:3]}')
    if let_matches:
        errors.append(f'ES6 let found ({len(let_matches)} instances): {let_matches[:3]}')
    if arrow_matches:
        errors.append(f'ES6 arrow functions found ({len(arrow_matches)} instances)')
else:
    errors.append('Cannot extract <script> content for ES5 check')

# === 5. callSql PARAMETER NAME (CRITICAL — must be {sql: ...} not {query: ...}) ===
if script_match:
    query_params = re.findall(r'callSql\([^,]+,\s*\{\s*query\s*:', script)
    if query_params:
        errors.append(f'CRITICAL: Found {{query: ...}} instead of {{sql: ...}} in callSql ({len(query_params)} instances). This will cause runtime error.')

# === 6. localStorage CACHE_KEY (must be unique, must exist) ===
if 'var CACHE_KEY' not in html:
    errors.append('MISSING: var CACHE_KEY declaration')

# === 7. CACHE INIT BLOCK (NO auto-call loadData) ===
if 'window.addEventListener(' in html and 'load' in html:
    errors.append('FORBIDDEN: window.addEventListener with load — will auto-call MCP')
if '<body onload=' in html.lower():
    errors.append('FORBIDDEN: body onload — will auto-call MCP')

# Check that init block loads cache, does NOT call loadData()
if not re.search(r"dlog\('Init.*checking cache", html):
    errors.append('MISSING: cache init block (dlog Init...checking cache)')
if re.search(r"var cached = tryLoadCache\(\);\s*if\s*\(\s*cached\s*\)", html):
    pass
else:
    warnings.append('Cache init block may be missing or malformed — verify tryLoadCache then renderAll pattern')

# === 8. saveCache BEFORE renderAll in loadData ===
if script_match:
    save_pos = script.find('saveCache(')
    render_pos = script.find('renderAll(')
    if save_pos < 0:
        errors.append('MISSING: saveCache() call in loadData')
    elif render_pos < 0:
        errors.append('MISSING: renderAll() call')
    elif save_pos > render_pos:
        errors.append('ORDER: saveCache() must be called BEFORE renderAll() in loadData')

# === 9. CHART CDN (if using charts) ===
if 'Chart' in html and 'new Chart(' in html:
    if 'chart.js@' not in html.lower():
        errors.append('MISSING: Chart.js CDN script tag (but new Chart() found in JS)')
    if 'getContext(' not in html:
        warnings.append('Chart declared but getContext not found — chart may not render')

# === 10. DEBUG BOX CSS ===
if '.debug-box' not in html:
    errors.append('MISSING: .debug-box CSS rule')
if 'function dlog(' not in html:
    errors.append('MISSING: dlog() function')

# === 11. CSS light mode ===
if 'color-scheme: light' not in html:
    warnings.append('MISSING: :root { color-scheme: light } — artifact may render in dark mode')

# === 12. MCP TOOLS referenced correctly ===
mcp_calls = re.findall(r"callMcpWithTimeout\('([^']+)'", script) if script_match else []
mcp_calls += re.findall(r'callMcpWithTimeout\("([^"]+)"', script) if script_match else []
if mcp_calls:
    for call in mcp_calls:
        if not call.startswith('mcp__'):
            errors.append(f'INVALID MCP tool name: {call}')

# === 13. SQL injection check (dates must use dynamic vars, not hard-coded) ===
if script_match:
    hardcoded_dates = re.findall(r"BETWEEN\s+'20\\d\\d-\\d\\d-\\d\\d'\\s+AND\\s+'20\\d\\d-\\d\\d-\\d\\d'", script)
    if hardcoded_dates:
        errors.append(f'HARDCODED dates in SQL ({len(hardcoded_dates)} instances) — must use getDateRange()')

# === 14. RAW DATE LEAK CHECK (date fields displayed without formatDate/formatDateTime) ===
if script_match:
    # Look for common date field names used directly in innerHTML without format wrapper
    raw_date_patterns = re.findall(r"(?:row|item|d|r)\.(sold_date|created_at|updated_at|start_date|end_date|period|month|year_month|\w+_date|\w+_at)", script)
    if raw_date_patterns:
        # Check if they appear outside of formatDate/formatDateTime/formatPeriod calls
        unformatted = []
        for match in re.finditer(r"['\"`\+]\s*(?:row|item|d|r)\.(sold_date|created_at|updated_at|start_date|end_date|period|month|year_month|\w+_date|\w+_at)", script):
            # Check if it's inside a format call (look backwards ~30 chars)
            start = max(0, match.start() - 40)
            context = script[start:match.start()]
            if not re.search(r'format(Date|DateTime|DateTimeFull|DateShort|Period|LastUpdated)\(', context):
                unformatted.append(match.group(1))
        if unformatted:
            unique_fields = list(set(unformatted))[:5]
            errors.append(f'RAW DATE LEAK: date fields used without formatDate/formatDateTime: {unique_fields}. Wrap in formatDate() or formatDateTime()')

# === RESULTS ===
print("=" * 60)
print("ARTIFACT VALIDATION REPORT")
print("=" * 60)
print(f"Errors: {len(errors)}")
print(f"Warnings: {len(warnings)}")
print()

if errors:
    print("ERRORS (must fix before create_artifact):")
    for i, e in enumerate(errors, 1):
        print(f"  {i}. {e}")
    print()

if warnings:
    print("WARNINGS (review before create_artifact):")
    for i, w in enumerate(warnings, 1):
        print(f"  {i}. {w}")
    print()

if not errors and not warnings:
    print("ALL CHECKS PASSED — artifact is ready for create_artifact")
elif not errors:
    print("No critical errors — artifact can proceed with create_artifact")
else:
    print("BLOCKED: Fix errors before calling create_artifact")
    sys.exit(1)
VALIDEOF
```

**Replace `ARTIFACT_PATH` with the actual file path** (Linux VM path, e.g. `/sessions/relaxed-jolly-cannon/mnt/Workspace/sales-overview-dashboard.html`).

### 12B — Validation Decision Table

| Result | Action |
|--------|--------|
| 0 errors, 0 warnings | Proceed to `create_artifact` immediately |
| 0 errors, N warnings | Review warnings, fix if relevant, then proceed |
| 1+ errors | Fix ALL errors before calling `create_artifact`. Show the error list to the user. |

### 12C — Post-Create Verification (after `create_artifact`)

After `create_artifact` returns success, run a quick smoke check:

```bash
# Verify artifact HTML file still exists and is > 5KB
python3 -c "
import os
path = 'ARTIFACT_PATH'
size = os.path.getsize(path)
if size < 5000:
    print(f'WARNING: Artifact file is only {size} bytes — may be truncated')
else:
    print(f'OK: Artifact file OK: {size} bytes')
"
```

### 12D — Common Validation Failures and Fixes

| Error Pattern | Root Cause | Fix |
|---------------|------------|-----|
| `{query: ...}` in callSql | Subagent or manual error used wrong param name | Replace `{query: q1}` with `{sql: q1}` everywhere |
| Missing `tryLoadCache()` | Section 7 cache not implemented | Copy the 3 cache functions from Section 7 |
| `saveCache()` after `renderAll()` | Order reversed | Swap the two lines in `loadData()` |
| `const` / `let` found | ES6 syntax leaked in | Replace with `var` |
| Missing `id="debugBox"` | Debug box HTML omitted | Add `<div class="debug-box" id="debugBox"></div>` |
| Hard-coded dates in SQL | Static dates instead of `getDateRange()` | Use `dr.fy27Start` / `dr.fy27End` variables |
| `window.addEventListener` with load | Auto-execute pattern from template | Remove, use cache-init block pattern |
| **RAW DATE LEAK** (`row.sold_date` without format) | Date field used directly in innerHTML/textContent | Wrap with `formatDate(row.sold_date)` or `formatDateTime(row.created_at)` — see Section 4 Rendering Guard |

---

## 13. Updated Checklist (23 items — was 19, added validation + date formatting items)

1. Step 0: AskUserQuestion - ask chat reply or artifact first
2. Step 0B: Clarify if needed - if request ambiguous, ask more
3. Step 0C: Complexity Gate - check >=4 dimensions? >=3 skills? >=5 queries? -> split artifacts
4. Pick right mcg-sales-agent skill - get KPI formulas + business rules
5. Dynamic date range - getDateRange() never hard-code
6. Split queries small - <=1 month scope per query - JS merge (especially FY27/FY26 separate)
7. Max 4 queries per artifact - more = split
8. callMcpWithTimeout - Promise.race 25s - never Promise.all
9. localStorage cache (Section 7) - **MANDATORY**: CACHE_KEY, getDateKey, tryLoadCache, saveCache, cache-init block, NO auto-load, saveCache BEFORE renderAll
10. Debug box - dlog() every step
11. ES5 only - var + function - never const/let/arrow
12. callSql() - structuredContent, JSON array, NDJSON
13. fmt() / pctStr() / yoyPct() / formatDate() / formatDateTime() / formatPeriod() / formatLastUpdated()
14. **Date/DateTime formatting (Section 4)** — NEVER show raw ISO dates to user, use Buddhist Era formatted output
15. Chart.js - destroy -> setTimeout 200ms -> recreate
16. CSS - Section 9 base template
17. Refresh button - disabled while loading, show "(cached)" label when from cache
18. Cache init block - tryLoadCache() first, placeholder if no cache, NEVER auto-call loadData()
19. Never share file path inside artifact - artifact only
20. Naming convention - if multiple artifacts, use consistent prefix
21. **Pre-Create Validation (Step 12A)** — run validation script, fix ALL errors before create_artifact
22. **Post-Create Verification (Step 12C)** — verify file size > 5KB, confirm artifact registered
23. **MCP param check** — verify `{sql: ...}` not `{query: ...}` in callSql calls