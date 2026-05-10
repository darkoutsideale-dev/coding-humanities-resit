from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
IMDB_DIR = ROOT / "data" / "raw" / "aclImdb"
OUTPUT_PATH = ROOT / "data" / "processed" / "imdb_reviews_processed.csv"


def read_review_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()


def extract_rating_from_filename(file_path):
    # IMDb filenames usually look like: 12345_8.txt
    # The number after "_" is the rating.
    stem = file_path.stem
    try:
        rating = int(stem.split("_")[-1])
    except ValueError:
        rating = None
    return rating


def load_reviews(split, sentiment):
    folder = IMDB_DIR / split / sentiment
    rows = []

    for file_path in folder.glob("*.txt"):
        text = read_review_file(file_path)
        rating = extract_rating_from_filename(file_path)
        word_count = len(text.split())

        review_id = f"{split}_{sentiment}_{file_path.stem}"

        rows.append({
            "review_id": review_id,
            "split": split,
            "sentiment": sentiment,
            "rating": rating,
            "word_count": word_count,
            "text": text
        })

    return rows


def main():
    all_rows = []

    for split in ["train", "test"]:
        for sentiment in ["pos", "neg"]:
            print(f"Loading {split}/{sentiment} reviews...")
            all_rows.extend(load_reviews(split, sentiment))

    df = pd.DataFrame(all_rows)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("\nIMDb review dataset created.")
    print("Shape:", df.shape)
    print("\nSentiment counts:")
    print(df["sentiment"].value_counts())
    print("\nSplit counts:")
    print(df["split"].value_counts())
    print("\nSaved to:", OUTPUT_PATH)


if __name__ == "__main__":
    main()