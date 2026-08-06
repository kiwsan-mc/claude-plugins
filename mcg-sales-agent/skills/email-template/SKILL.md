---
name: "email-template"
description: "MC Group email template — use when sending any report or notification email via Outlook. Applies the standard MC Group theme (Tahoma, #2c3e50 header, responsive design) with header/body/footer structure. Triggers: \"send email\", \"ส่งเมล\", \"email report\", \"send report via email\", \"outlook\"."
---

# MC Group Email Template

Use this HTML template whenever sending emails via `mcp__ms-outlook__outlook_send_mail`.
Based on MC Group's production email template (DailySalesReport.cshtml).

## Design Strategy

1. **Light mode only** with clean inline styles — white backgrounds, dark text. Works everywhere including Outlook desktop (Word renderer).
2. **Responsive** via `@media` breakpoints at 680px and 480px.
3. **MSO conditionals** for Outlook-specific pixel density settings.
4. **Table-based layout** for maximum email client compatibility.

## Template Rules

1. **Always minify** to a single line (replace newlines with spaces) before pasting into the `body` parameter to avoid JSON parsing issues
2. **Replace `{{PLACEHOLDER}}`** values with actual dynamic content before sending
3. **Font:** Tahoma throughout, base size 13px for body text
4. **Outlook MCP:** always set `html: true`
5. Keep subject concise with key metric in it
6. Use `&#x0E3F;` HTML entity instead of literal ฿ character
7. **VML for Outlook**: Use `<!--[if mso]>` conditional comments for Outlook-specific fixes

## Color Scheme

| Element | Color | Hex |
|---------|-------|-----|
| Page bg | Light gray | `#f5f5f5` |
| Container bg | White | `#ffffff` |
| Header bg | Slate blue | `#2c3e50` |
| Header text | White | `#ffffff` |
| Header subtitle | Light gray | `#bdc3c7` |
| Body text | Dark | `#222222` |
| Secondary text | `#333333` |
| Info box bg | `#f9f9f9` |
| Info box border | `#2c3e50` |
| Warning box bg | `#fef9e7` |
| Warning box border | `#f39c12` |
| Warning text | `#7d6608` |
| Green (positive) | `#27ae60` |
| Red (negative) | `#e74c3c` |
| Yellow (warning) | `#e67e22` |
| Blue (info/link) | `#0563C1` |
| Footer bg | `#f9f9f9` |
| Footer text | `#888888` |
| Footer border | `#eeeeee` |
| Divider | `#e0e0e0` |
| Table header bg | `#2c3e50` |
| Table header text | `#ffffff` |
| Table row bg (even) | `#fafafa` |
| Table border | `#e0e0e0` |

## The Template (Full Master)

Replace `{{PLACEHOLDER}}` text with actual content, then minify (remove newlines) before sending.

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<title>{{EMAIL_TITLE}}</title>
<!--[if mso]>
<noscript>
<xml>
<o:OfficeDocumentSettings>
<o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings>
</xml>
</noscript>
<![endif]-->
<style type="text/css">
body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
img { -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }
@media only screen and (max-width: 680px) {
.email-container { width: 100% !important; max-width: 100% !important; }
.email-body-padding { padding: 20px 16px !important; }
.email-header-padding { padding: 16px 16px !important; }
.email-footer-padding { padding: 12px 16px !important; }
.email-header-title { font-size: 16px !important; }
.info-box-padding { padding: 12px 14px !important; }
.kpi-table th, .kpi-table td { font-size: 10px !important; padding: 4px 5px !important; }
}
@media only screen and (max-width: 480px) {
.email-body-padding { padding: 16px 12px !important; }
.email-header-padding { padding: 14px 12px !important; }
.email-footer-padding { padding: 10px 12px !important; }
.email-header-title { font-size: 15px !important; }
.email-header-subtitle { font-size: 12px !important; }
.email-text { font-size: 12px !important; }
.info-box-padding { padding: 10px 12px !important; }
.kpi-table th, .kpi-table td { font-size: 9px !important; padding: 3px 4px !important; }
}
</style>
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: Tahoma, Geneva, sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f5f5f5; padding: 20px 0;">
<tr>
<td align="center">
<table role="presentation" class="email-container" width="680" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; max-width: 680px; width: 100%;">

<!-- HEADER -->
<tr>
<td class="email-header-padding" style="background-color: #2c3e50; padding: 20px 32px;">
<h1 class="email-header-title" style="margin: 0; font-family: Tahoma, Geneva, sans-serif; font-size: 18px; font-weight: bold; color: #ffffff;">{{HEADER_TITLE}}</h1>
<p class="email-header-subtitle" style="margin: 4px 0 0 0; font-family: Tahoma, Geneva, sans-serif; font-size: 13px; color: #bdc3c7;">{{HEADER_SUBTITLE}}</p>
</td>
</tr>

<!-- BODY -->
<tr>
<td class="email-body-padding" style="padding: 28px 32px;">
{{BODY_CONTENT}}
</td>
</tr>

<!-- FOOTER -->
<tr>
<td class="email-footer-padding" style="background-color: #f9f9f9; padding: 14px 32px; border-top: 1px solid #eeeeee;">
<p class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 11px; color: #888888; margin: 0; text-align: center;">This is an automated email from MC Group PCL. Please do not reply directly to this message.</p>
</td>
</tr>

