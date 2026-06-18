#!/usr/bin/env python3
"""
build_pdf.py — Generate airstream_deck.pdf from airstream_deck.html
"""

import re
import os
import subprocess
import sys

# ── 1. Read source HTML ────────────────────────────────────────────────────────
with open('/home/user/airstream-lead-distro-analysis/airstream_deck.html', 'r') as f:
    html = f.read()

# ── 2. SVG extraction helpers ─────────────────────────────────────────────────
def extract_svg(html, viewbox_w, viewbox_h, occurrence=0):
    pattern = rf'<svg[^>]*viewBox="0 0 {viewbox_w} {viewbox_h}".*?</svg>'
    matches = re.findall(pattern, html, re.DOTALL)
    if matches and occurrence < len(matches):
        return matches[occurrence]
    return (f'<svg viewBox="0 0 {viewbox_w} {viewbox_h}" xmlns="http://www.w3.org/2000/svg">'
            f'<text x="10" y="20" fill="red">SVG not found {viewbox_w}x{viewbox_h}</text></svg>')

def resize_svg(svg_str, width):
    svg_str = re.sub(r'\s+width="[^"]*"', '', svg_str)
    svg_str = re.sub(r'\s+height="[^"]*"', '', svg_str)
    svg_str = re.sub(r'<svg', f'<svg style="width:{width}px;height:auto;display:block"', svg_str, count=1)
    return svg_str

SVG_MONTHLY      = extract_svg(html, 780, 210)
SVG_SOURCE_DONUT = extract_svg(html, 200, 200)
SVG_SCORE        = extract_svg(html, 260, 180)
SVG_BRAND        = extract_svg(html, 200, 180)
SVG_SCENARIO     = extract_svg(html, 440, 220)
SVG_TIMELINE     = extract_svg(html, 560, 210)
SVG_S3RATE       = extract_svg(html, 220, 170)
SVG_SRCMIX       = extract_svg(html, 320, 170)
SVG_PERDEAL      = extract_svg(html, 240, 170)

# ── 3. Build print HTML ───────────────────────────────────────────────────────
CSS = """
@page { size: 16in 9in; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Helvetica, Arial, sans-serif; }
.page { width: 1536px; height: 864px; overflow: hidden; page-break-after: always; position: relative; }
.card  { background: #FFFFFF; border-radius: 8px; padding: 12px 14px; }
.card-dark { background: #243447; border-radius: 8px; padding: 12px 14px; }
.row  { display: table; width: 100%; border-spacing: 12px 0; }
.col  { display: table-cell; vertical-align: top; }
"""

