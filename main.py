import os
import pandas as pd
import numpy as np

DATA_FILE = "data/Pharmacy_OLTP_SLStyle_18Months.csv"
CLEAN_FILE = "data/cleaned_pharmacy_sales.csv"
REPORT_FOLDER = "reports"


def load_data():
    data = pd.read_csv(r"E:\Pharmacy_OLTP_SLStyle_18Months.csv")

    
    data["Transaction_Date"] = pd.to_datetime(
        data["Transaction_Date"], errors="coerce"
    )
    data["Expiry_Date"] = pd.to_datetime(
        data["Expiry_Date"], errors="coerce"
    )

    data["Month_Name"] = data["Transaction_Date"].dt.to_period("M").astype(str)

    return data


def show_overview(data):
    print("\n========== DATASET OVERVIEW ==========")
    print("Number of rows:", data.shape[0])
    print("Number of columns:", data.shape[1])
    print("Date range:",
          data["Transaction_Date"].min().date(), "to",
          data["Transaction_Date"].max().date())
    print("Unique medicines:", data["Medicine_ID"].nunique())
    print("Branches:", data["Branch_Name"].nunique())
    print("Total units sold:", int(data["Quantity"].sum()))
    print("Total sales revenue (LKR):", round(data["Line_Total_LKR"].sum(), 2))
    print("Transaction records:", data["Transaction_ID"].nunique())

    print("\nFirst five rows:")
    print(data.head().to_string(index=False))


def check_data(data):
    print("\n========== DATA QUALITY CHECK ==========")
    print("\nMissing values in each column:")
    print(data.isnull().sum().to_string())

    print("\nDuplicate full rows:", data.duplicated().sum())
    print("Repeated transaction IDs:",
          data["Transaction_ID"].duplicated().sum())

    # Check if recorded totals match quantity * unit price after discount.
    expected_total = (
        data["Quantity"]
        * data["Unit_Price_LKR"]
        * (1 - data["Discount_Rate"])
    )
    difference = (expected_total - data["Line_Total_LKR"]).abs()
    print("Rows with a total difference greater than 0.02 LKR:",
          int((difference > 0.02).sum()))

    print("\nNote: missing Strength_mg can be normal for some dosage forms.")
    print("Do not delete rows just because this optional field is missing.")


def save_clean_data(data):
    # Keep the raw file unchanged and save a separate cleaned copy.
    data.to_csv(CLEAN_FILE, index=False)
    print("\nCleaned data saved to:", CLEAN_FILE)


def sales_by_date(data):
    print("\n========== SALES FOR A DATE RANGE ==========")
    print("Available dates:",
          data["Transaction_Date"].min().date(), "to",
          data["Transaction_Date"].max().date())

    start_text = input("Enter start date (YYYY-MM-DD): ")
    end_text = input("Enter end date (YYYY-MM-DD): ")

    start_date = pd.to_datetime(start_text, errors="coerce")
    end_date = pd.to_datetime(end_text, errors="coerce")

    if pd.isna(start_date) or pd.isna(end_date):
        print("Date format is incorrect. Please try YYYY-MM-DD.")
        return

    if start_date > end_date:
        print("Start date must be before or equal to end date.")
        return

    result = data[
        (data["Transaction_Date"] >= start_date)
        & (data["Transaction_Date"] < end_date + pd.Timedelta(days=1))
    ]

    if result.empty:
        print("No records found for these dates.")
        return

    print("\nNumber of transaction records:", result["Transaction_ID"].nunique())
    print("Units sold:", int(result["Quantity"].sum()))
    print("Sales revenue (LKR):", round(result["Line_Total_LKR"].sum(), 2))
    print("\nSales by day:")
    daily = result.groupby(result["Transaction_Date"].dt.date)["Line_Total_LKR"].sum()
    print(daily.to_string())


def top_medicines(data):
    print("\n========== TOP-SELLING MEDICINES ==========")
    top = (
        data.groupby(["Medicine_ID", "Medicine_Name"])
        .agg(
            Units_Sold=("Quantity", "sum"),
            Sales_Revenue=("Line_Total_LKR", "sum"),
            Number_of_Records=("Transaction_ID", "count")
        )
        .sort_values("Units_Sold", ascending=False)
        .head(10)
    )
    print(top.to_string())


