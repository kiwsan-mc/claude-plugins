---
name: "email-template"
description: "MC Group dark-theme email template — use when sending any report or notification email via Outlook. Applies the standard dark theme (Tahoma, #2e2e2e background, responsive design) with header/body/footer structure. Triggers: \"send email\", \"ส่งเมล\", \"email report\", \"send report via email\", \"outlook\"."
---

# MC Group Email Template

Use this HTML template whenever sending emails via `mcp__ms-outlook__outlook_send_mail`.
The template supports both **Light Mode** (default) and **Dark Mode** (via `@media (prefers-color-scheme: dark)` for OWA/browser clients).

## Design Strategy: Light-first with Dark Override

1. **Default (light mode)**: Inline styles set light colors — white backgrounds, dark text. Works everywhere including Outlook desktop (Word renderer).
2. **Dark mode override**: `@media (prefers-color-scheme: dark)` in `<style>` swaps backgrounds to dark and text to light. Works in OWA, webmail, and modern email clients.
3. **Outlook desktop**: Ignores `@media` queries — renders the light mode version, which is clean and professional on both.

## Template Rules

1. **Always minify** to a single line (replace newlines with spaces) before pasting into the `body` parameter to avoid JSON parsing issues
2. **Replace `{{PLACEHOLDER}}`** values with actual dynamic content before sending
3. **Font:** Tahoma throughout, base size 10pt (size 2)
4. **Outlook MCP:** always set `html: true`
5. Keep subject concise with key metric in it
6. Use `&#x0E3F;` HTML entity instead of literal ฿ character
7. **VML for Outlook**: Use `<!--[if mso]>` conditional comments for Outlook-specific fixes when needed

## Color Scheme

### Light Mode (default inline styles)
| Element | Color | Hex |
|---------|-------|-----|
| Page bg | Light gray | `#f5f5f5` |
| Container bg | White | `#ffffff` |
| Header bg | Slate blue | `#2c3e50` |
| Table header bg | `#2c3e50` |
| Table row bg (even) | `#fafafa` |
| Text | Dark | `#333333` |
| Header text | White | `#ffffff` |
| Subtitle | `#bdc3c7` |
| Green (positive) | `#27ae60` |
| Red (negative) | `#e74c3c` |
| Yellow (warning) | `#e67e22` |
| Blue (info) | `#2980b9` |
| Footer text | `#888888` |
| Border | `#e0e0e0` |

### Dark Mode (via @media)
| Element | Color | Hex |
|---------|-------|-----|
| Page bg | `#1a1a1a` |
| Container bg | `#222222` |
| Table header bg | `#333333` |
| Table row bg (even) | `#2a2a2a` |
| Text | `#e0e0e0` |
| Border | `#444444` |

### Info Box Colors (same in both modes — tinted backgrounds)
- Headline: light bg `#eafaf1`, dark bg `#1a3a2a`, border `#27ae60`
- Blue: light bg `#eaf2f8`, dark bg `#1a2a3a`, border `#2980b9`
- Red: light bg `#fdedec`, dark bg `#3a1a1a`, border `#e74c3c`
- Action: light bg `#fef9e7`, dark bg `#3a3520`, border `#e67e22`

## The Template (Skeleton)

### Full Master Template

Replace `{{PLACEHOLDER}}` text with actual content, then minify (remove newlines) before sending.

