from pathlib import Path
import re
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

LABMT_PATH = ROOT / "data" / "clean" / "labMT_clean.csv"
IMDB_PATH = ROOT / "data" / "processed" / "imdb_reviews_processed.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "imdb_reviews_scored.csv"


def tokenize(text):
    """
    Convert review text into lowercase word tokens.
    Only alphabetic words are kept.
    """
    return re.findall(r"[a-z]+", str(text).lower())


def score_review(text, labmt_scores):
    tokens = tokenize(text)

    matched_scores = [
        labmt_scores[token]
        for token in tokens
        if token in labmt_scores
    ]

    matched_token_count = len(matched_scores)

    if matched_token_count == 0:
        mean_happiness = None
    else:
        mean_happiness = sum(matched_scores) / matched_token_count

    return matched_token_count, mean_happiness


def main():
    print("Loading labMT lexicon...")
    labmt = pd.read_csv(LABMT_PATH)

    labmt_scores = dict(
        zip(labmt["word"], labmt["happiness_average"])
    )

    print("Loading IMDb processed reviews...")
    reviews = pd.read_csv(IMDB_PATH)

    matched_counts = []
    mean_scores = []

    print("Scoring IMDb reviews with labMT...")

    for i, text in enumerate(reviews["text"]):
        matched_count, mean_score = score_review(text, labmt_scores)

        matched_counts.append(matched_count)
        mean_scores.append(mean_score)

        if (i + 1) % 5000 == 0:
            print(f"Scored {i + 1} reviews...")

    reviews["matched_token_count"] = matched_counts
    reviews["mean_happiness"] = mean_scores

    reviews.to_csv(OUTPUT_PATH, index=False)

    print("\nScored IMDb dataset saved.")
    print("Shape:", reviews.shape)
    print("Saved to:", OUTPUT_PATH)

    print("\nMean happiness by sentiment:")
    print(reviews.groupby("sentiment")["mean_happiness"].mean())

    print("\nMatched token count summary:")
    print(reviews["matched_token_count"].describe())


if __name__ == "__main__":
    main()