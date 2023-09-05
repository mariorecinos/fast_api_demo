
from fastapi import FastAPI, Request, Form, APIRouter, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from models.account import Account
import csv

router = APIRouter()

ACCOUNTS_CSV = "db/accounts.csv"

templates = Jinja2Templates(directory="templates")


# Helper function to write accounts to CSV
def write_accounts_to_csv(accounts):
    with open(ACCOUNTS_CSV, mode="w", newline="") as file:
        fieldnames = ["account_number", "name", "user"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for account in accounts:
            print(account)
            account_data = {
                "account_number": account["account_number"],
                "name": account["name"],
                "user": account["user"],
            }
            writer.writerow(account_data)

# Helper function to read accounts from CSV
def read_accounts_from_csv():
    accounts = []
    with open(ACCOUNTS_CSV, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            accounts.append(row)
    return accounts
# Create an account
@router.post("/create")
async def create_account(request: Request, user_id: str, account: Account):
    # Load existing accounts from CSV
    accounts = read_accounts_from_csv()

    # Add the new account to the list
    accounts.append(account.dict())

    # Write updated accounts list back to CSV
    write_accounts_to_csv(accounts)

    return templates.TemplateResponse("accounts/account_list.html", {"request": request})


@router.get("/new", response_class=HTMLResponse)
async def create_account_form(request: Request):
    return templates.TemplateResponse("accounts/create_account.html", {"request": request})

# Delete an account
@router.delete("/{account_number}/user/{user_id}")
async def delete_account(user_id: str, account_number: str):
    # Load existing accounts from CSV
    accounts = read_accounts_from_csv()

    # Find and remove the account
    updated_accounts = [account for account in accounts if account["account_number"] != account_number]

    # Write updated accounts list back to CSV
    write_accounts_to_csv(updated_accounts)

    return {"message": "Account deleted successfully"}

@router.put("/{account_number}/user/{user_id}")
async def edit_account(user_id: str, account_number: str, updated_account: Account):
    # Load existing accounts from CSV
    accounts = read_accounts_from_csv()

    # Find the account and update its details
    for account in accounts:
        if account["account_number"] == account_number:
            account.update(updated_account.dict())
            break

    # Write updated accounts list back to CSV
    write_accounts_to_csv(accounts)

    return {"message": "Account updated successfully"}

# Get all accounts
@router.get("/user/{user_id}")
async def get_all_accounts(request: Request, user_id: str):
    # Load existing accounts from CSV
    accounts = read_accounts_from_csv()

    # Filter accounts belonging to the specified user
    user_accounts = [account for account in accounts if account["user"] == user_id]

    return templates.TemplateResponse(
        "accounts/account_list.html",
        {"request": request, "accounts": user_accounts}
    )

@router.get("/{account_id}/user/{user_id}")
async def get_account_details(request: Request, account_id: str, user_id: str):
    # Load existing accounts from CSV
    accounts = read_accounts_from_csv()

    # Find the account with the specified account ID and user ID
    account = next((acc for acc in accounts if acc["user"] == user_id and acc["account_number"] == account_id), None)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return templates.TemplateResponse("accounts/details.html", {"request": request, "account": account})