```html
<div class="XbIp4 jmmB7 customScrollBar GNqVo allowTextSelection"><div tabindex="0" aria-label="{{REPORT_LABEL}}" role="document" aria-live="polite" aria-atomic="false" class="BIZfh" id="UniqueMessageBody_14"><div visibility="visible"><style type="text/css">
.rps_6972 > div, .rps_6972 table, .rps_6972 td, .rps_6972 a {}
.rps_6972 table, .rps_6972 td {}
.rps_6972 img {border:0;height:auto;line-height:100%;outline:none;text-decoration:none}
@media only screen and (max-width: 680px) {
.rps_6972 .x_email-container {width:100%!important;max-width:100%!important}
.rps_6972 .x_email-body-padding {padding:20px 16px!important}
.rps_6972 .x_email-header-padding {padding:16px 16px!important}
.rps_6972 .x_email-footer-padding {padding:12px 16px!important}
.rps_6972 .x_email-header-title {font-size:16px!important}
.rps_6972 .x_info-box-padding {padding:12px 14px!important}
.rps_6972 .x_kpi-table th, .rps_6972 .x_kpi-table td {font-size:10px!important;padding:4px 5px!important}
}
@media only screen and (max-width: 480px) {
.rps_6972 .x_email-body-padding {padding:16px 12px!important}
.rps_6972 .x_email-header-padding {padding:14px 12px!important}
.rps_6972 .x_email-footer-padding {padding:10px 12px!important}
.rps_6972 .x_email-header-title {font-size:15px!important}
.rps_6972 .x_email-header-subtitle {font-size:12px!important}
.rps_6972 .x_email-text {font-size:11px!important}
.rps_6972 .x_info-box-padding {padding:10px 12px!important}
.rps_6972 .x_kpi-table th, .rps_6972 .x_kpi-table td {font-size:9px!important;padding:3px 4px!important}
}
@media (prefers-color-scheme: dark) {
.rps_6972 .x_page-bg {background-color:#1a1a1a!important}
.rps_6972 .x_container-bg {background-color:#222222!important}
.rps_6972 .x_table-header {background-color:#333333!important}
.rps_6972 .x_row-even {background-color:#2a2a2a!important}
.rps_6972 .x_text {color:#e0e0e0!important}
.rps_6972 .x_text-light {color:#cccccc!important}
.rps_6972 .x_border {border-color:#444444!important}
.rps_6972 .x_hr {border-color:#555555!important;color:#888888!important}
/* Dark mode info boxes */
.rps_6972 .x_headline-bg {background-color:#1a3a2a!important}
.rps_6972 .x_blue-bg {background-color:#1a2a3a!important}
.rps_6972 .x_red-bg {background-color:#3a1a1a!important}
.rps_6972 .x_action-bg {background-color:#3a3520!important}
}
</style><div class="rps_6972"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" class="x_page-bg" style="background-color:#f5f5f5;padding:20px 0"><tbody><tr><td align="center"><table role="presentation" class="x_email-container x_container-bg" width="680" cellpadding="0" cellspacing="0" border="0" style="background-color:#ffffff;max-width:680px;width:100%"><tbody>
<!-- HEADER -->
<tr><td class="x_email-header-padding" style="background-color:#2c3e50;padding:20px 32px">
<h1 class="x_email-header-title" style="margin:0;font-family:Tahoma,Geneva,sans-serif;font-size:18px;font-weight:bold;color:#ffffff">{{HEADER_TITLE}}</h1>
<p class="x_email-header-subtitle" style="margin:4px 0 0 0;font-family:Tahoma,Geneva,sans-serif;font-size:13px;color:#bdc3c7">{{HEADER_SUBTITLE}}</p>
</td></tr>
<!-- BODY -->
<tr><td class="x_email-body-padding" style="padding:28px 32px">
{{BODY_CONTENT}}
</td></tr>
<!-- FOOTER -->
<tr><td class="x_email-footer-padding" style="background-color:#fafafa;padding:14px 32px;border-top:1px solid #e0e0e0">
<p class="x_email-text x_text" style="font-family:Tahoma,Geneva,sans-serif;font-size:10px;color:#888888;margin:0;text-align:center">{{FOOTER_TEXT}}</p>
</td></tr>
</tbody></table></td></tr></tbody></table></div></div></div></div></div></div>
```

## Reusable Components (insert into `{{BODY_CONTENT}}`)

### Headline Box
```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:20px"><tbody><tr>
<td class="x_info-box-padding x_headline-bg" style="background-color:#eafaf1;border-left:3px solid #27ae60;padding:14px 18px">
<p class="x_email-text x_text" style="font-family:Tahoma,Geneva,sans-serif;font-size:13px;color:#333333;margin:0"><strong style="color:#27ae60">{{HEADLINE_TEXT}}</strong></p>
</td></tr></tbody></table>
```

### Section Title
```html
<p class="x_email-text x_text" style="font-family:Tahoma,Geneva,sans-serif;font-size:13px;color:#333333;margin:0 0 8px 0;font-weight:bold">{{SECTION_TITLE}}</p>
```

### Table (full)
```html
<table role="presentation" class="x_kpi-table" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:20px">
<thead><tr class="x_table-header" style="background-color:#2c3e50">
{{TH_CELLS}}
</tr></thead>
<tbody>
{{TABLE_ROWS}}
</tbody></table>
```

### TH Cell
```html
<th class="x_email-text" style="font-family:Tahoma,Geneva,sans-serif;font-size:11px;color:#ffffff;padding:8px 10px;text-align:left;font-weight:bold;border-bottom:2px solid #1a252f">{{COL_LABEL}}</th>
```

### TR (even row)
```html
<tr class="x_row-even" style="background-color:#fafafa">
{{TD_CELLS}}
</tr>
```

### TR (odd row)
```html
<tr>
{{TD_CELLS}}
</tr>
```

