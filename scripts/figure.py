#!/usr/bin/env python3
"""Figure 1: symptom distribution of included fixes. Usage: python3 figure.py <kaggle_dir>"""
import json, sys, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = sys.argv[1]; R = json.load(open(f"{D}/analysis/results.json"))
order = ["SILENT", "UNSAFE", "MISLEAD", "REJECT", "TOOLS", "UNAVAIL", "OPERATOR", "UNKNOWN"]
grp = {"SILENT": 0, "UNSAFE": 0, "MISLEAD": 0, "REJECT": 1, "TOOLS": 1, "UNAVAIL": 1, "OPERATOR": 2, "UNKNOWN": 2}
col = ["#eb6834", "#2a78d6", "#b9b8b2"]
names = ["Response cannot be trusted by the agent (success-looking or misleading)", "Agent sees an explicit failure", "Not agent-facing / not inferable"]
n = [R["symptom"][s]["n"] for s in order]
fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
fig.patch.set_facecolor("#fcfcfb"); ax.set_facecolor("#fcfcfb")
y = list(range(len(order)))[::-1]
for yi, s, v in zip(y, order, n):
    ax.barh(yi, v, color=col[grp[s]], height=0.62, edgecolor="#fcfcfb", linewidth=2)
    ax.text(v + 0.8, yi, str(v), va="center", fontsize=8, color="#0b0b0b")
ax.set_yticks(y); ax.set_yticklabels(order, fontsize=8, color="#0b0b0b")
ax.set_xlabel("Included defect fixes (n = %d); headline denominator = %d (orange + blue)" % (R["included_total"], R["agent_facing_known"]), fontsize=8, color="#52514e")
for s in ["top", "right"]: ax.spines[s].set_visible(False)
for s in ["left", "bottom"]: ax.spines[s].set_color("#b9b8b2")
ax.tick_params(colors="#52514e", labelsize=8); ax.grid(axis="x", color="#e6e5e0", linewidth=0.6); ax.set_axisbelow(True)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=c, label=l) for c, l in zip(col, names)], fontsize=7, frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=1)
plt.tight_layout(); plt.savefig(f"{D}/analysis/fig1_symptoms.png", facecolor=fig.get_facecolor())
