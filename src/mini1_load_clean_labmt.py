import pandas as pd


def load_and_clean_labmt(path):
    df = pd.read_csv(
        path,
        sep="\t",
        skiprows=2,
        engine="python"
    )

    df = df.replace("--", pd.NA)

    numeric_cols = df.columns[1:]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    return df


if __name__ == "__main__":
    df = load_and_clean_labmt("data/raw/Data_Set_S1.txt")

    print("Shape:", df.shape)
    print("\nData types:")
    print(df.dtypes)
    print("\nMissing values:")
    print(df.isna().sum())

    df.to_csv("data/clean/labMT_clean.csv", index=False)
    print("\nCleaned dataset saved to data/clean/labMT_clean.csv")