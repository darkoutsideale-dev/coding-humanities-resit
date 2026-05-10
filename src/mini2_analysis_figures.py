from pathlib import Path
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ----------------------------
# Paths
# ----------------------------
ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "data" / "processed" / "imdb_reviews_scored.csv"

FIG_DIR = ROOT / "figures"
TABLE_DIR = ROOT / "tables"

FIG_DIR.mkdir(exist_ok=True)
TABLE_DIR.mkdir(exist_ok=True)


# ----------------------------
# Helper functions
# ----------------------------
def bootstrap_mean_difference(pos_scores, neg_scores, n_bootstrap=5000, random_state=42):
    """
    Bootstrap the mean difference between positive and negative reviews.
    Difference is calculated as: positive mean - negative mean.
    """
    rng = np.random.default_rng(random_state)

    pos_scores = np.array(pos_scores)
    neg_scores = np.array(neg_scores)

    differences = []

    for _ in range(n_bootstrap):
        pos_sample = rng.choice(pos_scores, size=len(pos_scores), replace=True)
        neg_sample = rng.choice(neg_scores, size=len(neg_scores), replace=True)

        differences.append(pos_sample.mean() - neg_sample.mean())

    return np.array(differences)


def shorten_text(text, max_chars=350):
    """
    Shorten long review texts for readable table output.
    """
    text = str(text).replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split())

    if len(text) <= max_chars:
        return text

    return text[:max_chars] + "..."


