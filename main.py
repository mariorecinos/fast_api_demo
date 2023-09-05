from typing import Annotated
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from models.user import User
from routes.users import get_current_user
from routes.users import router as users
from routes.accounts import router as accounts
from routes.transactions import router as transactions


from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")  # Make sure you have a "templates" folder in your project directory

app = FastAPI()


# Route for the root URL
@app.get("/")
async def home_page(request: Request):
    print(request)
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(users)
app.include_router(accounts, prefix="/accounts")
app.include_router(transactions, prefix="/transactions")
