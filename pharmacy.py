import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os

data = pd.read_csv(r"E:\Pharmacy_OLTP_SLStyle_18Months.csv")

stock = {}
prices = {}

for medicine in data["Medicine_Name"].unique():
    sold = data[data["Medicine_Name"] == medicine]["Quantity"].sum()
    price = data[data["Medicine_Name"] == medicine]["Unit_Price_LKR"].mean()

    stock[medicine] = int(sold * 1.5) + 50
    prices[medicine] = round(price, 2)

total_bills = 0
total_revenue = 0

# New file for purchases. Existing records are preserved.
sales_file = "pharmacy_sales.csv"
if not os.path.exists(sales_file):
    pd.DataFrame(columns=[
        "Bill_Number", "Date", "Medicine_Name", "Quantity",
        "Unit_Price_LKR", "Subtotal_LKR", "Discount_Percent",
        "Discount_Amount_LKR", "Total_LKR"
    ]).to_csv(sales_file, index=False)

while True:
    print("\\n===== PHARMACY INVOICE SYSTEM =====")
    print("1. Sales Overview")
    print("2. Check Medicine Stock")
    print("3. Top Selling Medicines")
    print("4. Create Bill")
    print("5. Calculate Estimated Profit")
    print("6. Show All Medicines")
    print("7. Exit")
    print("8. Show Charts")

    choice = input("Enter your choice: ")

    if choice == "1":
        print("\\n===== SALES OVERVIEW =====")
        print("Total transactions:", data["Transaction_ID"].nunique())
        print("Total units sold:", int(data["Quantity"].sum()))
        print("Total historical revenue:", round(data["Line_Total_LKR"].sum(), 2), "LKR")
        print("Total medicines:", data["Medicine_Name"].nunique())
        print("Total branches:", data["Branch_Name"].nunique())
        input("\\nPress Enter to continue...")

    elif choice == "2":
        name = input("Enter medicine name: ").lower()
        found = False

        for medicine in stock:
            if name in medicine.lower():
                print("\\nMedicine:", medicine)
                print("Stock:", stock[medicine])
                print("Price:", prices[medicine], "LKR")
                found = True

        if not found:
            print("Medicine not found.")

        input("\\nPress Enter to continue...")

    elif choice == "3":
        print("\\n===== TOP 10 MEDICINES =====")
        top = data.groupby("Medicine_Name")["Quantity"].sum()
        top = top.sort_values(ascending=False).head(10)
        print(top)
        input("\\nPress Enter to continue...")

    elif choice == "4":
        name = input("Enter medicine name: ").lower()
        matches = []

        for medicine in stock:
            if name in medicine.lower():
                matches.append(medicine)

        if len(matches) == 0:
            print("Medicine not found.")
            input("\\nPress Enter to continue...")
            continue

        print("\\nMatching medicines:")
        for i in range(len(matches)):
            print(i + 1, matches[i])

        if len(matches) == 1:
            medicine = matches[0]
        else:
            try:
                number = int(input("Choose medicine number: "))
            except ValueError:
                print("Please enter a valid number.")
                input("\\nPress Enter to continue...")
                continue

            if number < 1 or number > len(matches):
                print("Invalid number.")
                input("\\nPress Enter to continue...")
                continue
            medicine = matches[number - 1]

        print("\\nPrice:", prices[medicine], "LKR")
        print("Available stock:", stock[medicine])

        if stock[medicine] <= 0:
            print("Medicine is out of stock.")
            input("\\nPress Enter to continue...")
            continue

        try:
            quantity = int(input("Enter quantity: "))
        except ValueError:
            print("Please enter a whole number for quantity.")
            input("\\nPress Enter to continue...")
            continue

        if quantity <= 0:
            print("Quantity must be greater than zero.")
            input("\\nPress Enter to continue...")
            continue

        if quantity > stock[medicine]:
            print("Not enough stock.")
            input("\\nPress Enter to continue...")
            continue

        try:
            discount = float(input("Enter discount percentage (0 if none): "))
        except ValueError:
            print("Invalid discount. Using 0%.")
            discount = 0

        if discount < 0 or discount > 50:
            print("Invalid discount. Using 0%.")
            discount = 0

        subtotal = prices[medicine] * quantity
        discount_amount = subtotal * discount / 100
        total = subtotal - discount_amount

        stock[medicine] = stock[medicine] - quantity
        total_bills = total_bills + 1
        total_revenue = total_revenue + total

        # Append this purchase to the CSV file (keeps earlier purchases).
        sale_record = pd.DataFrame([{
            "Bill_Number": total_bills,
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Medicine_Name": medicine,
            "Quantity": quantity,
            "Unit_Price_LKR": prices[medicine],
            "Subtotal_LKR": round(subtotal, 2),
            "Discount_Percent": discount,
            "Discount_Amount_LKR": round(discount_amount, 2),
            "Total_LKR": round(total, 2)
        }])
        sale_record.to_csv(sales_file, mode="a", header=False, index=False)

        print("\\n===== PHARMACY BILL =====")
        print("Bill number:", total_bills)
        print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M"))
        print("Medicine:", medicine)
        print("Quantity:", quantity)
        print("Unit price:", prices[medicine], "LKR")
        print("Subtotal:", round(subtotal, 2), "LKR")
        print("Discount:", discount, "%")
        print("Total to pay:", round(total, 2), "LKR")
        print("=========================")
        print("Remaining stock:", stock[medicine])
        print("Purchase saved to", sales_file)

        input("\\nPress Enter to continue...")

    elif choice == "5":
        print("\\n===== ESTIMATED PROFIT =====")
        cost = total_revenue * 0.70
        profit = total_revenue - cost

        print("Bills created:", total_bills)
        print("Revenue:", round(total_revenue, 2), "LKR")
        print("Assumed cost (70%):", round(cost, 2), "LKR")
        print("Estimated profit:", round(profit, 2), "LKR")
        input("\\nPress Enter to continue...")

    elif choice == "6":
        print("\\n===== MEDICINE LIST =====")
        for medicine in sorted(stock):
            print(medicine, "| Stock:", stock[medicine], "| Price:", prices[medicine], "LKR")
        input("\\nPress Enter to continue...")

    elif choice == "7":
        print("Program closed. Goodbye!")
        break

    elif choice == "8":
        top = data.groupby("Medicine_Name")["Quantity"].sum().sort_values(ascending=False).head(10)
        plt.figure(figsize=(11, 6))
        top.sort_values().plot(kind="barh")
        plt.title("Top 10 Medicines by Historical Units Sold")
        plt.xlabel("Units sold")
        plt.ylabel("Medicine")
        plt.tight_layout()
        plt.show()

        sales = pd.read_csv(sales_file)
        if not sales.empty:
            sales["Date"] = pd.to_datetime(sales["Date"], errors="coerce")
            daily_revenue = sales.groupby(sales["Date"].dt.date)["Total_LKR"].sum()
            plt.figure(figsize=(10, 5))
            daily_revenue.plot(kind="line", marker="o")
            plt.title("Revenue from New Purchases")
            plt.xlabel("Date")
            plt.ylabel("Revenue (LKR)")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()

            low_stock = pd.Series(stock).sort_values().head(10)
            plt.figure(figsize=(11, 6))
            low_stock.sort_values(ascending=True).plot(kind="barh")
            plt.title("10 Medicines with Lowest Current Stock")
            plt.xlabel("Units remaining")
            plt.ylabel("Medicine")
            plt.tight_layout()
            plt.show()
        else:
            print("No saved purchases yet. Create a bill first to see the revenue chart.")
        input("\\nPress Enter to continue...")

    else:
        print("Invalid choice. Try again.")
        input("\\nPress Enter to continue...")
