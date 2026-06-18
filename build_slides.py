"""
Airstream Dealer Lead Distribution — Forecast vs. Actual Slides
Post-launch window: May 27, 2026
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.gridspec as gridspec
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import warnings
warnings.filterwarnings('ignore')

# ── Brand palette ──────────────────────────────────────────────────────────
NAVY      = '#1C2B3A'
SILVER    = '#A8B4BC'
LIGHT_SIL = '#D6DDE0'
GOLD      = '#C09B5E'
WHITE     = '#FFFFFF'
RED       = '#C0392B'
GREEN     = '#27AE60'
MID_GRAY  = '#5C6E7A'
BG        = '#F4F6F7'

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans'],
    'axes.facecolor': BG,
    'figure.facecolor': WHITE,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.spines.bottom': False,
    'axes.grid': False,
    'xtick.color': MID_GRAY,
    'ytick.color': MID_GRAY,
    'text.color': NAVY,
})

DATA = '/root/.claude/uploads/62219832-3331-54a1-98f1-d82a07069b17'

# ── Load data ──────────────────────────────────────────────────────────────
print('Loading data...')
pre_files = [
    f'{DATA}/79cc431c-3120265262026_Leads.xlsx',
    f'{DATA}/efcf71ee-101202512312025_Leads.xlsx',
    f'{DATA}/62567f8f-7120259302025.xlsx',
    f'{DATA}/993d030d-040120256302025_leads.xlsx',
    f'{DATA}/1577ae0c-2120253312025.xlsx',
]
dfs = []
for f in pre_files:
    df = pd.read_excel(f, usecols=['Lead Date','Lead Source','Lead Score','Brand','Dealer'])
    dfs.append(df)

pre_all = pd.concat(dfs, ignore_index=True)
pre_all['Lead Date'] = pd.to_datetime(pre_all['Lead Date'], format='mixed')
pre_all['month'] = pre_all['Lead Date'].dt.to_period('M')

# Baseline: Mar 2025 – Mar 2026 (11 months available from upload; Jan/Feb 2026 missing)
baseline = pre_all[(pre_all['Lead Date'] >= '2025-03-01') & (pre_all['Lead Date'] < '2026-04-01')].copy()
# We have 11 months; PDF used 13 months (incl Jan+Feb 2026 which weren't uploaded)
# Use our 11-month window, note the gap
BASELINE_MONTHS = 11

# Post-launch: May 28 – June 18, 2026
post = pd.read_csv(f'{DATA}/4661ff1f-5282661826_Leads_Post_Launch.csv',
                   usecols=['Lead Date','Lead Source','Lead Score','Brand','Dealer'])
post['Lead Date'] = pd.to_datetime(post['Lead Date'], format='mixed')
post_jun = post[post['Lead Date'] >= '2026-06-01'].copy()  # full June days
jun_days = post_jun['Lead Date'].dt.date.nunique()
print(f'Post-launch June: {len(post_jun)} leads over {jun_days} unique days')

# ── Derived metrics ────────────────────────────────────────────────────────
def classify_source(s):
    s = str(s).upper()
    if 'PAID_SOCIAL' in s or 'FACEBOOK' in s or 'META' in s:
        return 'External Paid\n(Meta)'
    elif 'DIRECT' in s:
        return 'Direct Traffic'
    elif 'ORGANIC' in s:
        return 'Organic Search'
    elif 'EMAIL' in s:
        return 'Email Marketing'
    elif 'PAID_SEARCH' in s or 'PAID SEARCH' in s:
        return 'Paid Search'
    else:
        return 'Other'

baseline['source_cat'] = baseline['Lead Source'].apply(classify_source)
post['source_cat'] = post['Lead Source'].apply(classify_source)

# Monthly volume
monthly_pre = baseline.groupby('month').size().reset_index(name='leads')
monthly_pre['month_dt'] = monthly_pre['month'].dt.to_timestamp()

# Key numbers
baseline_total = len(baseline)
baseline_avg_mo = baseline_total / BASELINE_MONTHS   # ~19,793 matches ~19,200 from PDF
dealers = baseline['Dealer'].nunique()

# PDF baseline: 19,200/mo (use PDF number for forecast comparison)
PDF_BASELINE = 19200
PDF_FORECAST = 17900
DEALERS = 83

# Post-launch June run rate
jun_leads = len(post_jun)
jun_daily_rate = jun_leads / jun_days
jun_monthly_rate = jun_daily_rate * 30
print(f'June run rate: {jun_daily_rate:.1f}/day → {jun_monthly_rate:.0f}/mo projected')

# Score 3+ rates
def score3plus_rate(df):
    s = pd.to_numeric(df['Lead Score'], errors='coerce')
    return (s >= 3).sum() / len(df) * 100

baseline_s3 = score3plus_rate(baseline)
post_s3 = score3plus_rate(post)

# Brand split
def brand_split(df):
    tt = (df['Brand'].str.upper().str.contains('TRAVEL', na=False)).sum()
    tc = (df['Brand'].str.upper().str.contains('TOURING', na=False)).sum()
    return tt, tc

b_tt, b_tc = brand_split(baseline)
p_tt, p_tc = brand_split(post)

# Source splits %
b_src = baseline['source_cat'].value_counts(normalize=True) * 100
p_src = post['source_cat'].value_counts(normalize=True) * 100

# Score distribution
b_score = pd.to_numeric(baseline['Lead Score'], errors='coerce').value_counts().sort_index()
p_score = pd.to_numeric(post['Lead Score'], errors='coerce').value_counts().sort_index()
b_score_pct = b_score / b_score.sum() * 100
p_score_pct = p_score / p_score.sum() * 100

print(f'Baseline avg/mo (our data): {baseline_avg_mo:.0f}')
print(f'Post June monthly rate: {jun_monthly_rate:.0f}')
print(f'Baseline Score3+: {baseline_s3:.1f}%')
print(f'Post Score3+: {post_s3:.1f}%')
print(f'Baseline source: {b_src.to_dict()}')
print(f'Post source: {p_src.to_dict()}')

# ── Helper functions ────────────────────────────────────────────────────────
def add_logo_area(fig, text='AIRSTREAM'):
    fig.text(0.02, 0.97, text, fontsize=14, fontweight='bold',
             color=NAVY, va='top', ha='left', transform=fig.transFigure,
             fontfamily='sans-serif')
    fig.text(0.02, 0.94, '── Lead Distribution Analysis  |  Element Three  |  June 2026',
             fontsize=8, color=MID_GRAY, va='top', ha='left', transform=fig.transFigure)

def bottom_bar(fig, label=''):
    ax = fig.add_axes([0, 0, 1, 0.025])
    ax.set_facecolor(NAVY)
    ax.axis('off')
    ax.text(0.5, 0.5, label, color=SILVER, fontsize=7, ha='center', va='center',
            transform=ax.transAxes)

def title_style(ax, title, subtitle=''):
    ax.set_title(title, fontsize=13, fontweight='bold', color=NAVY, pad=10, loc='left')
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=8.5,
                color=MID_GRAY, va='bottom')

def metric_box(ax, label, value, delta=None, delta_positive=True):
    ax.set_facecolor(NAVY)
    ax.axis('off')
    ax.text(0.5, 0.65, value, fontsize=22, fontweight='bold', color=WHITE,
            ha='center', va='center', transform=ax.transAxes)
    ax.text(0.5, 0.25, label, fontsize=8, color=SILVER,
            ha='center', va='center', transform=ax.transAxes)
    if delta:
        col = GREEN if delta_positive else RED
        ax.text(0.5, 0.88, delta, fontsize=9, color=col,
                ha='center', va='center', transform=ax.transAxes)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title / Context
# ════════════════════════════════════════════════════════════════════════════
print('Building slide 1...')
fig1 = plt.figure(figsize=(16, 9), facecolor=NAVY)

# Left silver stripe
ax_stripe = fig1.add_axes([0, 0, 0.008, 1])
ax_stripe.set_facecolor(GOLD)
ax_stripe.axis('off')

# Title block
fig1.text(0.06, 0.72, 'AIRSTREAM', fontsize=48, fontweight='bold',
          color=WHITE, va='top', ha='left', transform=fig1.transFigure, alpha=0.15)
fig1.text(0.06, 0.72, 'AIRSTREAM', fontsize=48, fontweight='bold',
          color=WHITE, va='top', ha='left', transform=fig1.transFigure)
fig1.text(0.06, 0.58, 'Dealer Lead Distribution', fontsize=32, fontweight='bold',
          color=WHITE, va='top', ha='left', transform=fig1.transFigure)
fig1.text(0.06, 0.48, 'Forecast vs. Actual  ·  Post-Launch Analysis',
          fontsize=18, color=GOLD, va='top', ha='left', transform=fig1.transFigure)

# Divider line
ax_line = fig1.add_axes([0.06, 0.44, 0.88, 0.002])
ax_line.set_facecolor(SILVER)
ax_line.axis('off')

# Context bullets
bullets = [
    ('Website Launch', 'May 27, 2026'),
    ('Pre-Launch Baseline', 'Mar 2025 – Mar 2026  ·  ~19,200 leads/mo'),
    ('Forecasted Outcome', '~17,900 leads/mo  (–7%, form elimination impact)'),
    ('Post-Launch Window', 'May 28 – June 18, 2026  ·  22 days of live data'),
    ('Lead Pipeline', 'HubSpot → Make → AIMBase → 83 Dealers'),
]
for i, (lbl, val) in enumerate(bullets):
    y = 0.38 - i * 0.065
    fig1.text(0.06, y, f'{lbl}:', fontsize=11, color=GOLD, va='top',
              transform=fig1.transFigure, fontweight='bold')
    fig1.text(0.28, y, val, fontsize=11, color=WHITE, va='top',
              transform=fig1.transFigure)

# Metric boxes at bottom
metrics = [
    ('249,981', 'Historical Leads\n(13-mo baseline)'),
    ('~19,200', 'Avg Leads / Month\n(pre-launch)'),
    ('~17,900', 'Forecasted\nMonthly Volume'),
    (f'{int(jun_monthly_rate):,}', 'June 2026\nRun Rate'),
]
colors_m = [NAVY, MID_GRAY, MID_GRAY, RED if jun_monthly_rate < PDF_FORECAST else GREEN]
for i, (val, lbl) in enumerate(metrics):
    ax = fig1.add_axes([0.06 + i*0.235, 0.04, 0.21, 0.14])
    border_col = GOLD if i == 0 else (RED if (i==3 and jun_monthly_rate < PDF_FORECAST) else SILVER)
    ax.set_facecolor('#243447')
    for spine in ax.spines.values():
        spine.set_edgecolor(border_col)
        spine.set_linewidth(1.5)
    ax.axis('off')
    ax.text(0.5, 0.62, val, fontsize=20, fontweight='bold', color=WHITE,
            ha='center', va='center', transform=ax.transAxes)
    ax.text(0.5, 0.22, lbl, fontsize=8, color=SILVER,
            ha='center', va='center', transform=ax.transAxes)

fig1.text(0.96, 0.02, 'Element Three  ·  Confidential', fontsize=7,
          color=MID_GRAY, ha='right', va='bottom', transform=fig1.transFigure)

fig1.savefig('/home/user/airstream-lead-distro-analysis/slide1_title.png',
             dpi=150, bbox_inches='tight', facecolor=NAVY)
plt.close(fig1)
print('Slide 1 done.')

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Pre-Launch Baseline Deep Dive
# ════════════════════════════════════════════════════════════════════════════
print('Building slide 2...')
fig2 = plt.figure(figsize=(16, 9), facecolor=WHITE)
add_logo_area(fig2)

gs = gridspec.GridSpec(2, 3, figure=fig2, left=0.05, right=0.97,
                       top=0.88, bottom=0.1, hspace=0.45, wspace=0.35)

# ── Top spanning: Monthly volume trend ────────────────────────────────────
ax_trend = fig2.add_subplot(gs[0, :])
ax_trend.set_facecolor(BG)
months = monthly_pre['month_dt']
leads = monthly_pre['leads']

bars = ax_trend.bar(range(len(months)), leads, color=NAVY, width=0.6, zorder=2)

# Highlight the peak (June 2025)
peak_idx = leads.idxmax()
bars[peak_idx].set_color(GOLD)

# Forecast line
ax_trend.axhline(PDF_BASELINE, color=SILVER, linewidth=1.5, linestyle='--', zorder=3, alpha=0.8)
ax_trend.text(len(months)-0.3, PDF_BASELINE + 200, 'Baseline avg ~19,200', fontsize=7.5,
              color=MID_GRAY, va='bottom', ha='right')

ax_trend.set_xticks(range(len(months)))
ax_trend.set_xticklabels([m.strftime('%b\n%Y') for m in months], fontsize=8, color=MID_GRAY)
ax_trend.set_ylabel('Dealer Leads', fontsize=9, color=MID_GRAY)
ax_trend.yaxis.set_tick_params(labelsize=8)
for bar, val in zip(bars, leads):
    ax_trend.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 150,
                  f'{int(val/1000):.0f}k', ha='center', va='bottom', fontsize=7, color=MID_GRAY)

# Seasonality note
ax_trend.annotate('Seasonality: June\npeak (+49% vs winter)',
                  xy=(peak_idx, leads.iloc[peak_idx]),
                  xytext=(peak_idx - 2, leads.iloc[peak_idx] - 5500),
                  arrowprops=dict(arrowstyle='->', color=GOLD, lw=1.2),
                  fontsize=7.5, color=GOLD)

title_style(ax_trend, 'Monthly Lead Volume — Pre-Launch Baseline',
            'Mar 2025 – Mar 2026  ·  11 months of uploaded data  (Jan–Feb 2026 not included in upload)')
ax_trend.spines['bottom'].set_visible(True)
ax_trend.spines['bottom'].set_color(LIGHT_SIL)

# ── Bottom left: Source split ─────────────────────────────────────────────
ax_src = fig2.add_subplot(gs[1, 0])
ax_src.set_facecolor(BG)
src_labels = ['External Paid\n(Meta)', 'Direct Traffic', 'Organic Search',
              'Email Marketing', 'Paid Search', 'Other']
src_counts = [baseline['source_cat'].value_counts().get(l, 0) for l in src_labels]
src_pcts = [c / sum(src_counts) * 100 for c in src_counts]
colors_src = [GOLD, NAVY, MID_GRAY, SILVER, '#7F8C8D', LIGHT_SIL]

wedges, texts, autotexts = ax_src.pie(
    src_counts, labels=None, autopct='%1.0f%%',
    colors=colors_src, startangle=90,
    wedgeprops={'edgecolor': WHITE, 'linewidth': 1.5},
    pctdistance=0.75, textprops={'fontsize': 8}
)
for at in autotexts:
    at.set_color(WHITE)
    at.set_fontweight('bold')
    at.set_fontsize(7)

legend_patches = [mpatches.Patch(color=colors_src[i], label=f'{src_labels[i].replace(chr(10)," ")} ({src_pcts[i]:.0f}%)')
                  for i in range(len(src_labels))]
ax_src.legend(handles=legend_patches, fontsize=6.5, loc='lower center',
              bbox_to_anchor=(0.5, -0.45), ncol=2, frameon=False)
title_style(ax_src, 'Source Mix\n(Baseline)')

# ── Bottom center: Score distribution ────────────────────────────────────
ax_sc = fig2.add_subplot(gs[1, 1])
ax_sc.set_facecolor(BG)
score_vals = [1, 2, 3, 4, 5]
score_pcts_b = [b_score_pct.get(float(s), 0) for s in score_vals]
score_pcts_p = [p_score_pct.get(float(s), 0) for s in score_vals]

x = np.arange(len(score_vals))
w = 0.35
bars_b = ax_sc.bar(x - w/2, score_pcts_b, w, color=NAVY, label='Baseline', zorder=2)
bars_p = ax_sc.bar(x + w/2, score_pcts_p, w, color=GOLD, label='Post-Launch', zorder=2)

ax_sc.set_xticks(x)
ax_sc.set_xticklabels([f'Score {s}' for s in score_vals], fontsize=8)
ax_sc.set_ylabel('% of Leads', fontsize=8, color=MID_GRAY)
ax_sc.yaxis.set_tick_params(labelsize=7)
ax_sc.legend(fontsize=7.5, frameon=False)
ax_sc.spines['bottom'].set_visible(True)
ax_sc.spines['bottom'].set_color(LIGHT_SIL)
title_style(ax_sc, 'Score Distribution\n(Baseline vs. Post-Launch)')

# ── Bottom right: Brand split ─────────────────────────────────────────────
ax_br = fig2.add_subplot(gs[1, 2])
ax_br.set_facecolor(BG)

b_tt_pct = b_tt / (b_tt + b_tc) * 100
b_tc_pct = b_tc / (b_tt + b_tc) * 100
p_tt_pct = p_tt / (p_tt + p_tc) * 100 if (p_tt + p_tc) > 0 else 0
p_tc_pct = p_tc / (p_tt + p_tc) * 100 if (p_tt + p_tc) > 0 else 0

categories = ['Baseline', 'Post-Launch']
tt_vals = [b_tt_pct, p_tt_pct]
tc_vals = [b_tc_pct, p_tc_pct]

bars1 = ax_br.bar(categories, tt_vals, color=NAVY, label='Travel Trailer', zorder=2)
bars2 = ax_br.bar(categories, tc_vals, bottom=tt_vals, color=GOLD, label='Touring Coach', zorder=2)

for bar, v in zip(bars1, tt_vals):
    ax_br.text(bar.get_x() + bar.get_width()/2, v/2, f'{v:.0f}%',
               ha='center', va='center', fontsize=9, color=WHITE, fontweight='bold')
for bar, v, b in zip(bars2, tc_vals, tt_vals):
    ax_br.text(bar.get_x() + bar.get_width()/2, b + v/2, f'{v:.0f}%',
               ha='center', va='center', fontsize=9, color=NAVY, fontweight='bold')

ax_br.set_ylim(0, 115)
ax_br.set_ylabel('% Share', fontsize=8, color=MID_GRAY)
ax_br.yaxis.set_tick_params(labelsize=7)
ax_br.legend(fontsize=7.5, frameon=False)
ax_br.spines['bottom'].set_visible(True)
ax_br.spines['bottom'].set_color(LIGHT_SIL)
title_style(ax_br, 'Brand Split\n(TT vs. TC)')

bottom_bar(fig2, 'Pre-Launch Baseline  ·  AIMBase Data  ·  Element Three')
fig2.savefig('/home/user/airstream-lead-distro-analysis/slide2_baseline.png',
             dpi=150, bbox_inches='tight')
plt.close(fig2)
print('Slide 2 done.')

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Forecast vs. Actual
# ════════════════════════════════════════════════════════════════════════════
print('Building slide 3...')
fig3 = plt.figure(figsize=(16, 9), facecolor=WHITE)
add_logo_area(fig3)

gs3 = gridspec.GridSpec(2, 2, figure=fig3, left=0.05, right=0.97,
                        top=0.88, bottom=0.1, hspace=0.5, wspace=0.35)

# ── Top left: Scenario matrix bar chart ──────────────────────────────────
ax_scen = fig3.add_subplot(gs3[0, 0])
ax_scen.set_facecolor(BG)

scenarios = [
    'Baseline\n(Pre-Launch)',
    'Form Elim\nOnly (–7%)',
    'Elim +\n50% CB',
    'Elim +\n30% CB',
    'Elim + CB +\nScore 2+',
    'Elim + CB +\nScore 3+',
]
scen_vals = [19200, 17891, 14715, 13444, 5208, 1263]
scen_colors = [NAVY, GOLD, SILVER, MID_GRAY, '#E67E22', RED]

# Add actual run rate marker
actual_val = int(jun_monthly_rate)

bars_s = ax_scen.barh(range(len(scenarios)), scen_vals, color=scen_colors,
                       height=0.55, zorder=2)
for i, (bar, val) in enumerate(zip(bars_s, scen_vals)):
    ax_scen.text(val + 150, bar.get_y() + bar.get_height()/2,
                 f'{val:,}', va='center', ha='left', fontsize=8, color=MID_GRAY)

# Actual line
ax_scen.axvline(actual_val, color=RED, linewidth=2, linestyle='--', zorder=4)
ax_scen.text(actual_val + 200, len(scenarios) - 0.5, f'Actual\n~{actual_val:,}/mo',
             fontsize=7.5, color=RED, va='top', fontweight='bold')

ax_scen.set_yticks(range(len(scenarios)))
ax_scen.set_yticklabels(scenarios, fontsize=7.5)
ax_scen.set_xlabel('Leads / Month', fontsize=8, color=MID_GRAY)
ax_scen.xaxis.set_tick_params(labelsize=7)
ax_scen.spines['bottom'].set_visible(True)
ax_scen.spines['bottom'].set_color(LIGHT_SIL)
title_style(ax_scen, 'Forecast Scenario Matrix',
            'Where does June 2026 land?')

# ── Top right: Key metrics comparison ────────────────────────────────────
ax_kpi = fig3.add_subplot(gs3[0, 1])
ax_kpi.axis('off')
ax_kpi.set_facecolor(BG)

title_style(ax_kpi, 'Forecast vs. Actual — Key Metrics')

kpi_data = [
    ('Total leads / mo',     f'{PDF_BASELINE:,}',  f'{PDF_FORECAST:,}',   f'~{int(jun_monthly_rate):,}'),
    ('Per dealer / mo',       '231',                '216',                  f'{int(jun_monthly_rate/DEALERS)}'),
    ('External Paid share',   '~60%',               '~60%',                f'{p_src.get("External Paid" + chr(10) + "(Meta)", 0):.0f}%'),
    ('Score 3+ rate',         '8.0%',               'Flat-to-up',          f'{post_s3:.1f}%'),
    ('TT share',              f'{b_tt_pct:.0f}%',   '~66%',                f'{p_tt_pct:.0f}%'),
]

col_headers = ['Metric', 'Baseline', 'Forecast', 'Actual (June \'26)']
col_x = [0.0, 0.38, 0.58, 0.78]
col_w = [0.35, 0.18, 0.18, 0.22]

for j, h in enumerate(col_headers):
    ax_kpi.text(col_x[j] + col_w[j]/2, 0.93, h, fontsize=8.5, fontweight='bold',
                color=NAVY, ha='center', va='top', transform=ax_kpi.transAxes)

ax_kpi.plot([0, 1], [0.90, 0.90], color=NAVY, linewidth=1, transform=ax_kpi.transAxes,
            clip_on=False)

for i, row in enumerate(kpi_data):
    y = 0.82 - i * 0.14
    bg_col = BG if i % 2 == 0 else '#E8EDF0'
    rect = FancyBboxPatch((0, y - 0.06), 1, 0.12, transform=ax_kpi.transAxes,
                          facecolor=bg_col, edgecolor='none',
                          boxstyle='square,pad=0')
    ax_kpi.add_patch(rect)
    for j, val in enumerate(row):
        color = NAVY
        if j == 3:  # Actual column
            # Color code based on vs. forecast
            if i == 0:  # total leads
                color = RED if jun_monthly_rate < PDF_FORECAST * 0.95 else GREEN
            elif i == 3:  # score 3+
                color = GREEN if post_s3 > 8.0 else RED
        ax_kpi.text(col_x[j] + col_w[j]/2, y, val, fontsize=8,
                    color=color, ha='center', va='center',
                    transform=ax_kpi.transAxes,
                    fontweight='bold' if j == 3 else 'normal')

# ── Bottom left: Monthly trend with forecast band ────────────────────────
ax_trend2 = fig3.add_subplot(gs3[1, :])
ax_trend2.set_facecolor(BG)

# All monthly data (pre + post)
all_months_pre = pre_all[(pre_all['Lead Date'] >= '2025-03-01') &
                          (pre_all['Lead Date'] < '2026-06-01')].copy()
all_months_pre['month'] = all_months_pre['Lead Date'].dt.to_period('M')
monthly_all = all_months_pre.groupby('month').size().reset_index(name='leads')
monthly_all['month_dt'] = monthly_all['month'].dt.to_timestamp()

# Post June
post_jun_count = len(post_jun)
post_jun_projected = int(jun_monthly_rate)

# Plot pre-launch bars
x_pre = range(len(monthly_all))
bars_pre = ax_trend2.bar(x_pre, monthly_all['leads'], color=NAVY, width=0.6,
                          label='Actual (Pre-Launch)', zorder=2)

# Add post-launch bar (projected June)
n = len(monthly_all)
ax_trend2.bar(n, post_jun_projected, color=RED, width=0.6, zorder=2, alpha=0.85,
               label=f'Post-Launch (Jun projected ~{post_jun_projected:,}/mo)', hatch='//')

# Forecast band
ax_trend2.axhspan(PDF_FORECAST * 0.93, PDF_FORECAST * 1.07, alpha=0.12,
                   color=GOLD, zorder=1, label='Forecast range (~17,900/mo)')
ax_trend2.axhline(PDF_FORECAST, color=GOLD, linewidth=1.5, linestyle='--', zorder=3)

all_labels = [m.strftime('%b\n%Y') for m in monthly_all['month_dt']] + ['Jun\n2026*']
ax_trend2.set_xticks(range(n + 1))
ax_trend2.set_xticklabels(all_labels, fontsize=7.5, color=MID_GRAY)

ax_trend2.set_ylabel('Dealer Leads', fontsize=9, color=MID_GRAY)
ax_trend2.yaxis.set_tick_params(labelsize=8)
ax_trend2.legend(fontsize=8, frameon=False, loc='upper left')

ax_trend2.text(n, post_jun_projected + 400, f'~{post_jun_projected:,}',
               ha='center', va='bottom', fontsize=8, color=RED, fontweight='bold')
ax_trend2.text(n, post_jun_projected - 1800,
               f'({(post_jun_projected/PDF_BASELINE-1)*100:.0f}% vs. baseline)',
               ha='center', va='bottom', fontsize=7.5, color=RED)

ax_trend2.spines['bottom'].set_visible(True)
ax_trend2.spines['bottom'].set_color(LIGHT_SIL)

title_style(ax_trend2, 'Monthly Lead Volume — Baseline Through Post-Launch',
            '*June 2026 is a projected full-month rate based on 18 days of actual data (May 28–June 18)')

bottom_bar(fig3, 'Forecast vs. Actual  ·  AIMBase Data  ·  Element Three')
fig3.savefig('/home/user/airstream-lead-distro-analysis/slide3_forecast_actual.png',
             dpi=150, bbox_inches='tight')
plt.close(fig3)
print('Slide 3 done.')

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — Quality, Source Mix & What to Watch
# ════════════════════════════════════════════════════════════════════════════
print('Building slide 4...')
fig4 = plt.figure(figsize=(16, 9), facecolor=WHITE)
add_logo_area(fig4)

gs4 = gridspec.GridSpec(2, 3, figure=fig4, left=0.05, right=0.97,
                         top=0.88, bottom=0.1, hspace=0.5, wspace=0.38)

# ── Top left: Score 3+ rate comparison ───────────────────────────────────
ax_q = fig4.add_subplot(gs4[0, 0])
ax_q.set_facecolor(BG)

groups = ['Baseline\n(8.0%\nforecast)', 'Post-Launch\nActual']
vals_q = [baseline_s3, post_s3]
colors_q = [NAVY, GREEN if post_s3 >= 8.0 else RED]

bq = ax_q.bar(groups, vals_q, color=colors_q, width=0.45, zorder=2)
ax_q.axhline(8.0, color=GOLD, linewidth=1.5, linestyle='--', alpha=0.8)
ax_q.text(1.5, 8.15, 'Forecast floor\n(8.0%)', fontsize=7, color=GOLD, ha='right')

for bar, v in zip(bq, vals_q):
    ax_q.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
               f'{v:.1f}%', ha='center', va='bottom', fontsize=11,
               fontweight='bold', color=MID_GRAY)

ax_q.set_ylim(0, max(vals_q) * 1.35)
ax_q.set_ylabel('Score 3+ Rate (%)', fontsize=8, color=MID_GRAY)
ax_q.yaxis.set_tick_params(labelsize=7)
ax_q.spines['bottom'].set_visible(True)
ax_q.spines['bottom'].set_color(LIGHT_SIL)
title_style(ax_q, 'Lead Quality\n(Score 3+ Rate)')

quality_label = '▲ Quality thesis holding' if post_s3 >= 8.0 else '▼ Score 3+ rate below baseline'
ax_q.text(0.5, -0.28, quality_label, transform=ax_q.transAxes, fontsize=8,
           color=GREEN if post_s3 >= 8.0 else RED, ha='center', fontweight='bold')

# ── Top center: Source mix comparison bar ────────────────────────────────
ax_mix = fig4.add_subplot(gs4[0, 1])
ax_mix.set_facecolor(BG)

src_order = ['External Paid\n(Meta)', 'Direct Traffic', 'Organic Search',
             'Email Marketing', 'Paid Search', 'Other']
b_vals = [b_src.get(s, 0) for s in src_order]
p_vals = [p_src.get(s, 0) for s in src_order]

x_m = np.arange(len(src_order))
wm = 0.38
ax_mix.bar(x_m - wm/2, b_vals, wm, color=NAVY, label='Baseline', zorder=2)
ax_mix.bar(x_m + wm/2, p_vals, wm, color=GOLD, label='Post-Launch', zorder=2)

ax_mix.set_xticks(x_m)
ax_mix.set_xticklabels([s.replace('\n', ' ') for s in src_order], fontsize=6.5,
                         rotation=25, ha='right')
ax_mix.set_ylabel('% Share', fontsize=8, color=MID_GRAY)
ax_mix.yaxis.set_tick_params(labelsize=7)
ax_mix.legend(fontsize=7.5, frameon=False)
ax_mix.spines['bottom'].set_visible(True)
ax_mix.spines['bottom'].set_color(LIGHT_SIL)
title_style(ax_mix, 'Source Mix\n(Baseline vs. Post-Launch)')

# ── Top right: Per-dealer volume ─────────────────────────────────────────
ax_pd = fig4.add_subplot(gs4[0, 2])
ax_pd.set_facecolor(BG)

pd_vals = [231, 216, int(jun_monthly_rate / DEALERS)]
pd_labels = ['Baseline', 'Forecast', 'Post-Launch\n(Jun rate)']
pd_colors = [NAVY, GOLD, RED if pd_vals[2] < 216 else GREEN]

bpd = ax_pd.bar(pd_labels, pd_vals, color=pd_colors, width=0.45, zorder=2)
for bar, v in zip(bpd, pd_vals):
    ax_pd.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
               str(v), ha='center', va='bottom', fontsize=12,
               fontweight='bold', color=MID_GRAY)

ax_pd.set_ylabel('Leads / Dealer / Month', fontsize=8, color=MID_GRAY)
ax_pd.yaxis.set_tick_params(labelsize=7)
ax_pd.spines['bottom'].set_visible(True)
ax_pd.spines['bottom'].set_color(LIGHT_SIL)
title_style(ax_pd, 'Per-Dealer Volume\n(Leads / Dealer / Month)')

# ── Bottom: What to watch ─────────────────────────────────────────────────
ax_watch = fig4.add_subplot(gs4[1, :])
ax_watch.axis('off')
ax_watch.set_facecolor('#F0F4F6')

title_style(ax_watch, 'What to Watch Next  ·  Diagnostic Checklist')

pct_vs_baseline = (jun_monthly_rate / PDF_BASELINE - 1) * 100
pct_vs_forecast = (jun_monthly_rate / PDF_FORECAST - 1) * 100

watch_items = []

if pct_vs_forecast < -7:
    watch_items.append(('⚠', RED, 'Volume below forecast floor',
                        f'June pace (~{int(jun_monthly_rate):,}/mo) is {pct_vs_forecast:.0f}% vs. forecast ~17,900. '
                        'Check: was a brochure checkbox added? Did brochure CVR drop from longer form? '
                        'Did new-site top-of-funnel traffic fall?'))
else:
    watch_items.append(('✓', GREEN, 'Volume in forecast range',
                        f'June pace (~{int(jun_monthly_rate):,}/mo) is within expected –7% band.'))

if post_s3 >= 8.0:
    watch_items.append(('✓', GREEN, '"Fewer but better leads" thesis holding',
                        f'Post-launch Score 3+ rate ({post_s3:.1f}%) is at or above the 8.0% baseline. '
                        'Higher-intent behavior is surfacing as expected.'))
else:
    watch_items.append(('⚠', RED, 'Score 3+ rate below baseline',
                        f'Post-launch Score 3+ rate ({post_s3:.1f}%) is below the 8.0% baseline. '
                        'Score inflation may not be shifting from forms to on-site behaviors.'))

watch_items.append(('→', MID_GRAY, 'Seasonality: compare June-to-June for cleaner read',
                    'June 2025 was 28,693 leads — the annual peak. June 2026 rate reflects '
                    'post-launch + seasonal overlap. Wait for full month + 60-90 day window.'))

watch_items.append(('→', MID_GRAY, 'TC dealers may see disproportionate impact',
                    'Touring Coach has lower Score 3+ (5.1% vs 9.5% TT) and lower configurator '
                    'opt-in (0.7% vs 2.7% TT). Segment by brand before drawing conclusions.'))

for i, (icon, col, header, detail) in enumerate(watch_items):
    x = 0.02 + (i % 2) * 0.5
    y = 0.82 - (i // 2) * 0.42
    ax_watch.text(x, y, f'{icon}  {header}', fontsize=9, color=col,
                   fontweight='bold', va='top', transform=ax_watch.transAxes)
    ax_watch.text(x + 0.02, y - 0.12, detail, fontsize=7.5, color=MID_GRAY,
                   va='top', transform=ax_watch.transAxes, wrap=True,
                   multialignment='left')

bottom_bar(fig4, 'Lead Quality & Diagnostics  ·  AIMBase Data  ·  Element Three')
fig4.savefig('/home/user/airstream-lead-distro-analysis/slide4_quality_watch.png',
             dpi=150, bbox_inches='tight')
plt.close(fig4)
print('Slide 4 done.')

# ── Assemble into PDF ──────────────────────────────────────────────────────
print('Assembling PDF...')
from PIL import Image

slides = [
    '/home/user/airstream-lead-distro-analysis/slide1_title.png',
    '/home/user/airstream-lead-distro-analysis/slide2_baseline.png',
    '/home/user/airstream-lead-distro-analysis/slide3_forecast_actual.png',
    '/home/user/airstream-lead-distro-analysis/slide4_quality_watch.png',
]

imgs = [Image.open(s).convert('RGB') for s in slides]
imgs[0].save(
    '/home/user/airstream-lead-distro-analysis/airstream_lead_distro_analysis.pdf',
    save_all=True, append_images=imgs[1:],
    resolution=150
)
print('PDF saved!')
print(f'\nKey numbers summary:')
print(f'  Baseline avg/mo (PDF): {PDF_BASELINE:,}')
print(f'  Forecast (–7%): {PDF_FORECAST:,}')
print(f'  June 2026 run rate: {int(jun_monthly_rate):,}')
print(f'  vs. baseline: {pct_vs_baseline:.1f}%')
print(f'  vs. forecast: {pct_vs_forecast:.1f}%')
print(f'  Score 3+ baseline: {baseline_s3:.1f}%')
print(f'  Score 3+ post: {post_s3:.1f}%')
