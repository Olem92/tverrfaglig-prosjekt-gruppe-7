from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import VarehusDatabase

app = FastAPI()
db = VarehusDatabase()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request):
    return templates.TemplateResponse("orders.html", {"request": request})

@app.get("/inventory", response_class=HTMLResponse)
async def inventory_page(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})

@app.get("/contacts", response_class=HTMLResponse)
async def contacts_page(request: Request):
    return templates.TemplateResponse("contacts.html", {"request": request})

# --- API endpoints for data (keep these as before) ---
@app.on_event("startup")
def connect_to_db():
    try:
        db.connect()
    except Exception as e:
        raise RuntimeError(f"Failed to connect to DB: {e}")

@app.get("/api/orders")
def get_orders():
    try:
        return db.get_orders()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory")
def get_inventory():
    try:
        return db.get_inventory()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts")
def get_contacts():
    try:
        return db.get_contacts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