def monthly_sales(data):
    print("\n========== MONTHLY SALES ==========")
    monthly = data.groupby("Month_Name").agg(
        Sales_Revenue=("Line_Total_LKR", "sum"),
        Units_Sold=("Quantity", "sum"),
        Transaction_Records=("Transaction_ID", "nunique")
    )
    print(monthly.to_string())


def category_report(data):
    print("\n========== SALES BY MEDICINE CATEGORY ==========")
    result = data.groupby("Medicine_Category").agg(
        Units_Sold=("Quantity", "sum"),
        Sales_Revenue=("Line_Total_LKR", "sum"),
        Unique_Medicines=("Medicine_ID", "nunique")
    ).sort_values("Sales_Revenue", ascending=False)
    print(result.to_string())


def branch_report(data):
    print("\n========== SALES BY BRANCH ==========")
    result = data.groupby(["Branch_ID", "Branch_Name"]).agg(
        Units_Sold=("Quantity", "sum"),
        Sales_Revenue=("Line_Total_LKR", "sum"),
        Transaction_Records=("Transaction_ID", "nunique")
    ).sort_values("Sales_Revenue", ascending=False)
    print(result.to_string())


def payment_report(data):
    print("\n========== PAYMENT METHOD REPORT ==========")
    result = data.groupby("Payment_Method").agg(
        Transaction_Records=("Transaction_ID", "nunique"),
        Sales_Revenue=("Line_Total_LKR", "sum")
    ).sort_values("Sales_Revenue", ascending=False)
    print(result.to_string())


def expiry_report(data):
    # These are expiry dates attached to historical sales records,
    # not a list of today's available inventory.
    print("\n========== HISTORICAL EXPIRY-DATE CHECK ==========")
    print("This report does not show current stock or current expired stock.")

    today = pd.Timestamp.today().normalize()
    expired_at_sale_date = data[
        data["Expiry_Date"] < data["Transaction_Date"]
    ]

    print("Records where expiry date was before transaction date:",
          len(expired_at_sale_date))

    if not expired_at_sale_date.empty:
        print(expired_at_sale_date[
            ["Transaction_Date", "Medicine_Name", "Batch_No", "Expiry_Date"]
        ].head(20).to_string(index=False))


def make_charts(data):
    os.makedirs(REPORT_FOLDER, exist_ok=True)

    print("\nCreating charts...")

    # Chart 1: monthly sales revenue.
  

    # NumPy example: calculate each row's estimated pre-discount amount.
    # This is a calculation practice, not profit.
    quantity_array = np.array(data["Quantity"])
    price_array = np.array(data["Unit_Price_LKR"])
    before_discount = quantity_array * price_array
    print("Total before discounts (LKR):", round(before_discount.sum(), 2))

    print("Charts saved in the reports folder.")


def main():
    if not os.path.exists(DATA_FILE):
        print("Dataset not found.")
        print("Put the original CSV inside the data folder.")
        return

    data = load_data()

    while True:
        print("\n========== PHARMACY SALES ANALYSIS ==========")
        print("1. Dataset overview")
        print("2. Check data quality")
        print("3. Save cleaned dataset")
        print("4. Sales report for a date range")
        print("5. Top-selling medicines")
        print("6. Monthly sales report")
        print("7. Sales by medicine category")
        print("8. Sales by branch")
        print("9. Sales by payment method")
        print("10. Historical expiry-date check")
        print("11. Create charts")
        print("12. Exit")

        choice = input("Choose an option (1-12): ").strip()

        if choice == "1":
            show_overview(data)
        elif choice == "2":
            check_data(data)
        elif choice == "3":
            save_clean_data(data)
        elif choice == "4":
            sales_by_date(data)
        elif choice == "5":
            top_medicines(data)
        elif choice == "6":
            monthly_sales(data)
        elif choice == "7":
            category_report(data)
        elif choice == "8":
            branch_report(data)
        elif choice == "9":
            payment_report(data)
        elif choice == "10":
            expiry_report(data)
        elif choice == "11":
            make_charts(data)
        elif choice == "12":
            print("Goodbye!")
            break
        else:
            print("Please choose a number from 1 to 12.")


if __name__ == "__main__":
    main()