# ─────────────────────────────── PAGE 1 ───────────────────────────────────────
PAGE1 = f"""
<div class="page" style="background:#1C2B3A; padding:60px 80px 48px;">
  <!-- gold left border -->
  <div style="position:absolute;left:0;top:0;bottom:0;width:6px;background:#C09B5E;"></div>

  <!-- top row -->
  <div style="display:table;width:100%;">
    <div style="display:table-cell;vertical-align:top;">
      <span style="color:#FFFFFF;font-weight:bold;letter-spacing:4px;font-size:13px;">AIRSTREAM</span>
    </div>
    <div style="display:table-cell;vertical-align:top;text-align:right;">
      <span style="color:#A8B4BC;font-size:12px;">01 / 04</span>
    </div>
  </div>

  <!-- eyebrow -->
  <div style="color:#C09B5E;font-size:13px;letter-spacing:3px;text-transform:uppercase;font-weight:600;margin-top:40px;">
    DEALER LEAD DISTRIBUTION
  </div>

  <!-- H1 -->
  <h1 style="color:#FFFFFF;font-size:42px;font-weight:bold;line-height:1.15;margin-top:12px;">
    Forecast vs. Actual Post-Launch Analysis
  </h1>

  <!-- gold divider -->
  <div style="width:44px;height:3px;background:#C09B5E;margin:20px 0;border-radius:2px;"></div>

  <!-- subtitle -->
  <div style="color:#A8B4BC;font-size:18px;">
    How did the new Airstream website change dealer lead volume?
  </div>

  <!-- KPI row -->
  <div style="display:table;width:100%;border-spacing:12px 0;margin-top:32px;table-layout:fixed;">
    <div style="display:table-cell;vertical-align:top;width:25%;">
      <div style="background:#243447;border-radius:8px;padding:20px;border:1px solid rgba(255,255,255,0.08);">
        <div style="color:#FFFFFF;font-size:32px;font-weight:bold;">249,981</div>
        <div style="color:#A8B4BC;font-size:12px;margin-top:6px;">Historical Leads (13-mo baseline)</div>
      </div>
    </div>
    <div style="display:table-cell;vertical-align:top;width:25%;">
      <div style="background:#243447;border-radius:8px;padding:20px;border:1px solid rgba(255,255,255,0.08);">
        <div style="color:#FFFFFF;font-size:32px;font-weight:bold;">~19,200</div>
        <div style="color:#A8B4BC;font-size:12px;margin-top:6px;">Avg Leads / Month</div>
      </div>
    </div>
    <div style="display:table-cell;vertical-align:top;width:25%;">
      <div style="background:#243447;border-radius:8px;padding:20px;border:1px solid rgba(255,255,255,0.08);">
        <div style="color:#FFFFFF;font-size:32px;font-weight:bold;">~17,900</div>
        <div style="color:#A8B4BC;font-size:12px;margin-top:6px;">Forecasted Monthly (&ndash;7%)</div>
      </div>
    </div>
    <div style="display:table-cell;vertical-align:top;width:25%;">
      <div style="background:#243447;border-radius:8px;padding:20px;border:1px solid #C0392B;">
        <div style="color:#C0392B;font-size:32px;font-weight:bold;">~12,026</div>
        <div style="color:#A8B4BC;font-size:12px;margin-top:6px;">June 2026 Pace (&ndash;37% vs baseline)</div>
      </div>
    </div>
  </div>

  <!-- meta row -->
  <div style="margin-top:24px;font-size:11px;color:#A8B4BC;">
    Website Launch: May 27 2026 &nbsp;&middot;&nbsp; Post-Launch Window: May 28 &ndash; June 18
    &nbsp;&middot;&nbsp; Baseline: Mar 2025 &ndash; May 2026 &nbsp;&middot;&nbsp; Dealers: 83
    &nbsp;&middot;&nbsp; Pipeline: HubSpot &rarr; Make &rarr; AIMBase &rarr; Dealers
  </div>

  <!-- footer -->
  <div style="position:absolute;bottom:30px;right:80px;font-size:11px;color:#5C6E7A;">
    Element Three &middot; Confidential
  </div>
</div>
"""

# ─────────────────────────────── PAGE 2 ───────────────────────────────────────
PAGE2 = f"""
<div class="page" style="background:#F4F6F7; padding:48px 80px 40px;">

  <!-- top row -->
  <div style="display:table;width:100%;">
    <div style="display:table-cell;vertical-align:top;">
      <span style="color:#1C2B3A;font-weight:bold;letter-spacing:4px;font-size:13px;">AIRSTREAM</span>
    </div>
    <div style="display:table-cell;vertical-align:top;text-align:right;">
      <span style="color:#A8B4BC;font-size:12px;">02 / 04</span>
    </div>
  </div>

  <!-- eyebrow -->
  <div style="color:#C09B5E;font-size:13px;letter-spacing:3px;text-transform:uppercase;font-weight:600;margin-top:8px;">
    PRE-LAUNCH BASELINE
  </div>

  <!-- H2 -->
  <h2 style="color:#1C2B3A;font-size:28px;font-weight:bold;margin-top:4px;">
    The &ldquo;Before&rdquo; Numbers
  </h2>

  <!-- sub -->
  <div style="color:#5C6E7A;font-size:13px;">
    Mar 2025 &ndash; May 2026 &middot; AIMBase data &middot; 83 dealers
  </div>

  <!-- monthly chart card -->
  <div style="background:#FFFFFF;border-radius:8px;padding:14px;margin-top:14px;">
    <div style="color:#1C2B3A;font-size:11px;font-weight:bold;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">
      MONTHLY LEAD VOLUME
    </div>
    {resize_svg(SVG_MONTHLY, 1376)}
  </div>

  <!-- bottom row -->
  <div style="display:table;width:100%;border-spacing:12px 0;margin-top:12px;table-layout:fixed;">
    <div style="display:table-cell;vertical-align:top;width:44%;">
      <div style="background:#FFFFFF;border-radius:8px;padding:12px 14px;">
        <div style="color:#1C2B3A;font-size:11px;font-weight:bold;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">SOURCE MIX</div>
        {resize_svg(SVG_SOURCE_DONUT, 160)}
        <div style="color:#5C6E7A;font-size:11px;margin-top:6px;">
          Direct 43% &nbsp;|&nbsp; Meta 34% &nbsp;|&nbsp; Google 12% &nbsp;|&nbsp; Email 6% &nbsp;|&nbsp; Other 5%
        </div>
      </div>
    </div>
    <div style="display:table-cell;vertical-align:top;width:31%;">
      <div style="background:#FFFFFF;border-radius:8px;padding:12px 14px;">
        <div style="color:#1C2B3A;font-size:11px;font-weight:bold;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">SCORE DISTRIBUTION</div>
        {resize_svg(SVG_SCORE, 340)}
      </div>
    </div>
    <div style="display:table-cell;vertical-align:top;width:25%;">
      <div style="background:#FFFFFF;border-radius:8px;padding:12px 14px;">
        <div style="color:#1C2B3A;font-size:11px;font-weight:bold;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">BRAND SPLIT</div>
        {resize_svg(SVG_BRAND, 260)}
      </div>
    </div>
  </div>

  <!-- footer -->
  <div style="position:absolute;bottom:20px;right:80px;font-size:11px;color:#5C6E7A;">
    AIMBase export &middot; Element Three
  </div>
</div>
"""

