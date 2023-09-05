from fastapi import APIRouter, HTTPException, Depends
from models.transaction import Transaction  # Import Transaction model from models
import csv
import uuid
from datetime import datetime
from routes.accounts import read_accounts_from_csv, write_accounts_to_csv  # Import the functions
router = APIRouter()

ACCOUNTS_CSV = "db/accounts.csv"
TRANSACTIONS_CSV = "db/transactions.csv"  # Path to transactions CSV

# Helper function to write transactions to CSV
def write_transactions_to_csv(transactions):
    with open(TRANSACTIONS_CSV, mode="w", newline="") as file:
        fieldnames = ["id", "title", "type", "amount", "date", "user_id", "account_number"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)

# Helper function to read transactions from CSV
def read_transactions_from_csv():
    transactions = []
    with open(TRANSACTIONS_CSV, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            transactions.append(row)
    return transactions

# Add a transaction to an account
@router.post("/user/{user_id}/account/{account_number}")
async def add_transaction(user_id: str, account_number: str, transaction: Transaction):
    # Load existing accounts from CSV
    accounts = read_accounts_from_csv()

    # Load existing transactions from CSV
    transactions = read_transactions_from_csv()

    # Find the account associated with the user and account number
    target_account = None
    for account in accounts:
        if account["user"] == user_id and account["account_number"] == account_number:
            target_account = account
            print(target_account, "line 44")
            break

    if not target_account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Generate a unique ID for the new transaction
    new_transaction_id = str(uuid.uuid4())

    # Add transaction details

    new_transaction = {
        "id": new_transaction_id,
        "title": transaction.title,
        "type": transaction.type,
        "amount": transaction.amount,
        "user_id": user_id,
        "account_number": account_number,
        "date": transaction.date.strftime("%Y-%m-%d") # Format date as string
    }

    print(new_transaction, "line 64")

    # Append the new transaction to the list
    transactions.append(new_transaction)


    # Write updated transactions back to CSV
    write_transactions_to_csv(transactions)

    return {"message": "Transaction added successfully"}

# Delete a transaction
@router.delete("/{transaction_id}/user/{user_id}")
async def delete_transaction(user_id: str, transaction_id: str):
    # Load existing transactions from CSV
    transactions = read_transactions_from_csv()

    # Find and remove the transaction
    updated_transactions = [transaction for transaction in transactions if transaction["id"] != transaction_id]

    # Write updated transactions list back to CSV
    write_transactions_to_csv(updated_transactions)

    return {"message": "Transaction deleted successfully"}

# Update a transaction
@router.put("/{transaction_id}/user/{user_id}")
async def edit_transaction(user_id: str, transaction_id: str, updated_transaction: Transaction):
    # Load existing transactions from CSV
    transactions = read_transactions_from_csv()

    # Find the transaction and update its details
    for transaction in transactions:
        if transaction["id"] == transaction_id:
            transaction.update(updated_transaction.dict())
            break

    # Write updated transactions list back to CSV
    write_transactions_to_csv(transactions)

    return {"message": "Transaction updated successfully"}

# Get all transactions for an account
@router.get("/user/{user_id}/account/{account_number}")
async def get_account_transactions(user_id: str, account_number: str):
    # Load existing transactions from CSV
    transactions = read_transactions_from_csv()

    # Filter transactions belonging to the specified account
    account_transactions = [transaction for transaction in transactions if transaction["user_id"] == user_id and transaction["account_number"] == account_number]

    return account_transactions

# Get all transactions for a user
@router.get("/user/{user_id}")
async def get_user_transactions(user_id: str):
    # Load existing transactions from CSV
    transactions = read_transactions_from_csv()

    # Filter transactions belonging to the specified user
    user_transactions = [transaction for transaction in transactions if transaction["user_id"] == user_id]

    return user_transactions
