from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # avoid display issues
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ----------------------------
# Paths
# ----------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "clean" / "labMT_clean.csv"
FIG_DIR = ROOT / "figures"
TABLE_DIR = ROOT / "tables"

FIG_DIR.mkdir(exist_ok=True)
TABLE_DIR.mkdir(exist_ok=True)

# ----------------------------
# Load data
# ----------------------------
df = pd.read_csv(DATA_PATH)

rank_cols = ["twitter_rank", "google_rank", "nyt_rank", "lyrics_rank"]

# ----------------------------
# Save some useful tables
# ----------------------------

# Data dictionary table
data_dict = pd.DataFrame({
    "column": df.columns,
    "dtype": [str(df[col].dtype) for col in df.columns],
    "missing_values": [int(df[col].isna().sum()) for col in df.columns]
})
data_dict.to_csv(TABLE_DIR / "mini1_data_dictionary.csv", index=False)

# Random sample table
df.sample(15, random_state=42).to_csv(TABLE_DIR / "mini1_random_sample_15_rows.csv", index=False)

# Top positive / negative words
top_positive = df.nlargest(10, "happiness_average")[["word", "happiness_average"]].copy()
top_negative = df.nsmallest(10, "happiness_average")[["word", "happiness_average"]].copy()

top_positive.to_csv(TABLE_DIR / "mini1_top_10_positive_words.csv", index=False)
top_negative.to_csv(TABLE_DIR / "mini1_top_10_negative_words.csv", index=False)

# Missing values table
missing_table = df.isna().sum().reset_index()
missing_table.columns = ["column", "missing_values"]
missing_table.to_csv(TABLE_DIR / "mini1_missing_values.csv", index=False)

# Summary stats
summary_stats = pd.DataFrame({
    "metric": [
        "rows", "columns", "mean_happiness", "median_happiness",
        "std_happiness", "min_happiness", "max_happiness",
        "5th_percentile", "95th_percentile", "duplicate_words"
    ],
    "value": [
        int(df.shape[0]),
        int(df.shape[1]),
        df["happiness_average"].mean(),
        df["happiness_average"].median(),
        df["happiness_average"].std(),
        df["happiness_average"].min(),
        df["happiness_average"].max(),
        df["happiness_average"].quantile(0.05),
        df["happiness_average"].quantile(0.95),
        int(df["word"].duplicated().sum())
    ]
})
summary_stats.to_csv(TABLE_DIR / "mini1_summary_statistics.csv", index=False)

# Save a short sanity check txt file
with open(TABLE_DIR / "mini1_sanity_check_summary.txt", "w", encoding="utf-8") as f:
    f.write("Mini Project 1 sanity checks\n")
    f.write("----------------------------\n")
    f.write(f"Shape: {df.shape}\n")
    f.write(f"Duplicate words: {df['word'].duplicated().sum()}\n")
    f.write(f"Missing values by column:\n{df.isna().sum().to_string()}\n\n")
    f.write("Top 10 positive words:\n")
    f.write(top_positive.to_string(index=False))
    f.write("\n\nTop 10 negative words:\n")
    f.write(top_negative.to_string(index=False))

# ----------------------------
# Figure 1: Distribution of happiness average
# ----------------------------
mean_val = df["happiness_average"].mean()
median_val = df["happiness_average"].median()
std_val = df["happiness_average"].std()
p5 = df["happiness_average"].quantile(0.05)
p95 = df["happiness_average"].quantile(0.95)
n = len(df)

plt.figure(figsize=(10, 6))
counts, bins, patches = plt.hist(
    df["happiness_average"],
    bins=35,
    density=True,
    alpha=0.8,
    edgecolor="black"
)

# Add lines
plt.axvline(mean_val, linewidth=2, label="Mean")
plt.axvline(median_val, linewidth=2, linestyle="--", label="Median")
plt.axvline(mean_val - std_val, linewidth=1.8, linestyle=":", label="Mean ± 1 SD")
plt.axvline(mean_val + std_val, linewidth=1.8, linestyle=":")

# simple smooth line using rolling average of histogram heights
bin_centers = 0.5 * (bins[:-1] + bins[1:])
smooth_counts = pd.Series(counts).rolling(window=3, center=True, min_periods=1).mean()
plt.plot(bin_centers, smooth_counts, linewidth=2)

stats_text = (
    f"n = {n}\n"
    f"Mean = {mean_val:.2f}\n"
    f"Median = {median_val:.2f}\n"
    f"SD = {std_val:.2f}\n"
    f"5th %ile = {p5:.2f}\n"
    f"95th %ile = {p95:.2f}"
)

