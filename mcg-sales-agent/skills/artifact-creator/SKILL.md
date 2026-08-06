---
name: "artifact-creator"
description: "Use this skill whenever the user wants to create a live monitoring dashboard artifact (HTML artifact with MCP data fetching, localStorage cache, Chart.js charts, and pull-to-refresh button). Triggers when the user mentions \"create artifact\", \"monitor\", \"dashboard\", \"live artifact\", \"artifact creator\", or wants to create a persisted data dashboard in Cowork sidebar. For MC Group sales data, always use mcg-sales-agent skills first to get correct KPI formulas and business rules before building the artifact."
---

# Artifact Creator - Technical Patterns

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

fmt(n): if >=1e6 show X.XXM, if >=1e3 show X.XK, else locale string
pctStr(a,b): if !b return '-', else ((a-b)/b)*100 to 1 decimal + '%'

---

## 6. Chart.js - Destroy Before Recreate

var barInst = null, doughInst = null;
if (barInst) barInst.destroy();
barInst = new Chart(ctx, { ... });
Create charts in setTimeout(function() {...}, 200) after innerHTML

---

## 7. localStorage Cache + Auto-Invalidation (CRITICAL)

Use dateKey fingerprint - cross-day cache is auto-invalidated

---

## 8. Debug Box (MANDATORY)

Always include div.debug-box#debugBox + dlog() function

---

## 9-13. (CSS, UI Button, Scheduled Task, No Path, ES5)

Standard patterns as previously defined

---

## Known Issues and Troubleshooting Flow

5-step troubleshooting flow

---

## Checklist: Building a New Artifact (19 items)

1. Step 0: AskUserQuestion - ask chat reply or artifact first
2. Step 0B: Clarify if needed - if request ambiguous, ask more
3. Step 0C: Complexity Gate - check >=4 dimensions? >=3 skills? >=5 queries? -> split artifacts
4. Pick right mcg-sales-agent skill - get KPI formulas + business rules
5. Dynamic date range - getDateRange() never hard-code
6. Split queries small - <=1 month scope per query - JS merge
7. Max 4 queries per artifact - more = split
8. callMcpWithTimeout - Promise.race 25s - never Promise.all
9. cache dateKey - auto-invalidate cross-day
10. Debug box - dlog() every step
11. ES5 only - var + function - never const/let/arrow
12. callSql() - structuredContent, JSON array, NDJSON
13. fmt() / pctStr() / formatDate()
14. Chart.js - destroy -> setTimeout 200ms -> recreate
15. CSS - align-items: start + min-height
16. Refresh button - disabled while loading
17. Cache init - validate field + dateKey
18. Never share file path - artifact only
19. Naming convention - if multiple artifacts, use consistent prefix
