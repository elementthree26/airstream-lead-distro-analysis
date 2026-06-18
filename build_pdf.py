#!/usr/bin/env python3
"""
build_pdf.py — Generate a polished Airstream branded executive PDF deck.
Outputs /tmp/airstream_print.html and airstream_deck.pdf.
"""

import re
import subprocess
from pathlib import Path

SRC_HTML = Path(__file__).parent / "airstream_deck.html"
OUT_HTML  = Path("/tmp/airstream_print.html")
OUT_PDF   = Path(__file__).parent / "airstream_deck.pdf"

# ── Extract SVGs from source ──────────────────────────────────────────────────
src = SRC_HTML.read_text()

def extract_svg(viewbox: str) -> str:
    """Extract first <svg viewBox="..."> ... </svg> matching the given viewBox."""
    pattern = rf'(<svg\s[^>]*viewBox="{re.escape(viewbox)}"[^>]*>.*?</svg>)'
    m = re.search(pattern, src, re.DOTALL | re.IGNORECASE)
    if not m:
        raise ValueError(f"SVG with viewBox '{viewbox}' not found")
    svg = m.group(1)
    # Replace style attribute to be WeasyPrint-friendly
    svg = re.sub(r'\s+style="[^"]*"', '', svg)
    svg = svg.replace('<svg ', '<svg style="width:100%;height:auto;display:block" ', 1)
    return svg

SVG_MONTHLY   = extract_svg("0 0 780 210")
SVG_SRC_DONUT = extract_svg("0 0 200 200")
SVG_SCORE     = extract_svg("0 0 260 180")
SVG_BRAND     = extract_svg("0 0 200 180")
SVG_SCENARIO  = extract_svg("0 0 440 220")
SVG_TIMELINE  = extract_svg("0 0 560 210")
SVG_S3RATE    = extract_svg("0 0 220 170")
SVG_SRCMIX    = extract_svg("0 0 320 170")
SVG_PERDEAL   = extract_svg("0 0 240 170")

# ── HTML ──────────────────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Airstream &middot; Dealer Lead Distribution &middot; Forecast vs. Actual</title>
<style>
/* Reset */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; background: #1C2B3A; }}

/* Page wrapper */
.page {{
  width: 1536px;
  height: 864px;
  overflow: hidden;
  page-break-after: always;
  position: relative;
}}

/* ─── SHARED HEADER BAR ─────────────────────────────────────────── */
.hdr-bar {{
  width: 1536px;
  height: 44px;
  background: #1C2B3A;
  position: relative;
}}
.hdr-bar-gold {{
  width: 1536px;
  height: 44px;
  background: #C09B5E;
  position: relative;
}}
.hdr-table {{
  display: table;
  width: 100%;
  height: 44px;
  padding: 0 56px;
}}
.hdr-left {{
  display: table-cell;
  vertical-align: middle;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: #FFFFFF;
}}
.hdr-left-dark {{
  display: table-cell;
  vertical-align: middle;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: #1C2B3A;
}}
.hdr-right {{
  display: table-cell;
  vertical-align: middle;
  text-align: right;
  font-size: 11px;
  letter-spacing: 2px;
  color: #C09B5E;
}}
.hdr-right-dark {{
  display: table-cell;
  vertical-align: middle;
  text-align: right;
  font-size: 11px;
  letter-spacing: 2px;
  color: #1C2B3A;
}}

/* ─── FOOTER STRIP ──────────────────────────────────────────────── */
.footer-strip {{
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: #C09B5E;
}}
.footer-strip-thin {{
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: #C09B5E;
}}

/* ─── COMMON TEXT ───────────────────────────────────────────────── */
.eyebrow {{
  font-size: 11px;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: #C09B5E;
  font-weight: 700;
  margin-bottom: 10px;
}}
.gold-rule {{
  width: 56px;
  height: 4px;
  background: #C09B5E;
  border-radius: 2px;
  margin: 12px 0 16px 0;
}}
.gold-rule-sm {{
  width: 44px;
  height: 3px;
  background: #C09B5E;
  border-radius: 2px;
  margin: 8px 0 10px 0;
}}

