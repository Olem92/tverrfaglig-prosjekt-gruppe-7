from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import VarehusDatabase

app = FastAPI()
db = VarehusDatabase()

## FastAPI henter CSS-filer
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/icons", StaticFiles(directory="icons"), name="icons")

## FastAPI henter templates
templates = Jinja2Templates(directory="templates")

## FastAPI henter HTML-filer
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

## FastAPI henter ordre fra databasen
@app.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request):
    return templates.TemplateResponse("orders.html", {"request": request})

## FastAPI henter lager fra databasen
@app.get("/inventory", response_class=HTMLResponse)
async def inventory_page(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})

## FastAPI henter kontakter fra databasen
@app.get("/contacts", response_class=HTMLResponse)
async def contacts_page(request: Request):
    return templates.TemplateResponse("contacts.html", {"request": request})

## FastAPI henter kontakter fra databasen
@app.get("/management", response_class=HTMLResponse)
async def management_page(request: Request):
    return templates.TemplateResponse("management.html", {"request": request})

## FastAPI kobler til og henter data fra databasen
@app.on_event("startup")
def connect_to_db():
    try:
        db.connect()
    except Exception as e:
        raise RuntimeError(f"Failed to connect to DB: {e}")
    
## FastAPI henter ordre
@app.get("/api/orders")
def get_orders():
    try:
        return db.get_orders()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## FastAPI henter lagerbeholdning
@app.get("/api/inventory")
def get_inventory():
    try:
        return db.get_inventory()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## FastAPI henter kontakter
@app.get("/api/contacts")
def get_contacts():
    try:
        return db.get_contacts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


##### FIX Management funksjoner! ==>
#@app.get("/api/management")
#def get_contacts():
#    try:
#        return db.get_contacts()
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=str(e))
#    
#@app.get("/api/management")
#def get_contacts():
#    try:
#        return db.get_contacts()
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=str(e))
#    
#@app.get("/api/management")
#def get_contacts():
#    try:
#        return db.get_contacts()
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=str(e))