# ─────────────────────────────── PAGE 3 ───────────────────────────────────────
PAGE3 = f"""
<div class="page" style="background:#1C2B3A; padding:48px 80px 40px;">

  <!-- top row -->
  <div style="display:table;width:100%;">
    <div style="display:table-cell;vertical-align:top;">
      <span style="color:#FFFFFF;font-weight:bold;letter-spacing:4px;font-size:13px;">AIRSTREAM</span>
    </div>
    <div style="display:table-cell;vertical-align:top;text-align:right;">
      <span style="color:#A8B4BC;font-size:12px;">03 / 04</span>
    </div>
  </div>

  <!-- eyebrow -->
  <div style="color:#C09B5E;font-size:13px;letter-spacing:3px;text-transform:uppercase;font-weight:600;margin-top:8px;">
    FORECAST VS. ACTUAL
  </div>

  <!-- H2 -->
  <h2 style="color:#FFFFFF;font-size:28px;font-weight:bold;margin-top:4px;">
    Where Did June 2026 Land?
  </h2>

  <!-- sub -->
  <div style="color:#A8B4BC;font-size:13px;">
    Forecasted &ndash;7% from form elimination &middot; June 2026 running &ndash;37% vs. baseline
  </div>

  <!-- two chart cards -->
  <div style="display:table;width:100%;border-spacing:12px 0;margin-top:12px;table-layout:fixed;">
    <div style="display:table-cell;vertical-align:top;width:50%;">
      <div style="background:#243447;border-radius:8px;padding:12px 14px;">
        <div style="color:#C09B5E;font-size:11px;letter-spacing:2px;text-transform:uppercase;font-weight:600;margin-bottom:8px;">
          FORECAST SCENARIO MATRIX
        </div>
        {resize_svg(SVG_SCENARIO, 600)}
      </div>
    </div>
    <div style="display:table-cell;vertical-align:top;width:50%;">
      <div style="background:#243447;border-radius:8px;padding:12px 14px;">
        <div style="color:#C09B5E;font-size:11px;letter-spacing:2px;text-transform:uppercase;font-weight:600;margin-bottom:8px;">
          MONTHLY VOLUME
        </div>
        {resize_svg(SVG_TIMELINE, 600)}
        <div style="color:#A8B4BC;font-size:11px;margin-top:6px;">
          &#9632; Baseline 2025 &nbsp; &#9632; Forecast 2026 &nbsp; &#9632; Actual 2026
        </div>
      </div>
    </div>
  </div>

  <!-- metrics table card -->
  <div style="background:#243447;border-radius:8px;padding:14px;margin-top:10px;">
    <table style="width:100%;border-collapse:collapse;font-size:11px;">
      <thead>
        <tr style="color:#C09B5E;font-weight:bold;">
          <td style="padding:4px 8px;">Metric</td>
          <td style="padding:4px 8px;">Baseline</td>
          <td style="padding:4px 8px;">Forecast</td>
          <td style="padding:4px 8px;">Actual &mdash; June 2026</td>
          <td style="padding:4px 8px;">vs. Forecast</td>
        </tr>
      </thead>
      <tbody>
        <tr style="color:#D6DDE0;background:rgba(255,255,255,0.04);">
          <td style="padding:4px 8px;">Total leads / mo</td>
          <td style="padding:4px 8px;">~19,200</td>
          <td style="padding:4px 8px;">~17,900 (&ndash;7%)</td>
          <td style="padding:4px 8px;color:#C0392B;">~12,026</td>
          <td style="padding:4px 8px;color:#C0392B;">&ndash;33%</td>
        </tr>
        <tr style="color:#D6DDE0;">
          <td style="padding:4px 8px;">Per dealer / mo</td>
          <td style="padding:4px 8px;">231</td>
          <td style="padding:4px 8px;">~216</td>
          <td style="padding:4px 8px;color:#C0392B;">~145</td>
          <td style="padding:4px 8px;color:#C0392B;">&ndash;33%</td>
        </tr>
        <tr style="color:#D6DDE0;background:rgba(255,255,255,0.04);">
          <td style="padding:4px 8px;">External Paid share</td>
          <td style="padding:4px 8px;">~60%</td>
          <td style="padding:4px 8px;">~60% (unchanged)</td>
          <td style="padding:4px 8px;color:#C0392B;">81%</td>
          <td style="padding:4px 8px;color:#C0392B;">&uarr; Meta dominant</td>
        </tr>
        <tr style="color:#D6DDE0;">
          <td style="padding:4px 8px;">Score 3+ rate</td>
          <td style="padding:4px 8px;">6.3%</td>
          <td style="padding:4px 8px;">Flat-to-up</td>
          <td style="padding:4px 8px;color:#27AE60;">6.1%</td>
          <td style="padding:4px 8px;">Roughly flat</td>
        </tr>
        <tr style="color:#D6DDE0;background:rgba(255,255,255,0.04);">
          <td style="padding:4px 8px;">Travel Trailer share</td>
          <td style="padding:4px 8px;">68%</td>
          <td style="padding:4px 8px;">~66%</td>
          <td style="padding:4px 8px;color:#C0392B;">52%</td>
          <td style="padding:4px 8px;color:#C0392B;">&darr; TC overrepresented</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- footer -->
  <div style="position:absolute;bottom:20px;right:80px;font-size:11px;color:#A8B4BC;">
    AIMBase export &middot; Element Three
  </div>
</div>
"""

