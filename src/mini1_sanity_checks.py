import pandas as pd


def run_sanity_checks(path):
    df = pd.read_csv(path)

    # 1. Check duplicated words
    duplicated_words_count = df["word"].duplicated().sum()

    # 2. Random sample of 15 rows
    random_sample = df.sample(15, random_state=42)

    # 3. Top 10 happiest words
    top_positive = df.sort_values(
        "happiness_average",
        ascending=False
    ).head(10)

    # 4. Top 10 least happy words
    top_negative = df.sort_values(
        "happiness_average",
        ascending=True
    ).head(10)

    print("Duplicated words:", duplicated_words_count)

    print("\nRandom sample:")
    print(random_sample)

    print("\nTop 10 happiest words:")
    print(top_positive[["word", "happiness_average"]])

    print("\nTop 10 least happy words:")
    print(top_negative[["word", "happiness_average"]])

    # Save outputs to tables folder
    random_sample.to_csv("tables/mini1_random_sample.csv", index=False)
    top_positive.to_csv("tables/mini1_top_10_positive_words.csv", index=False)
    top_negative.to_csv("tables/mini1_top_10_negative_words.csv", index=False)

    duplicated_summary = pd.DataFrame({
        "check": ["duplicated_words"],
        "count": [duplicated_words_count]
    })
    duplicated_summary.to_csv("tables/mini1_duplicated_words_check.csv", index=False)

    print("\nSanity check tables saved to tables/")


if __name__ == "__main__":
    run_sanity_checks("data/clean/labMT_clean.csv")