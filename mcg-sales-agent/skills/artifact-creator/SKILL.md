---
name: "artifact-creator"
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
3. Use mcp__mcg-toolbox__sales_agent with query patterns from the skill
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
// Format date (date only) — Gregorian (CE)
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
 
// Format datetime — Gregorian (CE) + time (HH:mm)
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
| Table column "Sold Date" | `formatDate(row.sold_date)` | `05 Aug 2026` |
| Table column with tight space | `formatDateShort(row.sold_date)` | `05 Aug 26` |
| Header "Last Updated" | `formatLastUpdated()` | `05 Aug 2026 14:30` |
| Header "Data Period" | `formatDate(dr.fy27Start) + ' - ' + formatDate(dr.fy27End)` | `01 Jul 2026 - 04 Aug 2026` |
| Chart X-axis (monthly) | `formatPeriod(row.month)` | `Aug 2026` |
| Debug log timestamps | `formatDateTimeFull(row.created_at)` | `05 Aug 2026 14:30:45` |
| Footer "Data as of" | `formatLastUpdated()` | `05 Aug 2026 14:30` |
 
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
 
## 9. CSS Base Template — Fashion Island Clean Style
 
Use this clean white-card layout instead of the old dark header (`#2c3e50`) style.
All artifacts MUST use this template going forward.
 
```css
:root { color-scheme: light }
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: Tahoma, 'Segoe UI', system-ui, sans-serif;
  background: #f0f1f3; color: #1a1a1a;
  padding: 24px; max-width: 1400px; margin: 0 auto;
}
 
/* ── Top Bar ── */
.top-bar {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px;
}
.top-bar h1 { font-size: 1.5rem; font-weight: 700; }
.top-bar .sub { font-size: 0.8rem; color: #777; margin-left: 8px; font-weight: 400; }
 
/* ── Refresh Button ── */
.btn-live {
  background: #2563eb; color: white;
  border: none; padding: 8px 16px; border-radius: 6px;
  cursor: pointer; font-family: Tahoma, sans-serif;
  font-size: 0.8rem; font-weight: 600;
}
.btn-live:hover { background: #1d4ed8; }
.btn-live:disabled { background: #bdc3c7; cursor: not-allowed; }
.btn-refresh {
  background: #f0f1f3; color: #555;
  border: 1px solid #ddd; padding: 6px 14px; border-radius: 6px;
  cursor: pointer; font-family: Tahoma, sans-serif; font-size: 0.8rem;
}
.status-bar {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.75rem; color: #999;
}
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.dot.live { background: #16a34a; }
.dot.cached { background: #f59e0b; }
 
/* ── Summary KPI Strip (top-level big numbers) ── */
.summary-strip {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px; margin-bottom: 20px;
}
.summary-card {
  background: white; border-radius: 12px; padding: 18px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06); text-align: center;
}
.summary-card .lbl { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }
.summary-card .val { font-size: 1.8rem; font-weight: 700; margin: 4px 0; }
.summary-card .chg { font-size: 0.8rem; font-weight: 600; }
.chg.up { color: #16a34a; }
.chg.down { color: #dc2626; }
.chg.flat { color: #95a5a6; }
 
/* ── Branch / Dimension Card Grid ── */
.card-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px; margin-bottom: 20px;
  align-items: start;   /* ← prevent vertical stretch — all cards top-align */
}
.card {
  background: white; border-radius: 12px; padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  border-top: 4px solid #2563eb; /* ← colored accent bar */
}
/* Card accent colors — assign via JS based on data */
.card.accent-green  { border-top-color: #16a34a; }
.card.accent-blue   { border-top-color: #2563eb; }
.card.accent-red    { border-top-color: #dc2626; }
.card.accent-orange { border-top-color: #f59e0b; }
.card .card-title { font-size: 0.9rem; font-weight: 700; margin-bottom: 10px; }
.card .card-code  { font-size: 0.7rem; color: #999; font-weight: 400; }
 
/* ── KPI Tiles inside Cards — uniform height ── */
.kpi-row {
  display: grid; grid-template-columns: 1fr 1fr; gap: 6px;
}
.kpi-tile {
  padding: 6px 8px; background: #fafafa; border-radius: 8px;
  display: flex; flex-direction: column; justify-content: flex-start;
  min-height: 64px;   /* ← all tiles same height */
}
.kpi-tile .k { font-size: 0.68rem; color: #888; margin-bottom: 2px; }
.kpi-tile .v { font-size: 0.95rem; font-weight: 700; margin-bottom: 2px; }
.kpi-tile .c { font-size: 0.7rem; font-weight: 600; }
.kpi-tile .c.up { color: #16a34a; }
.kpi-tile .c.down { color: #dc2626; }
.kpi-tile .c.flat { color: #95a5a6; }
 
/* ── Chart & Table Sections ── */
.chart-row { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; margin-bottom: 16px; }
.chart-box {
  background: white; border-radius: 12px; padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.chart-box h3 { font-size: 0.85rem; color: #555; margin-bottom: 10px; font-weight: 600; }
.chart-box canvas { max-height: 300px; }
.table-box {
  background: white; border-radius: 12px; padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-bottom: 16px;
}
.table-box h3 { font-size: 0.85rem; color: #555; margin-bottom: 10px; font-weight: 600; }
 
/* ── Tables ── */
table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
th {
  background: #f8f8f8; text-align: left; padding: 8px 10px;
  font-size: 0.75rem; color: #666; font-weight: 600;
  border-bottom: 2px solid #eee;
}
td { padding: 8px 10px; border-bottom: 1px solid #f0f0f0; }
tr:hover td { background: #fafafa; }
.text-right { text-align: right; }
 
/* ── Insights / Recommendations ── */
.reco-box {
  background: white; border-radius: 12px; padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-bottom: 16px;
}
.reco-box h3 { font-size: 0.85rem; color: #555; margin-bottom: 8px; font-weight: 600; }
.reco-item { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 6px; font-size: 0.82rem; }
.tag {
  font-size: 0.65rem; padding: 2px 8px; border-radius: 4px;
  font-weight: 700; flex-shrink: 0; min-width: 44px; text-align: center;
}
.tag.red    { background: #fee2e2; color: #dc2626; }
.tag.yellow { background: #fef3c7; color: #d97706; }
.tag.green  { background: #dcfce7; color: #16a34a; }
 
/* ── Footer ── */
.footer { text-align: right; font-size: 0.7rem; color: #aaa; }
 
/* ── Debug Box ── */
.debug-box { margin-top:16px; padding:12px; background:#f8f9fa; border-radius:8px; font-size:11px; color:#666; max-height:200px; overflow-y:auto; font-family:monospace; display:none; }
```
 