# ─────────────────────────────── PAGE 4 ───────────────────────────────────────
PAGE4 = f"""
<div class="page" style="background:#F4F6F7; padding:48px 80px 40px;">

  <!-- top row -->
  <div style="display:table;width:100%;">
    <div style="display:table-cell;vertical-align:top;">
      <span style="color:#1C2B3A;font-weight:bold;letter-spacing:4px;font-size:13px;">AIRSTREAM</span>
    </div>
    <div style="display:table-cell;vertical-align:top;text-align:right;">
      <span style="color:#A8B4BC;font-size:12px;">04 / 04</span>
    </div>
  </div>

  <!-- eyebrow -->
  <div style="color:#C09B5E;font-size:13px;letter-spacing:3px;text-transform:uppercase;font-weight:600;margin-top:8px;">
    QUALITY &amp; DIAGNOSTICS
  </div>

  <!-- H2 -->
  <h2 style="color:#1C2B3A;font-size:28px;font-weight:bold;margin-top:4px;">
    What to Watch
  </h2>

  <!-- sub -->
  <div style="color:#5C6E7A;font-size:13px;">
    Post-launch is only 22 days &middot; Run full 60&ndash;90 day window before final conclusions
  </div>

  <!-- 3 chart cards -->
  <div style="display:table;width:100%;border-spacing:12px 0;margin-top:12px;table-layout:fixed;">
    <div style="display:table-cell;vertical-align:top;width:33%;">
      <div style="background:#FFFFFF;border-radius:8px;padding:12px 14px;">
        <div style="color:#1C2B3A;font-size:11px;font-weight:bold;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">SCORE 3+ RATE</div>
        {resize_svg(SVG_S3RATE, 360)}
      </div>
    </div>
    <div style="display:table-cell;vertical-align:top;width:33%;">
      <div style="background:#FFFFFF;border-radius:8px;padding:12px 14px;">
        <div style="color:#1C2B3A;font-size:11px;font-weight:bold;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">SOURCE MIX SHIFT</div>
        {resize_svg(SVG_SRCMIX, 340)}
        <div style="color:#5C6E7A;font-size:11px;margin-top:4px;">
          &#9632; Baseline &nbsp; &#9632; Post-Launch
        </div>
      </div>
    </div>
    <div style="display:table-cell;vertical-align:top;width:33%;">
      <div style="background:#FFFFFF;border-radius:8px;padding:12px 14px;">
        <div style="color:#1C2B3A;font-size:11px;font-weight:bold;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">LEADS / DEALER / MONTH</div>
        {resize_svg(SVG_PERDEAL, 340)}
      </div>
    </div>
  </div>

  <!-- 2x2 diagnostic grid -->
  <div style="display:table;width:100%;border-spacing:12px 0;margin-top:10px;table-layout:fixed;">
    <!-- row 1 -->
    <div style="display:table-row;">
      <div style="display:table-cell;vertical-align:top;width:50%;padding-bottom:8px;">
        <div style="border-left:4px solid #C0392B;background:#FDF2F2;padding:12px 14px;border-radius:0 8px 8px 0;">
          <div style="color:#C0392B;font-size:11px;font-weight:bold;margin-bottom:4px;">
            &#9888; Volume below forecast floor
          </div>
          <div style="color:#1C2B3A;font-size:11px;line-height:1.5;">
            June pace (~12,026/mo) is &ndash;33% vs. forecast ~17,900.
            Check: was a brochure checkbox added? Did consolidated form field count cut CVR?
            Did new-site top-of-funnel traffic fall?
          </div>
        </div>
      </div>
      <div style="display:table-cell;vertical-align:top;width:50%;padding-bottom:8px;padding-left:12px;">
        <div style="border-left:4px solid #C0392B;background:#FDF2F2;padding:12px 14px;border-radius:0 8px 8px 0;">
          <div style="color:#C0392B;font-size:11px;font-weight:bold;margin-bottom:4px;">
            &#9888; External Paid share surged to 81%
          </div>
          <div style="color:#1C2B3A;font-size:11px;line-height:1.5;">
            Baseline was ~57% Meta. Post-launch jump to 81% means website-captured volume
            (Direct, Organic, Email) collapsed more than paid. The new site may be converting
            on-site visitors at a lower rate.
          </div>
        </div>
      </div>
    </div>
    <!-- row 2 -->
    <div style="display:table-row;">
      <div style="display:table-cell;vertical-align:top;width:50%;">
        <div style="border-left:4px solid #27AE60;background:#F0FBF4;padding:12px 14px;border-radius:0 8px 8px 0;">
          <div style="color:#27AE60;font-size:11px;font-weight:bold;margin-bottom:4px;">
            &#10003; Score 3+ rate holding roughly flat
          </div>
          <div style="color:#1C2B3A;font-size:11px;line-height:1.5;">
            Post-launch 6.1% vs. 6.3% baseline &mdash; within noise.
          </div>
        </div>
      </div>
      <div style="display:table-cell;vertical-align:top;width:50%;padding-left:12px;">
        <div style="border-left:4px solid #A8B4BC;background:#FFFFFF;padding:12px 14px;border-radius:0 8px 8px 0;">
          <div style="color:#A8B4BC;font-size:11px;font-weight:bold;margin-bottom:4px;">
            &#128197; Seasonality &amp; window size caveat
          </div>
          <div style="color:#1C2B3A;font-size:11px;line-height:1.5;">
            June 2025 was the annual peak at 28,693 leads. Compare June-to-June once the
            full month closes.
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- footer -->
  <div style="position:absolute;bottom:20px;right:80px;font-size:11px;color:#5C6E7A;">
    AIMBase export &middot; Element Three
  </div>
</div>
"""

