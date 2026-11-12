"""
Generate static preview screenshots of the Matplotlib charts
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

artifact_dir = r"C:\Users\SMRITI SHARMA\.gemini\antigravity\brain\f1421fe0-92e1-431d-9ace-75ebca3e902e"
os.makedirs(artifact_dir, exist_ok=True)

# 1. Gauge Chart
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=130)
fig.patch.set_facecolor("#1e293b")
ax.set_facecolor("#1e293b")

segments = [
    ("Underweight\n< 18.5", 10.0, 18.5, "#38bdf8"),
    ("Normal\n18.5 - 24.9", 18.5, 25.0, "#22c55e"),
    ("Overweight\n25 - 29.9", 25.0, 30.0, "#f59e0b"),
    ("Obese I\n30 - 34.9", 30.0, 35.0, "#f97316"),
    ("Obese II\n35 - 39.9", 35.0, 40.0, "#ef4444"),
    ("Obese III\n≥ 40", 40.0, 48.0, "#991b1b"),
]

bar_y = 0.4
bar_height = 0.28
for label, start, end, color in segments:
    rect = patches.FancyBboxPatch(
        (start, bar_y), end - start, bar_height,
        boxstyle="round,pad=0.01,rounding_size=0.15",
        facecolor=color, edgecolor="#1e293b", linewidth=1.5, alpha=0.9
    )
    ax.add_patch(rect)
    ax.text((start + end) / 2, bar_y + bar_height + 0.05, label, ha="center", va="bottom", fontsize=8.5, color="#f8fafc", fontweight="bold")

current_bmi = 22.86
cat_color = "#22c55e"
cat_name = "Normal Weight"

ax.annotate(
    f"You: {current_bmi:.1f} BMI\n({cat_name})",
    xy=(current_bmi, bar_y + bar_height),
    xytext=(current_bmi, bar_y + bar_height + 0.32),
    arrowprops=dict(facecolor=cat_color, edgecolor="#f8fafc", shrink=0.05, width=3.5, headwidth=9, headlength=9),
    ha="center", va="bottom", fontsize=10, fontweight="bold", color="#f8fafc",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#334155", edgecolor=cat_color, linewidth=2)
)
ax.plot([current_bmi, current_bmi], [bar_y, bar_y + bar_height], color="#ffffff", linewidth=3)
ax.set_xlim(8, 50)
ax.set_ylim(0.0, 1.1)
tick_vals = [10, 18.5, 25, 30, 35, 40, 48]
ax.set_xticks(tick_vals)
ax.set_xticklabels([str(v) for v in tick_vals], color="#f8fafc", fontsize=9)
ax.set_yticks([])
ax.set_xlabel("Body Mass Index (kg/m²)", color="#f8fafc", fontsize=10, labelpad=8)
ax.set_title("WHO Body Mass Index Classification Spectrum", color="#f8fafc", fontsize=12, pad=12, fontweight="bold")
for s in ax.spines.values():
    s.set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(artifact_dir, "preview_gauge.png"))
plt.close(fig)

# 2. Trend Chart
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=130)
fig.patch.set_facecolor("#1e293b")
ax.set_facecolor("#1e293b")

dates = ["May 01", "Jun 01", "Jul 01", "Aug 01", "Sep 01", "Oct 01"]
bmis = [25.96, 25.40, 24.69, 24.16, 23.67, 23.18]
x_indices = list(range(len(dates)))

ax.axhspan(18.5, 24.9, color="#22c55e", alpha=0.18, label="Healthy BMI Zone (18.5 - 24.9)")
ax.axhline(18.5, color="#10b981", linestyle="--", linewidth=1, alpha=0.6)
ax.axhline(24.9, color="#10b981", linestyle="--", linewidth=1, alpha=0.6)

ax.plot(x_indices, bmis, color="#6366f1", linewidth=2.5, marker="o", markersize=7, markerfacecolor="#4f46e5", markeredgecolor="#ffffff", label="Your BMI")

for x, y in zip(x_indices, bmis):
    ax.annotate(f"{y:.1f}", xy=(x, y), xytext=(0, 8), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#f8fafc")

ax.set_xticks(x_indices)
ax.set_xticklabels(dates, color="#f8fafc", fontsize=9)
ax.tick_params(axis="y", colors="#f8fafc", labelsize=9)
ax.set_ylim(18, 28)
ax.set_ylabel("BMI (kg/m²)", color="#f8fafc", fontsize=10)
ax.set_title("Historical BMI Progress & Tracking Over Time", color="#f8fafc", fontsize=12, pad=12, fontweight="bold")
ax.grid(True, linestyle="--", alpha=0.3, color="#334155")
for s in ax.spines.values():
    s.set_color("#334155")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(loc="upper right", facecolor="#334155", edgecolor="#475569", labelcolor="#f8fafc", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(artifact_dir, "preview_trend.png"))
plt.close(fig)

print("Rendered preview charts successfully!")