### TD Cell (normal)
```html
<td class="x_email-text x_text" style="font-family:Tahoma,Geneva,sans-serif;font-size:11px;color:#333333;padding:7px 10px;border-bottom:1px solid #e0e0e0">{{VALUE}}</td>
```

### TD Cell (green)
```html
<td class="x_email-text x_text" style="font-family:Tahoma,Geneva,sans-serif;font-size:11px;color:#27ae60;padding:7px 10px;border-bottom:1px solid #e0e0e0;font-weight:bold">{{VALUE}}</td>
```

### TD Cell (red)
Use `color:#e74c3c` with `font-weight:bold`

### TD Cell (yellow)
Use `color:#e67e22` with `font-weight:bold`

### TD Cell (bold label)
Add `font-weight:bold` to style

### Green Takeaway Box
```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:12px"><tbody><tr>
<td class="x_info-box-padding x_headline-bg" style="background-color:#eafaf1;border-left:3px solid #27ae60;padding:10px 14px">
<p class="x_email-text x_text" style="font-family:Tahoma,Geneva,sans-serif;font-size:11px;color:#333333;margin:0"><strong style="color:#27ae60">{{TAKEAWAY_NUMBER}}. {{TAKEAWAY_TITLE}}</strong> {{TAKEAWAY_DETAIL}}</p>
</td></tr></tbody></table>
```

### Blue Takeaway Box
```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:12px"><tbody><tr>
<td class="x_info-box-padding x_blue-bg" style="background-color:#eaf2f8;border-left:3px solid #2980b9;padding:10px 14px">
<p class="x_email-text x_text" style="font-family:Tahoma,Geneva,sans-serif;font-size:11px;color:#333333;margin:0"><strong style="color:#2980b9">{{TAKEAWAY_NUMBER}}. {{TAKEAWAY_TITLE}}</strong> {{TAKEAWAY_DETAIL}}</p>
</td></tr></tbody></table>
```

### Red Takeaway Box
```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:12px"><tbody><tr>
<td class="x_info-box-padding x_red-bg" style="background-color:#fdedec;border-left:3px solid #e74c3c;padding:10px 14px">
<p class="x_email-text x_text" style="font-family:Tahoma,Geneva,sans-serif;font-size:11px;color:#333333;margin:0"><strong style="color:#e74c3c">{{TAKEAWAY_NUMBER}}. {{TAKEAWAY_TITLE}}</strong> {{TAKEAWAY_DETAIL}}</p>
</td></tr></tbody></table>
```

### Action Items Box
```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:20px"><tbody><tr>
<td class="x_info-box-padding x_action-bg" style="background-color:#fef9e7;border-left:3px solid #e67e22;padding:12px 16px">
<ul style="margin:0;padding:0 0 0 18px;list-style-type:disc">
{{ACTION_ITEMS}}
</ul>
</td></tr></tbody></table>
```

### Action Item
```html
<li class="x_email-text x_text" style="font-family:Tahoma,Geneva,sans-serif;font-size:11px;color:#333333;margin-bottom:6px">{{ACTION_TEXT}}</li>
```

### Divider
```html
<hr class="x_hr" style="border-width:1px medium medium;border-style:solid none none;border-color:#e0e0e0;margin:20px 0;color:#888888">
```

### Data Footer
```html
<p class="x_email-text x_text-light" style="font-family:Tahoma,Geneva,sans-serif;font-size:11px;color:#888888;margin:0 0 4px 0">{{DATA_SOURCE}}</p>
```

## Sending Steps

1. Build the HTML by replacing all `{{PLACEHOLDER}}` values
2. Minify: remove all newlines (replace with spaces), collapse multiple spaces
3. Call `mcp__ms-outlook__outlook_send_mail` with `html: true`, `to`, `subject`, and the minified `body`
4. Use the user's Outlook address from `mcp__ms-outlook__outlook_whoami`
5. Set `importance: "normal"` unless urgent

## How Light/Dark Works

| Client | Renders | How |
|--------|---------|-----|
| Outlook Desktop (Windows) | Light Mode | Reads inline styles, ignores `@media` |
| OWA (browser) | Follows OS setting | `@media (prefers-color-scheme: dark)` overrides |
| Outlook Mobile (iOS/Android) | Follows OS setting | Supports `@media` in WebView |
| Gmail / Webmail | Follows OS setting | Supports `@media` fully |

The `class` attributes (like `x_page-bg`, `x_text`, `x_headline-bg`) are only used in the `@media (dark)` block — Outlook desktop ignores classes without matching `[class]` selectors, so there's no conflict.