# ── 4. Assemble full print HTML ───────────────────────────────────────────────
PRINT_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Airstream Dealer Lead Distribution</title>
  <style>
{CSS}
  </style>
</head>
<body>
{PAGE1}
{PAGE2}
{PAGE3}
{PAGE4}
</body>
</html>
"""

out_html = '/tmp/airstream_print.html'
with open(out_html, 'w') as f:
    f.write(PRINT_HTML)
print(f"Wrote {out_html}")

# ── 5. Run WeasyPrint ─────────────────────────────────────────────────────────
out_pdf = '/home/user/airstream-lead-distro-analysis/airstream_deck.pdf'
result = subprocess.run(
    ['python3', '-m', 'weasyprint', out_html, out_pdf],
    capture_output=True, text=True
)
print("WeasyPrint stdout:", result.stdout)
print("WeasyPrint stderr:", result.stderr[:2000] if result.stderr else "(none)")
if result.returncode != 0:
    print(f"ERROR: WeasyPrint exited with code {result.returncode}")
    sys.exit(1)

# ── 6. Verify output ──────────────────────────────────────────────────────────
size = os.path.getsize(out_pdf)
print(f"PDF size: {size:,} bytes ({size/1024:.1f} KB)")
if size < 50 * 1024:
    print("ERROR: PDF is smaller than 50 KB!")
    sys.exit(1)
else:
    print("SUCCESS: PDF is > 50 KB")