</table>
</td>
</tr>
</table>
</body>
</html>
```

## Reusable Components (insert into `{{BODY_CONTENT}}`)

### Greeting
```html
<p class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 13px; color: #222222; margin: 0 0 18px 0;">เรียน ทุกท่าน,</p>
```

### Info Box (slate border)
```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 20px;">
<tr>
<td class="info-box-padding" style="background-color: #f9f9f9; border-left: 3px solid #2c3e50; padding: 14px 18px;">
<p class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 13px; color: #222222; margin: 0 0 8px 0; font-weight: bold;">{{INFO_TITLE}}</p>
<ul style="margin: 0; padding: 0 0 0 20px; list-style-type: disc;">
<li class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 13px; color: #333333; margin-bottom: 4px;">{{ITEM_1}}</li>
<li class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 13px; color: #333333;">{{ITEM_2}}</li>
</ul>
</td>
</tr>
</table>
```

### Warning Box (yellow border)
```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 20px;">
<tr>
<td class="info-box-padding" style="background-color: #fef9e7; border-left: 3px solid #f39c12; padding: 10px 14px;">
<p class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 13px; color: #7d6608; margin: 0;">{{WARNING_TEXT}}</p>
</td>
</tr>
</table>
```

### Success Box (green border)
```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 20px;">
<tr>
<td class="info-box-padding" style="background-color: #eafaf1; border-left: 3px solid #27ae60; padding: 10px 14px;">
<p class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 13px; color: #1e8449; margin: 0;"><strong style="color: #27ae60;">{{SUCCESS_TEXT}}</strong></p>
</td>
</tr>
</table>
```

### Error Box (red border)
```html
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 20px;">
<tr>
<td class="info-box-padding" style="background-color: #fdedec; border-left: 3px solid #e74c3c; padding: 10px 14px;">
<p class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 13px; color: #922b21; margin: 0;"><strong style="color: #e74c3c;">{{ERROR_TEXT}}</strong></p>
</td>
</tr>
</table>
```

### Section Title
```html
<p class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 13px; color: #222222; margin: 0 0 8px 0; font-weight: bold;">{{SECTION_TITLE}}</p>
```

### Body Text
```html
<p class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 13px; color: #333333; margin: 0 0 20px 0; line-height: 1.6;">{{TEXT_CONTENT}}</p>
```

### Link
```html
<a href="mailto:{{EMAIL}}" style="color: #0563C1; text-decoration: underline;">{{DISPLAY_TEXT}}</a>
```

### Table (full)
```html
<table role="presentation" class="kpi-table" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 20px;">
<thead>
<tr style="background-color: #2c3e50;">
{{TH_CELLS}}
</tr>
</thead>
<tbody>
{{TABLE_ROWS}}
</tbody>
</table>
```

### TH Cell
```html
<th class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 11px; color: #ffffff; padding: 8px 10px; text-align: left; font-weight: bold; border-bottom: 2px solid #1a252f;">{{COL_LABEL}}</th>
```

### TR (odd row)
```html
<tr>{{TD_CELLS}}</tr>
```

### TR (even row)
```html
<tr style="background-color: #fafafa;">{{TD_CELLS}}</tr>
```

### TD Cell (normal)
```html
<td class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 11px; color: #333333; padding: 7px 10px; border-bottom: 1px solid #e0e0e0;">{{VALUE}}</td>
```

### TD Cell (green/positive)
```html
<td class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 11px; color: #27ae60; padding: 7px 10px; border-bottom: 1px solid #e0e0e0; font-weight: bold;">{{VALUE}}</td>
```

### TD Cell (red/negative)
```html
<td class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 11px; color: #e74c3c; padding: 7px 10px; border-bottom: 1px solid #e0e0e0; font-weight: bold;">{{VALUE}}</td>
```

### TD Cell (yellow/warning)
```html
<td class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 11px; color: #e67e22; padding: 7px 10px; border-bottom: 1px solid #e0e0e0; font-weight: bold;">{{VALUE}}</td>
```

### TD Cell (bold label)
```html
<td class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 11px; color: #222222; padding: 7px 10px; border-bottom: 1px solid #e0e0e0; font-weight: bold;">{{VALUE}}</td>
```

### Divider
```html
<hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;" />
```

### Signature
```html
<p class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 13px; color: #222222; margin: 0;">Best Regards,</p>
<p class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 13px; color: #222222; margin: 4px 0 0 0; font-weight: bold;">{{TEAM_NAME}}</p>
```

### Help/Contact Line
```html
<p class="email-text" style="font-family: Tahoma, Geneva, sans-serif; font-size: 13px; color: #333333; margin: 0 0 20px 0; line-height: 1.6;">หากพบข้อผิดพลาดของข้อมูลหรือต้องการความช่วยเหลือเพิ่มเติม กรุณาเขียนรายละเอียดและส่งอีเมลแจ้งเรามาที่ <a href="mailto:it-helpdesk@mcgroupnet.com" style="color: #0563C1; text-decoration: underline;">it-helpdesk&#64;mcgroupnet.com</a></p>
```

## Sending Steps

1. Build the HTML by replacing all `{{PLACEHOLDER}}` values
2. Minify: remove all newlines (replace with spaces), collapse multiple spaces
3. Call `mcp__ms-outlook__outlook_send_mail` with `html: true`, `to`, `subject`, and the minified `body`
4. Use the user's Outlook address from `mcp__ms-outlook__outlook_whoami`
5. Set `importance: "normal"` unless urgent

## Compatibility

| Client | Renders | Notes |
|--------|---------|-------|
| Outlook Desktop (Windows) | Full support | Uses Word renderer, reads inline styles + MSO conditionals |
| OWA (browser) | Full support | Reads inline styles + `<style>` block |
| Outlook Mobile (iOS/Android) | Full support | Responsive via `@media` breakpoints |
| Gmail / Webmail | Full support | Inline styles work everywhere |