/* ─── PAGE 1 — TITLE SLIDE ──────────────────────────────────────── */
.kpi-table {{
  display: table;
  border-spacing: 12px 0;
  margin-top: 28px;
  margin-left: -12px;
}}
.kpi-cell {{
  display: table-cell;
  background: #243447;
  border: 1.5px solid #2E4056;
  border-radius: 10px;
  padding: 16px 14px;
  text-align: center;
  vertical-align: top;
  width: 340px;
}}
.kpi-cell-gold {{
  display: table-cell;
  background: #243447;
  border: 1.5px solid #C09B5E;
  border-radius: 10px;
  padding: 16px 14px;
  text-align: center;
  vertical-align: top;
  width: 340px;
}}
.kpi-cell-red {{
  display: table-cell;
  background: #243447;
  border: 1.5px solid #C0392B;
  border-radius: 10px;
  padding: 16px 14px;
  text-align: center;
  vertical-align: top;
  width: 340px;
}}
.kpi-val {{
  font-size: 34px;
  font-weight: 700;
  color: #FFFFFF;
  display: block;
}}
.kpi-val-red {{
  font-size: 34px;
  font-weight: 700;
  color: #C0392B;
  display: block;
}}
.kpi-label {{
  font-size: 11px;
  color: #A8B4BC;
  margin-top: 6px;
  line-height: 1.4;
}}
.kpi-sub {{
  font-size: 13px;
  font-weight: 700;
  color: #C0392B;
  margin-top: 4px;
}}
.meta-table {{
  display: table;
  width: 100%;
  border-spacing: 0;
  margin-top: 22px;
  padding-top: 14px;
  border-top: 1px solid #2A3A4A;
}}
.meta-cell {{
  display: table-cell;
  vertical-align: top;
  padding-right: 20px;
}}
.meta-key {{
  font-size: 10px;
  color: #C09B5E;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  font-weight: 700;
}}
.meta-val {{
  font-size: 13px;
  color: #D6DDE0;
  margin-top: 2px;
}}

/* ─── CARDS ─────────────────────────────────────────────────────── */
.card-light {{
  background: #FFFFFF;
  border-radius: 8px;
  padding: 12px 14px;
  box-shadow: 0 1px 8px #00000011;
  overflow: hidden;
}}
.card-dark {{
  background: #243447;
  border: 1px solid #2E4056;
  border-radius: 8px;
  padding: 12px 14px;
  overflow: hidden;
}}
.ct-light {{
  font-size: 10px;
  font-weight: 700;
  color: #1C2B3A;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-bottom: 3px;
}}
.ct-dark {{
  font-size: 10px;
  font-weight: 700;
  color: #D6DDE0;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-bottom: 3px;
}}
.cs-light {{
  font-size: 10px;
  color: #5C6E7A;
  margin-bottom: 6px;
}}
.cs-dark {{
  font-size: 10px;
  color: #5C6E7A;
  margin-bottom: 6px;
}}

/* ─── PAGE 2 LAYOUT ─────────────────────────────────────────────── */
.p2-body {{
  background: #F4F6F7;
  padding: 16px 56px 36px 56px;
  position: relative;
  height: 820px;
}}
.bottom-row-table {{
  display: table;
  border-spacing: 10px 0;
  margin-top: 10px;
  margin-left: -10px;
  width: 1460px;
}}
.br-cell-a {{
  display: table-cell;
  width: 750px;
  vertical-align: top;
}}
.br-cell-b {{
  display: table-cell;
  width: 420px;
  vertical-align: top;
}}
.br-cell-c {{
  display: table-cell;
  width: 290px;
  vertical-align: top;
}}
.src-mix-table {{
  display: table;
  width: 100%;
  border-spacing: 12px 0;
}}
.src-mix-donut {{
  display: table-cell;
  width: 160px;
  vertical-align: middle;
}}
.src-mix-text {{
  display: table-cell;
  vertical-align: middle;
  font-size: 13px;
  color: #5C6E7A;
  line-height: 1.8;
}}
.leg-dot {{
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 1px;
  vertical-align: middle;
  margin-right: 3px;
}}

