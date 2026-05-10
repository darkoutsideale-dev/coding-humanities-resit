import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os


# ---------- helper function ----------
def add_box(ax, x, y, w, h, text, fontsize=11):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02",
        linewidth=1.5,
        edgecolor="black",
        facecolor="#dceeff"
    )
    ax.add_patch(box)
    ax.text(
        x + w / 2, y + h / 2,
        text,
        ha="center", va="center",
        fontsize=fontsize,
        wrap=True
    )


def add_arrow(ax, x1, y1, x2, y2):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", lw=1.5)
    )


# ---------- figure ----------
fig, ax = plt.subplots(figsize=(10, 14))
ax.set_xlim(0, 10)
ax.set_ylim(0, 16)
ax.axis("off")

ax.text(
    5, 15.4,
    "Mini Project 1 Workflow: Loading, Cleaning, and Examining the labMT Dataset",
    ha="center", va="center",
    fontsize=15, fontweight="bold"
)

# box positions
w, h = 6.8, 1.0
x = 1.6

steps = [
    (13.8, "Raw input file:\nData_Set_S1.txt (labMT 1.0 dataset)"),
    (12.2, "Load the tab-delimited file into pandas"),
    (10.6, "Skip the metadata/comment lines\nat the top of the file"),
    (9.0, "Replace '--' with NaN\n(to mark missing ranks properly)"),
    (7.4, "Convert numeric columns to\ninteger / float types"),
    (5.8, "Check dataset structure:\nshape, column names, data types,\nand missing values"),
    (4.2, "Save cleaned dataset as:\ndata/clean/labMT_clean.csv"),
    (2.6, "Create supporting outputs:\n- data dictionary table\n- missing values table\n- duplicated words check\n- random sample\n- top 10 positive / negative words"),
    (1.0, "Generate figures and write README\nfor interpretation and reproducibility")
]

# draw boxes
for y, text in steps:
    add_box(ax, x, y, w, h, text)

# draw arrows
for i in range(len(steps) - 1):
    y_current = steps[i][0]
    y_next = steps[i + 1][0]
    add_arrow(ax, 5, y_current, 5, y_next + h)

# save figure
os.makedirs("figures", exist_ok=True)
output_path = "figures/mini1_workflow_diagram.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.close()

print(f"Workflow figure saved to {output_path}")