plt.text(
    0.03, 0.97, stats_text,
    transform=plt.gca().transAxes,
    va="top",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.9)
)

plt.title("Distribution of happiness average in labMT 1.0")
plt.xlabel("Happiness average (1-9)")
plt.ylabel("Density")
plt.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "mini1_fig1_happiness_distribution.png", dpi=300)
plt.close()

# ----------------------------
# Figure 2: Top 10 most positive words
# ----------------------------
top_pos_plot = df.nlargest(10, "happiness_average")[["word", "happiness_average"]]
top_pos_plot = top_pos_plot.sort_values("happiness_average")

plt.figure(figsize=(9, 6))
bars = plt.barh(top_pos_plot["word"], top_pos_plot["happiness_average"], edgecolor="black")
plt.title("Top 10 most positive words in labMT")
plt.xlabel("Happiness average")
plt.ylabel("Word")

for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.03, bar.get_y() + bar.get_height()/2, f"{width:.2f}", va="center")

plt.xlim(0, max(top_pos_plot["happiness_average"]) + 0.6)
plt.tight_layout()
plt.savefig(FIG_DIR / "mini1_fig2_top_10_positive_words.png", dpi=300)
plt.close()

# ----------------------------
# Figure 3: Top 10 most negative words
# ----------------------------
top_neg_plot = df.nsmallest(10, "happiness_average")[["word", "happiness_average"]]
top_neg_plot = top_neg_plot.sort_values("happiness_average", ascending=True)

plt.figure(figsize=(9, 6))
bars = plt.barh(top_neg_plot["word"], top_neg_plot["happiness_average"], edgecolor="black")
plt.title("Top 10 most negative words in labMT")
plt.xlabel("Happiness average")
plt.ylabel("Word")

for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.03, bar.get_y() + bar.get_height()/2, f"{width:.2f}", va="center")

plt.xlim(0, max(top_neg_plot["happiness_average"]) + 0.6)
plt.tight_layout()
plt.savefig(FIG_DIR / "mini1_fig3_top_10_negative_words.png", dpi=300)
plt.close()

# ----------------------------
# Figure 4: Coverage and missingness of corpus rank columns
# ----------------------------
coverage = df[rank_cols].notna().sum()
missing = df[rank_cols].isna().sum()

x = np.arange(len(rank_cols))
width = 0.36

plt.figure(figsize=(10, 6))
bars1 = plt.bar(x - width/2, coverage, width, label="Words with rank", edgecolor="black")
bars2 = plt.bar(x + width/2, missing, width, label="Missing rank", edgecolor="black")

plt.xticks(x, rank_cols, rotation=20)
plt.ylabel("Number of words")
plt.xlabel("Corpus rank column")
plt.title("Corpus coverage and missingness in labMT rank columns")
plt.legend()

for bars in [bars1, bars2]:
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + 40, f"{int(h)}", ha="center", va="bottom", fontsize=9)

plt.tight_layout()
plt.savefig(FIG_DIR / "mini1_fig4_rank_coverage_missingness.png", dpi=300)
plt.close()

# ----------------------------
# Figure 5: Happiness average vs disagreement
# ----------------------------
xvals = df["happiness_average"]
yvals = df["happiness_standard_deviation"]
corr = xvals.corr(yvals)

plt.figure(figsize=(10, 6))
hb = plt.hexbin(xvals, yvals, gridsize=40, mincnt=1)
cb = plt.colorbar(hb)
cb.set_label("Number of words")

plt.title("Happiness average vs rating disagreement in labMT")
plt.xlabel("Happiness average")
plt.ylabel("Happiness standard deviation")

plt.text(
    0.03, 0.95,
    f"Correlation = {corr:.2f}",
    transform=plt.gca().transAxes,
    va="top",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.9)
)

plt.tight_layout()
plt.savefig(FIG_DIR / "mini1_fig5_happiness_vs_disagreement.png", dpi=300)
plt.close()

print("Mini Project 1 figures saved to figures/")
print("Mini Project 1 tables saved to tables/")
print("Generated files:")
print("- mini1_fig1_happiness_distribution.png")
print("- mini1_fig2_top_10_positive_words.png")
print("- mini1_fig3_top_10_negative_words.png")
print("- mini1_fig4_rank_coverage_missingness.png")
print("- mini1_fig5_happiness_vs_disagreement.png")