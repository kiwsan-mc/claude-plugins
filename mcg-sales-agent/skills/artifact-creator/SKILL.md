---
name: "artifact-creator-v2"
description: "[v2] Use this skill whenever creating Cowork artifacts for MC Group sales dashboards. Mandatory localStorage cache pattern prevents unwanted permission popups. Includes complete code templates for all 11 sections: callMcpWithTimeout, query splitting (FY27/FY26 separate), dateKey cache, Chart.js, CSS, debug box, and troubleshooting table."
---

# Artifact Creator - Technical Patterns (v2)

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

## 4. Date Formatting (Thai Buddhist Era)

```javascript
function formatDate(d) {
    if (!d) return '-';
    var s = String(d).replace('T00:00:00Z','').replace('T00:00:00','');
    var parts = s.split('-');
    if (parts.length === 3) {
      var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      return parts[2] + ' ' + months[parseInt(parts[1])-1] + ' ' + (parseInt(parts[0])+543);
    }
    return s;
}
```

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
| Chart not rendering | Chart created before DOM ready | Use `setTimeout(function(){...}, 200)` after `innerHTML` |
| "window.cowork.callMcpTool not available" | Artifact opened outside Cowork | Show friendly message, artifact only works in Cowork sidebar |
| Cache not saving | `saveCache()` called AFTER `renderAll()` which modified data | Move `saveCache(results)` BEFORE `renderAll(results)` |

---

## 11. Checklist: Building a New Artifact (19 items)

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
13. fmt() / pctStr() / yoyPct() / formatDate()
14. Chart.js - destroy -> setTimeout 200ms -> recreate
15. CSS - Section 9 base template
16. Refresh button - disabled while loading, show "(cached)" label when from cache
17. Cache init block - tryLoadCache() first, placeholder if no cache, NEVER auto-call loadData()
18. Never share file path inside artifact - artifact only
19. Naming convention - if multiple artifacts, use consistent prefix