# ----------------------------
# Main analysis
# ----------------------------
def main():
    print("Loading scored IMDb reviews...")
    df = pd.read_csv(INPUT_PATH)

    # Remove reviews without a happiness score, just in case
    df = df.dropna(subset=["mean_happiness"]).copy()

    # Make sure the order is clear
    neg = df[df["sentiment"] == "neg"].copy()
    pos = df[df["sentiment"] == "pos"].copy()

    neg_scores = neg["mean_happiness"]
    pos_scores = pos["mean_happiness"]

    neg_mean = neg_scores.mean()
    pos_mean = pos_scores.mean()
    observed_diff = pos_mean - neg_mean

    print("\nBasic result:")
    print(f"Positive mean happiness: {pos_mean:.6f}")
    print(f"Negative mean happiness: {neg_mean:.6f}")
    print(f"Observed mean difference, positive - negative: {observed_diff:.6f}")

    # ----------------------------
    # Table 2: Summary by sentiment
    # ----------------------------
    sentiment_summary = (
        df.groupby("sentiment")
        .agg(
            count=("review_id", "count"),
            mean_happiness=("mean_happiness", "mean"),
            median_happiness=("mean_happiness", "median"),
            std_happiness=("mean_happiness", "std"),
            mean_word_count=("word_count", "mean"),
            mean_matched_token_count=("matched_token_count", "mean"),
            median_matched_token_count=("matched_token_count", "median"),
        )
        .reset_index()
    )

    sentiment_summary.to_csv(TABLE_DIR / "mini2_table2_sentiment_summary.csv", index=False)

    # ----------------------------
    # Figure 7: IMDb scoring workflow
    # ----------------------------
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis("off")

    steps = [
        "Raw IMDb review files\ntrain/test folders + positive/negative labels",
        "Extract review text and metadata\nreview_id, split, sentiment, rating, word_count",
        "Create processed review dataset\ndata/processed/imdb_reviews_processed.csv",
        "Tokenize review text\nlowercase alphabetic word tokens",
        "Match review tokens to cleaned labMT lexicon\nfrom data/clean/labMT_clean.csv",
        "Calculate review-level scores\nmatched_token_count and mean_happiness",
        "Compare positive and negative reviews\nfigures, tables, bootstrap, interpretation",
    ]

    y_positions = np.linspace(0.88, 0.10, len(steps))

    for i, (step, y) in enumerate(zip(steps, y_positions), start=1):
        ax.text(
            0.5,
            y,
            f"{i}. {step}",
            ha="center",
            va="center",
            fontsize=11,
            bbox=dict(boxstyle="round,pad=0.5", edgecolor="black", facecolor="white"),
        )

        if i < len(steps):
            ax.annotate(
                "",
                xy=(0.5, y_positions[i] + 0.045),
                xytext=(0.5, y - 0.045),
                arrowprops=dict(arrowstyle="->", lw=1.5),
            )

    ax.set_title("IMDb review scoring workflow with labMT", fontsize=15, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "mini2_fig7_imdb_scoring_workflow.png", dpi=300)
    plt.close()

    # ----------------------------
    # Figure 8: Distribution by sentiment
    # ----------------------------
    plt.figure(figsize=(10, 6))

    plt.hist(
        neg_scores,
        bins=45,
        density=True,
        alpha=0.6,
        label=f"Negative reviews, mean = {neg_mean:.3f}",
        edgecolor="black",
    )

    plt.hist(
        pos_scores,
        bins=45,
        density=True,
        alpha=0.6,
        label=f"Positive reviews, mean = {pos_mean:.3f}",
        edgecolor="black",
    )

    plt.axvline(neg_mean, linestyle="--", linewidth=2)
    plt.axvline(pos_mean, linestyle="-", linewidth=2)

    plt.title("Distribution of labMT happiness scores by IMDb sentiment")
    plt.xlabel("Review-level mean happiness score")
    plt.ylabel("Density")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "mini2_fig8_happiness_distribution_by_sentiment.png", dpi=300)
    plt.close()

    # ----------------------------
    # Figure 9: Boxplot by sentiment
    # ----------------------------
    plt.figure(figsize=(8, 6))

    plt.boxplot(
        [neg_scores, pos_scores],
        labels=["Negative", "Positive"],
        showfliers=False,
    )

    plt.title("Review-level happiness scores by IMDb sentiment")
    plt.xlabel("IMDb sentiment label")
    plt.ylabel("Mean labMT happiness score")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "mini2_fig9_boxplot_by_sentiment.png", dpi=300)
    plt.close()

    # ----------------------------
    # Figure 10: Bootstrap mean difference
    # ----------------------------
    print("\nRunning bootstrap...")
    boot_diffs = bootstrap_mean_difference(pos_scores, neg_scores)

    ci_low = np.percentile(boot_diffs, 2.5)
    ci_high = np.percentile(boot_diffs, 97.5)

    bootstrap_summary = pd.DataFrame(
        {
            "metric": [
                "positive_mean",
                "negative_mean",
                "observed_difference_positive_minus_negative",
                "bootstrap_ci_low_2.5",
                "bootstrap_ci_high_97.5",
            ],
            "value": [
                pos_mean,
                neg_mean,
                observed_diff,
                ci_low,
                ci_high,
            ],
        }
    )

    bootstrap_summary.to_csv(TABLE_DIR / "mini2_table3_bootstrap_summary.csv", index=False)

    plt.figure(figsize=(10, 6))

    plt.hist(boot_diffs, bins=45, edgecolor="black", alpha=0.8)
    plt.axvline(observed_diff, linewidth=2, label=f"Observed diff = {observed_diff:.3f}")
    plt.axvline(ci_low, linestyle="--", linewidth=2, label=f"95% CI low = {ci_low:.3f}")
    plt.axvline(ci_high, linestyle="--", linewidth=2, label=f"95% CI high = {ci_high:.3f}")
    plt.axvline(0, linestyle=":", linewidth=2, label="Zero difference")

    plt.title("Bootstrap distribution of mean happiness difference")
    plt.xlabel("Mean difference: positive - negative")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "mini2_fig10_bootstrap_mean_difference.png", dpi=300)
    plt.close()
    # ----------------------------
    # Figure 11: Small balanced sample stability check
    # ----------------------------
    rng = np.random.default_rng(42)

    sample_size = 1000
    n_repeats = 500
    small_sample_diffs = []

    for _ in range(n_repeats):
        pos_sample = rng.choice(pos_scores, size=sample_size, replace=False)
        neg_sample = rng.choice(neg_scores, size=sample_size, replace=False)

        diff = pos_sample.mean() - neg_sample.mean()
        small_sample_diffs.append(diff)

    small_sample_diffs = np.array(small_sample_diffs)

    proportion_positive = (small_sample_diffs > 0).mean()

    small_sample_summary = pd.DataFrame({
        "metric": [
            "sample_size_per_group",
            "number_of_repeats",
            "mean_small_sample_difference",
            "min_difference",
            "max_difference",
            "proportion_of_samples_with_positive_difference"
        ],
        "value": [
            sample_size,
            n_repeats,
            small_sample_diffs.mean(),
            small_sample_diffs.min(),
            small_sample_diffs.max(),
            proportion_positive
        ]
    })

    small_sample_summary.to_csv(
        TABLE_DIR / "mini2_table5_small_sample_stability.csv",
        index=False
    )

    plt.figure(figsize=(10, 6))
    plt.hist(small_sample_diffs, bins=35, edgecolor="black", alpha=0.8)
    plt.axvline(0, linestyle=":", linewidth=2, label="Zero difference")
    plt.axvline(
        small_sample_diffs.mean(),
        linewidth=2,
        label=f"Mean small-sample diff = {small_sample_diffs.mean():.3f}"
    )

    plt.title("Small-sample stability of the happiness difference")
    plt.xlabel("Mean difference: positive - negative")
    plt.ylabel("Frequency across repeated samples")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "mini2_fig11_small_sample_stability.png", dpi=300)
    plt.close()
    # Figure 12: Matched token count by sentiment
    # ----------------------------
    plt.figure(figsize=(10, 6))

    plt.hist(
        neg["matched_token_count"],
        bins=50,
        alpha=0.6,
        label="Negative reviews",
        edgecolor="black",
    )

    plt.hist(
        pos["matched_token_count"],
        bins=50,
        alpha=0.6,
        label="Positive reviews",
        edgecolor="black",
    )

    plt.title("Matched labMT token count by IMDb sentiment")
    plt.xlabel("Matched token count")
    plt.ylabel("Number of reviews")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "mini2_fig12_matched_token_count_by_sentiment.png", dpi=300)
    plt.close()

    # ----------------------------
    # Figure 13: Word count vs matched token count
    # ----------------------------
    sample_for_scatter = df.sample(
        n=min(8000, len(df)),
        random_state=42,
    )

    corr_wc_match = sample_for_scatter["word_count"].corr(sample_for_scatter["matched_token_count"])

    plt.figure(figsize=(10, 6))

    for sentiment, label in [("neg", "Negative reviews"), ("pos", "Positive reviews")]:
        subset = sample_for_scatter[sample_for_scatter["sentiment"] == sentiment]

        plt.scatter(
            subset["word_count"],
            subset["matched_token_count"],
            alpha=0.35,
            s=12,
            label=label,
        )

    plt.title("Review length and labMT matched token count")
    plt.xlabel("Review word count")
    plt.ylabel("Matched labMT token count")
    plt.legend()

    plt.text(
        0.03,
        0.95,
        f"Correlation = {corr_wc_match:.2f}",
        transform=plt.gca().transAxes,
        va="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.9),
    )

    plt.tight_layout()
    plt.savefig(FIG_DIR / "mini2_fig13_word_count_vs_matched_tokens.png", dpi=300)
    plt.close()

    # ----------------------------
    # Figure 14: Rating vs mean happiness
    # ----------------------------
    rating_df = df.dropna(subset=["rating"]).copy()

    rating_summary = (
        rating_df.groupby("rating")
        .agg(
            mean_happiness=("mean_happiness", "mean"),
            count=("review_id", "count"),
        )
        .reset_index()
    )

    rating_summary.to_csv(TABLE_DIR / "mini2_rating_summary.csv", index=False)

    plt.figure(figsize=(10, 6))
    plt.plot(
        rating_summary["rating"],
        rating_summary["mean_happiness"],
        marker="o",
        linewidth=2,
    )

    for _, row in rating_summary.iterrows():
        plt.text(
            row["rating"],
            row["mean_happiness"] + 0.005,
            f"n={int(row['count'])}",
            ha="center",
            fontsize=8,
        )

    plt.title("Average labMT happiness score by IMDb rating")
    plt.xlabel("IMDb rating from filename")
    plt.ylabel("Mean labMT happiness score")
    plt.xticks(sorted(rating_summary["rating"].unique()))
    plt.tight_layout()
    plt.savefig(FIG_DIR / "mini2_fig14_happiness_by_rating.png", dpi=300)
    plt.close()

    # ----------------------------
    # Table 4: Mismatch examples
    # ----------------------------
    # Positive reviews with low labMT score
    pos_low = (
        pos.sort_values("mean_happiness", ascending=True)
        .head(5)
        .copy()
    )
    pos_low["mismatch_type"] = "positive_label_low_labMT_score"

    # Negative reviews with high labMT score
    neg_high = (
        neg.sort_values("mean_happiness", ascending=False)
        .head(5)
        .copy()
    )
    neg_high["mismatch_type"] = "negative_label_high_labMT_score"

    mismatch = pd.concat([pos_low, neg_high], ignore_index=True)

    mismatch["short_text"] = mismatch["text"].apply(lambda x: shorten_text(x, max_chars=400))

    mismatch_table = mismatch[
        [
            "mismatch_type",
            "review_id",
            "sentiment",
            "rating",
            "word_count",
            "matched_token_count",
            "mean_happiness",
            "short_text",
        ]
    ]

    mismatch_table.to_csv(TABLE_DIR / "mini2_table4_mismatch_examples.csv", index=False)

    # Save a readable text version too
    with open(TABLE_DIR / "mini2_mismatch_examples_readable.txt", "w", encoding="utf-8") as f:
        for _, row in mismatch_table.iterrows():
            f.write("=" * 80 + "\n")
            f.write(f"Mismatch type: {row['mismatch_type']}\n")
            f.write(f"Review ID: {row['review_id']}\n")
            f.write(f"Sentiment label: {row['sentiment']}\n")
            f.write(f"Rating: {row['rating']}\n")
            f.write(f"Mean happiness: {row['mean_happiness']:.3f}\n")
            f.write(f"Matched tokens: {row['matched_token_count']}\n")
            f.write(f"Text: {row['short_text']}\n\n")

    print("\nPart 2 figures saved to figures/")
    print("Part 2 tables saved to tables/")

    print("\nKey results:")
    print(f"Positive mean happiness: {pos_mean:.6f}")
    print(f"Negative mean happiness: {neg_mean:.6f}")
    print(f"Observed difference, positive - negative: {observed_diff:.6f}")
    print(f"Bootstrap 95% CI: [{ci_low:.6f}, {ci_high:.6f}]")
    print(f"Word count vs matched token correlation: {corr_wc_match:.3f}")


if __name__ == "__main__":
    main()