/* ─── PAGE 3 LAYOUT ─────────────────────────────────────────────── */
.p3-body {{
  background: #1C2B3A;
  padding: 16px 56px 10px 56px;
  position: relative;
  height: 820px;
}}
.chart-row-table {{
  display: table;
  border-spacing: 12px 0;
  margin-top: 12px;
  margin-left: -12px;
  width: 1560px;
}}
.chart-cell-left {{
  display: table-cell;
  width: 640px;
  vertical-align: top;
}}
.chart-cell-right {{
  display: table-cell;
  width: 820px;
  vertical-align: top;
}}
.metrics-card {{
  background: #243447;
  border: 1px solid #2E4056;
  border-radius: 8px;
  padding: 12px 16px;
  margin-top: 10px;
}}
.metrics-tbl {{
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}}
.metrics-tbl th {{
  padding: 5px 10px;
  text-align: left;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: #A8B4BC;
  border-bottom: 1px solid #2E4056;
  font-weight: 600;
}}
.metrics-tbl th:not(:first-child) {{
  text-align: right;
}}
.metrics-tbl td {{
  padding: 6px 10px;
  color: #D6DDE0;
  border-bottom: 1px solid #1E2F40;
}}
.metrics-tbl td:first-child {{
  color: #FFFFFF;
  font-weight: 600;
  text-align: left;
}}
.metrics-tbl td:not(:first-child) {{
  text-align: right;
}}
.metrics-tbl tr:nth-child(even) td {{
  background: #1E3048;
}}
.neg {{ color: #C0392B !important; font-weight: 700; }}
.pos {{ color: #27AE60 !important; font-weight: 700; }}
.sil {{ color: #A8B4BC; }}

/* ─── PAGE 4 LAYOUT ─────────────────────────────────────────────── */
.p4-body {{
  background: #F4F6F7;
  padding: 16px 56px 36px 56px;
  position: relative;
  height: 820px;
}}
.top-row-table {{
  display: table;
  border-spacing: 10px 0;
  margin-top: 10px;
  margin-left: -10px;
  width: 1460px;
}}
.tr-cell-a {{
  display: table-cell;
  width: 390px;
  vertical-align: top;
}}
.tr-cell-b {{
  display: table-cell;
  width: 590px;
  vertical-align: top;
}}
.tr-cell-c {{
  display: table-cell;
  width: 430px;
  vertical-align: top;
}}
.diag-table {{
  display: table;
  border-spacing: 10px 0;
  margin-top: 10px;
  margin-left: -10px;
  width: 1460px;
}}
.diag-col {{
  display: table-cell;
  width: 720px;
  vertical-align: top;
}}
.diag-warn {{
  background: #FEF4F3;
  border-left: 4px solid #C0392B;
  border-radius: 6px;
  padding: 10px 14px;
  margin-bottom: 8px;
}}
.diag-ok {{
  background: #EDF7F1;
  border-left: 4px solid #27AE60;
  border-radius: 6px;
  padding: 10px 14px;
  margin-bottom: 8px;
}}
.diag-info {{
  background: #FFFFFF;
  border-left: 4px solid #A8B4BC;
  border-radius: 6px;
  padding: 10px 14px;
  box-shadow: 0 1px 4px #0000000f;
  margin-bottom: 8px;
}}
.dh {{
  font-size: 12px;
  font-weight: 700;
  color: #1C2B3A;
  margin-bottom: 4px;
}}
.db {{
  font-size: 11px;
  color: #5C6E7A;
  line-height: 1.55;
}}
.footer-credit {{
  position: absolute;
  bottom: 10px;
  right: 56px;
  font-size: 10px;
  color: #5C6E7A;
}}
</style>
</head>
<body>

<!-- ===============================================================
     PAGE 1 - TITLE SLIDE
================================================================ -->
<div class="page">
  <div style="background:#1C2B3A; width:1536px; height:864px; position:relative;">
    <!-- 8px gold left bar -->
    <div style="position:absolute;left:0;top:0;bottom:0;width:8px;background:#C09B5E;"></div>

    <!-- Top header row -->
    <div style="padding:14px 56px 12px 72px; border-bottom:1px solid #2A3A4A;">
      <div style="display:table;width:100%;">
        <div style="display:table-cell;vertical-align:middle;font-size:14px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#FFFFFF;">AIRSTREAM</div>
        <div style="display:table-cell;vertical-align:middle;text-align:right;font-size:10px;color:#5C6E7A;">CONFIDENTIAL &middot; ELEMENT THREE &middot; JUNE 2026</div>
      </div>
    </div>

    <!-- Content area -->
    <div style="padding:50px 56px 0 72px;">
      <div class="eyebrow">DEALER LEAD DISTRIBUTION</div>
      <div style="font-size:52px;font-weight:900;line-height:1.05;color:#FFFFFF;">Forecast vs. Actual<br>Post-Launch Analysis</div>
      <div class="gold-rule"></div>
      <div style="font-size:15px;color:#A8B4BC;line-height:1.5;">How did the new Airstream website affect dealer lead volume?</div>
      <div style="font-size:12px;color:#5C6E7A;margin-top:6px;">Pre-launch forecast &middot; May 27, 2026 launch &middot; 22 days of post-launch data</div>

      <!-- KPI boxes -->
      <div class="kpi-table">
        <div class="kpi-cell-gold">
          <span class="kpi-val">249,981</span>
          <div class="kpi-label">Historical Leads / 13-mo baseline</div>
        </div>
        <div class="kpi-cell">
          <span class="kpi-val">~19,200</span>
          <div class="kpi-label">Avg Leads / Month / pre-launch baseline</div>
        </div>
        <div class="kpi-cell">
          <span class="kpi-val">~17,900</span>
          <div class="kpi-label">Forecasted Monthly / (&ndash;7% from baseline)</div>
        </div>
        <div class="kpi-cell-red">
          <span class="kpi-val-red">~12,026</span>
          <div class="kpi-label">June 2026 Pace / 18 days of data</div>
          <div class="kpi-sub">&ndash;37% vs. baseline</div>
        </div>
      </div>

      <!-- Meta row -->
      <div class="meta-table">
        <div class="meta-cell">
          <div class="meta-key">Website Launch</div>
          <div class="meta-val">May 27, 2026</div>
        </div>
        <div class="meta-cell">
          <div class="meta-key">Post-Launch Window</div>
          <div class="meta-val">May 28 &ndash; June 18, 2026</div>
        </div>
        <div class="meta-cell">
          <div class="meta-key">Baseline Window</div>
          <div class="meta-val">Mar 2025 &ndash; May 2026</div>
        </div>
        <div class="meta-cell">
          <div class="meta-key">Dealers</div>
          <div class="meta-val">83</div>
        </div>
        <div class="meta-cell">
          <div class="meta-key">Pipeline</div>
          <div class="meta-val">HubSpot &rarr; Make &rarr; AIMBase &rarr; Dealers</div>
        </div>
        <div class="meta-cell">
          <div class="meta-key">Prepared by</div>
          <div class="meta-val">Element Three &middot; June 2026</div>
        </div>
      </div>
    </div>

    <!-- Footer gold strip -->
    <div class="footer-strip"></div>
  </div>
</div>

<!-- ===============================================================
     PAGE 2 - PRE-LAUNCH BASELINE
================================================================ -->
<div class="page">
  <div class="hdr-bar">
    <div class="hdr-table">
      <div class="hdr-left">AIRSTREAM</div>
      <div class="hdr-right">02 / 04</div>
    </div>
  </div>
  <div class="p2-body">
    <div class="eyebrow" style="margin-bottom:6px;">PRE-LAUNCH BASELINE</div>
    <div style="font-size:30px;font-weight:700;color:#1C2B3A;margin-bottom:4px;">The &#8220;Before&#8221; Numbers</div>
    <div class="gold-rule-sm"></div>
    <div style="font-size:12px;color:#5C6E7A;margin-bottom:10px;">Mar 2025 &ndash; May 2026 &middot; AIMBase data &middot; 83 dealers</div>

    <!-- Monthly trend card -->
    <div class="card-light">
      <div class="ct-light">MONTHLY LEAD VOLUME &mdash; PRE-LAUNCH</div>
      <div class="cs-light">Gold bar = Jun 2025 peak &middot; Dashed line = ~19,200 baseline avg</div>
      {SVG_MONTHLY}
    </div>

    <!-- Bottom 3-card row -->
    <div class="bottom-row-table">
      <div class="br-cell-a">
        <div class="card-light" style="height:215px;">
          <div class="ct-light">SOURCE MIX (BASELINE)</div>
          <div class="src-mix-table">
            <div class="src-mix-donut">
              {SVG_SRC_DONUT}
            </div>
            <div class="src-mix-text">
              <div><strong style="color:#1C2B3A;">~60%</strong> External Paid (Meta)</div>
              <div><strong style="color:#1C2B3A;">~40%</strong> Website-Captured</div>
              <div style="margin-top:8px;font-size:11px;color:#5C6E7A;">Meta leads unaffected by website change</div>
            </div>
          </div>
        </div>
      </div>
      <div class="br-cell-b">
        <div class="card-light" style="height:215px;">
          <div class="ct-light">SCORE DISTRIBUTION</div>
          {SVG_SCORE}
          <div style="margin-top:4px;">
            <span style="font-size:9px;color:#5C6E7A;"><span class="leg-dot" style="background:#1C2B3A;"></span>Baseline</span>
            &nbsp;&nbsp;
            <span style="font-size:9px;color:#5C6E7A;"><span class="leg-dot" style="background:#C09B5E;"></span>Post-Launch</span>
          </div>
        </div>
      </div>
      <div class="br-cell-c">
        <div class="card-light" style="height:215px;">
          <div class="ct-light">BRAND SPLIT</div>
          {SVG_BRAND}
          <div style="margin-top:4px;">
            <span style="font-size:9px;color:#5C6E7A;"><span class="leg-dot" style="background:#1C2B3A;"></span>Travel Trailer</span>
            &nbsp;&nbsp;
            <span style="font-size:9px;color:#5C6E7A;"><span class="leg-dot" style="background:#C09B5E;"></span>Touring Coach</span>
          </div>
        </div>
      </div>
    </div>

    <div class="footer-strip-thin"></div>
  </div>
</div>

<!-- ===============================================================
     PAGE 3 - FORECAST VS. ACTUAL
================================================================ -->
<div class="page">
  <div class="hdr-bar-gold">
    <div class="hdr-table">
      <div class="hdr-left-dark">AIRSTREAM</div>
      <div class="hdr-right-dark">03 / 04</div>
    </div>
  </div>
  <div class="p3-body">
    <div class="eyebrow">FORECAST VS. ACTUAL</div>
    <div style="font-size:30px;font-weight:700;color:#FFFFFF;margin-bottom:4px;">Where Did June 2026 Land?</div>
    <div class="gold-rule-sm"></div>
    <div style="font-size:12px;color:#A8B4BC;">Forecasted &ndash;7% from form elimination &middot; June 2026 running &ndash;37% vs. baseline</div>

    <div class="chart-row-table">
      <div class="chart-cell-left">
        <div class="card-dark">
          <div class="ct-dark">FORECAST SCENARIO MATRIX</div>
          <div class="cs-dark">Red line = June 2026 actual pace (~12,026/mo)</div>
          {SVG_SCENARIO}
        </div>
      </div>
      <div class="chart-cell-right">
        <div class="card-dark">
          <div class="ct-dark">MONTHLY VOLUME &mdash; BASELINE THROUGH POST-LAUNCH</div>
          <div class="cs-dark">*June 2026 projected from 18 days of actuals &middot; Gold dashed = forecast</div>
          {SVG_TIMELINE}
          <div style="margin-top:4px;">
            <span style="font-size:9px;color:#A8B4BC;"><span class="leg-dot" style="background:#1C2B3A;border:1px solid #4A6070;"></span>Pre-Launch</span>
            &nbsp;&nbsp;
            <span style="font-size:9px;color:#A8B4BC;"><span class="leg-dot" style="background:#C0392B;"></span>Post-Launch</span>
          </div>
        </div>
      </div>
    </div>

    <div class="metrics-card">
      <div class="ct-dark">FORECAST vs. ACTUAL &mdash; KEY METRICS</div>
      <table class="metrics-tbl">
        <thead>
          <tr>
            <th>Metric</th>
            <th>Baseline</th>
            <th>Forecast</th>
            <th>Actual &mdash; June 2026</th>
            <th>vs. Forecast</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Total leads / mo</td>
            <td>~19,200</td>
            <td>~17,900 (&ndash;7%)</td>
            <td class="neg">~12,026</td>
            <td class="neg">&ndash;33%</td>
          </tr>
          <tr>
            <td>Per dealer / mo</td>
            <td>231</td>
            <td>~216</td>
            <td class="neg">~145</td>
            <td class="neg">&ndash;33%</td>
          </tr>
          <tr>
            <td>External Paid share</td>
            <td>~60%</td>
            <td>~60% (unchanged)</td>
            <td class="neg">81%</td>
            <td class="sil">&uarr; Meta dominant</td>
          </tr>
          <tr>
            <td>Score 3+ rate</td>
            <td>6.3%</td>
            <td>Flat-to-up</td>
            <td class="pos">6.1%</td>
            <td class="sil">Roughly flat</td>
          </tr>
          <tr>
            <td>Travel Trailer share</td>
            <td>68%</td>
            <td>~66%</td>
            <td class="neg">52%</td>
            <td class="sil">&darr; TC overrepresented</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="footer-strip"></div>
  </div>
</div>

<!-- ===============================================================
     PAGE 4 - QUALITY & DIAGNOSTICS
================================================================ -->
<div class="page">
  <div class="hdr-bar">
    <div class="hdr-table">
      <div class="hdr-left">AIRSTREAM</div>
      <div class="hdr-right">04 / 04</div>
    </div>
  </div>
  <div class="p4-body">
    <div class="eyebrow" style="margin-bottom:6px;">QUALITY &amp; DIAGNOSTICS</div>
    <div style="font-size:30px;font-weight:700;color:#1C2B3A;margin-bottom:4px;">What to Watch</div>
    <div class="gold-rule-sm"></div>
    <div style="font-size:12px;color:#5C6E7A;margin-bottom:0;">Post-launch is only 22 days &middot; Run full 60&ndash;90 day window before final conclusions</div>

    <div class="top-row-table">
      <div class="tr-cell-a">
        <div class="card-light">
          <div class="ct-light">SCORE 3+ RATE</div>
          {SVG_S3RATE}
        </div>
      </div>
      <div class="tr-cell-b">
        <div class="card-light">
          <div class="ct-light">SOURCE MIX SHIFT</div>
          {SVG_SRCMIX}
          <div style="margin-top:4px;">
            <span style="font-size:9px;color:#5C6E7A;"><span class="leg-dot" style="background:#1C2B3A;"></span>Baseline</span>
            &nbsp;&nbsp;
            <span style="font-size:9px;color:#5C6E7A;"><span class="leg-dot" style="background:#C09B5E;"></span>Post-Launch</span>
          </div>
        </div>
      </div>
      <div class="tr-cell-c">
        <div class="card-light">
          <div class="ct-light">LEADS / DEALER / MONTH</div>
          {SVG_PERDEAL}
        </div>
      </div>
    </div>

    <div class="diag-table">
      <div class="diag-col">
        <div class="diag-warn">
          <div class="dh">&#9888; Volume below forecast floor</div>
          <div class="db">June pace (~12,026/mo) is &ndash;33% vs. forecast ~17,900. Check: was a brochure checkbox added? Did consolidated form field count cut CVR? Did new-site top-of-funnel traffic fall?</div>
        </div>
        <div class="diag-ok">
          <div class="dh">&#10003; Score 3+ rate holding roughly flat</div>
          <div class="db">Post-launch 6.1% vs. 6.3% baseline &mdash; within noise. The &#8220;fewer but higher-quality leads&#8221; thesis is not yet disproved. Watch as volume stabilizes over 60&ndash;90 days.</div>
        </div>
      </div>
      <div class="diag-col">
        <div class="diag-warn">
          <div class="dh">&#9888; External Paid share surged to 81%</div>
          <div class="db">Baseline was ~57% Meta. Post-launch jump to 81% means website-captured volume (Direct, Organic, Email) collapsed more than paid. The new site may be converting on-site visitors at a lower rate.</div>
        </div>
        <div class="diag-info">
          <div class="dh">&#128197; Seasonality &amp; window size caveat</div>
          <div class="db">June 2025 was the annual peak at 28,693 leads. Compare June-to-June once the full month closes and re-run after 90 days before drawing final conclusions.</div>
        </div>
      </div>
    </div>

    <div class="footer-credit">Element Three &middot; Confidential</div>
    <div class="footer-strip-thin"></div>
  </div>
</div>

</body>
</html>
"""

# ── Write HTML ────────────────────────────────────────────────────────────────
OUT_HTML.write_text(html, encoding="utf-8")
print(f"HTML written: {OUT_HTML}  ({OUT_HTML.stat().st_size // 1024} KB)")

# ── Generate PDF via WeasyPrint ───────────────────────────────────────────────
result = subprocess.run(
    ["weasyprint", str(OUT_HTML), str(OUT_PDF)],
    capture_output=True,
    text=True
)
if result.returncode != 0:
    print("STDERR:", result.stderr[:3000])
    raise RuntimeError(f"WeasyPrint failed (exit {result.returncode})")

size_kb = OUT_PDF.stat().st_size // 1024
print(f"PDF written:  {OUT_PDF}  ({size_kb} KB)")
if size_kb < 60:
    raise RuntimeError(f"PDF too small ({size_kb} KB) — something went wrong")

print("Done.")