### Usage: Building Card Grids with This Template
 
**Summary KPI Strip (top-level totals):**
```html
<div class="summary-strip">
  <div class="summary-card"><div class="lbl">LABEL</div><div class="val">VALUE</div><div class="chg up">▲ +XX%</div></div>
</div>
```
 
**Branch/Dimension Cards (3-column grid):**
```html
<div class="card-grid">
  <div class="card accent-green">
    <div class="card-title">NAME <span class="card-code">CODE</span></div>
    <div class="kpi-row">
      <div class="kpi-tile"><div class="k">KPI</div><div class="v">VAL</div><div class="c up">▲ +XX%</div></div>
      <!-- repeat for 4-6 KPIs per card -->
    </div>
  </div>
</div>
```
 
**Empty placeholder rule:** Use `&nbsp;` for KPI tiles with no change indicator — keeps uniform height:
```html
<div class="kpi-tile"><div class="k">% Share</div><div class="v">57%</div><div class="c">&nbsp;</div></div>
```
 
---
 
## 10. Known Issues and Troubleshooting Flow
 
| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Popup on open without clicking Refresh | Missing localStorage cache pattern | Implement Section 7 cache pattern |
| Silent timeout (>25s, no response) | Query scanning >3 months of data | Split FY27/FY26 into separate queries |
| "T00:00:00Z" in date displays | PostgreSQL date cast without formatting | Use `formatDate()` from Section 4 |
| Chart not rendering | Chart created before DOM ready | Use `setTimeout(function(){...}, 200)` |
| "window.cowork.callMcpTool not available" | Artifact opened outside Cowork | Show friendly message |
| Cache not saving | `saveCache()` called AFTER `renderAll()` | Move `saveCache(results)` BEFORE `renderAll(results)` |
 
---
 
## 11. Checklist: Building a New Artifact (20 items)
 
1. Step 0: AskUserQuestion - ask chat reply or artifact first
2. Step 0B: Clarify if needed - if request ambiguous, ask more
3. Step 0C: Complexity Gate
4. Pick right mcg-sales-agent skill
5. Dynamic date range - getDateRange()
6. Split queries small - <=1 month scope
7. Max 4 queries per artifact
8. callMcpWithTimeout - Promise.race 25s
9. localStorage cache - MANDATORY + NO auto-load
10. Debug box - dlog() every step
11. ES5 only - var + function
12. callSql() - structuredContent, JSON array, NDJSON
13. fmt() / pctStr() / yoyPct() / formatDate() / formatDateTime() / formatPeriod()
14. Date/DateTime formatting - NEVER raw ISO dates
15. Chart.js - destroy -> setTimeout 200ms -> recreate
16. CSS - Section 9 Fashion Island Clean Style
17. Refresh button - disabled while loading
18. Cache init block - tryLoadCache() first
19. Never share file path
20. Naming convention - consistent prefix
 
---
 
## 12. E2E Validation (before AND after create_artifact)
 
Run validation script (see full version in plugin) — checks:
- Structure: DOCTYPE, html tags, script tags
- DOM elements: refreshBtn, periodInfo, debugBox, summaryGrid, tablesArea
- JS functions: dlog, getDateKey, tryLoadCache, saveCache, fmt, yoyPct, callMcpWithTimeout, callSql, getDateRange, loadData, renderAll, fetchData
- ES5 compliance: no const/let/arrow
- callSql params: {sql: ...} NOT {query: ...}
- CACHE_KEY declared
- NO auto-load patterns (window.addEventListener, body onload)
- saveCache BEFORE renderAll
- Chart.js CDN if using charts
- debug-box CSS + dlog()
- light mode
- MCP tool names valid
- Hard-coded dates check
- Raw date leak check