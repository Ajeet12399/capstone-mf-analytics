import pandas as pd
import glob
import os


def load_and_inspect_csvs(folder_path="data/raw"):
    """Load all CSV files and display basic inspection details."""

    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    csv_files.sort()

    if not csv_files:
        print(f"No CSV files found in: {folder_path}")
        return {}

    dataframes = {}

    print(f"\nFound {len(csv_files)} CSV files in '{folder_path}'")

    for file_path in csv_files:

        file_name = os.path.splitext(os.path.basename(file_path))[0]

        print("\n" + "=" * 60)
        print(f"Dataset: {file_name}")
        print("=" * 60)

        try:
            df = pd.read_csv(file_path)
            dataframes[file_name] = df

            print(f"\nShape: {df.shape}")

            print("\nColumns:")
            print(df.columns.tolist())

            print("\nData types:")
            print(df.dtypes)

            print("\nFirst 5 rows:")
            print(df.head())

            print("\nMissing values per column:")
            print(df.isnull().sum())

            print(f"\nDuplicate rows: {df.duplicated().sum()}")

        except Exception as e:
            print(f"\nERROR loading {file_name}: {e}")

    return dataframes


def analyze_datasets(all_data):
    """Perform validation and consistency checks on the datasets."""

    print("\n" + "=" * 60)
    print("DATASET ANALYSIS")
    print("=" * 60)


    fund_master = all_data["01_fund_master"]

    print("\n--- FUND MASTER ANALYSIS ---")

    print("\nFund houses:")
    print(fund_master["fund_house"].unique())

    print("\nCategories:")
    print(fund_master["category"].unique())

    print("\nSub-categories:")
    print(fund_master["sub_category"].unique())

    print("\nRisk categories:")
    print(fund_master["risk_category"].unique())

    print("\nSEBI category codes:")
    print(fund_master["sebi_category_code"].unique())



    print("\n" + "=" * 60)
    print("FUND MASTER vs NAV HISTORY")
    print("=" * 60)

    nav_history = all_data["02_nav_history"]

    fund_codes = set(fund_master["amfi_code"].dropna())
    nav_codes = set(nav_history["amfi_code"].dropna())

    missing_in_nav = fund_codes - nav_codes
    missing_in_master = nav_codes - fund_codes

    print(f"\nFund master schemes: {len(fund_codes)}")
    print(f"NAV history schemes: {len(nav_codes)}")

    print(
        f"\nSchemes in fund_master but missing NAV history: "
        f"{missing_in_nav}"
    )

    print(
        f"\nSchemes with NAV history but missing from fund_master: "
        f"{missing_in_master}"
    )



    print("\n" + "=" * 60)
    print("NAV HISTORY COVERAGE")
    print("=" * 60)

    rows_per_scheme = nav_history.groupby("amfi_code").size()

    print("\nNAV records per scheme statistics:")
    print(rows_per_scheme.describe())

    median_rows = rows_per_scheme.median()

    low_history_schemes = rows_per_scheme[
        rows_per_scheme < median_rows * 0.5
    ]

    print("\nSchemes with unusually little NAV history:")
    
    if low_history_schemes.empty:
        print("None")
    else:
        print(low_history_schemes)



    print("\n" + "=" * 60)
    print("INVESTOR TRANSACTION VALIDATION")
    print("=" * 60)

    investor_txns = all_data["08_investor_transactions"]

    txn_codes = set(investor_txns["amfi_code"].dropna())

    transactions_not_in_master = txn_codes - fund_codes

    print(
        "\nTransaction schemes not in fund_master:",
        transactions_not_in_master
    )

    if len(transactions_not_in_master) == 0:
        print("All transaction scheme codes exist in fund_master.")



if __name__ == "__main__":

    
    all_data = load_and_inspect_csvs()

    print("\n" + "=" * 60)
    print("DATA INGESTION SUMMARY")
    print("=" * 60)

    print(f"Total datasets loaded: {len(all_data)}")
    print(f"Dataset names: {list(all_data.keys())}")

    if all_data:
        analyze_datasets(all_data)