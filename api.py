# Importerer nødvendige moduler fra FastAPI
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# Importerer nødvendige moduler fra Pydantic
from pydantic import BaseModel
# Importerer VarehusDatabase-klassen fra database.py
from database import VarehusDatabase

app = FastAPI() # Definerer FastAPI-applikasjonen
db = VarehusDatabase() # Definerer database-klassen

## Brukt for å validere data som sendes til APIet
class ContactIn(BaseModel):
    fornavn: str
    etternavn: str
    adresse: str
    postnr: str

class ContactEdit(ContactIn):
    knr: int


## FastAPI henter CSS-filer og ikoner
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/icons", StaticFiles(directory="icons"), name="icons")

## FastAPI henter templates
templates = Jinja2Templates(directory="templates")

## FastAPI henter HTML-filer
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

## FastAPI funksjon for å servere orders-siden
@app.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request):
    return templates.TemplateResponse("orders.html", {"request": request})

## FastAPI funksjon for å servere inventory-siden
@app.get("/inventory", response_class=HTMLResponse)
async def inventory_page(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})

## FastAPI funksjon for å servere kontaktsiden
@app.get("/contacts", response_class=HTMLResponse)
async def contacts_page(request: Request):
    return templates.TemplateResponse("contacts.html", {"request": request})

## FastAPI funksjon for å servere management-siden
@app.get("/management", response_class=HTMLResponse)
async def management_page(request: Request):
    return templates.TemplateResponse("management.html", {"request": request})

## FastAPI funskjon for å koble til databasen ved oppstart
@app.on_event("startup")
def connect_to_db():
    try:
        db.connect()
    except Exception as e:
        raise RuntimeError(f"Failed to connect to DB: {e}")
    
## FastAPI funksjon for å hente ordrer
@app.get("/api/orders")
def get_orders():
    try:
        return db.get_orders()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## FastAPI funksjon for å hente lagerbeholdning
@app.get("/api/inventory")
def get_inventory():
    try:
        return db.get_inventory()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## FastAPI funksjon for å hente kontakter
@app.get("/api/contacts")
def get_contacts():
    try:
        return db.get_contacts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## FastAPI funksjon for å legge til kontakter
@app.post("/api/contacts")
def add_contact(contact: ContactIn):
    if db.add_contacts(contact.fornavn, contact.etternavn, contact.adresse, contact.postnr):
        return {"success": True}
    raise HTTPException(status_code=400, detail="Could not add contact")

## FastAPI funksjon for å editere kontakter
@app.put("/api/contacts/{knr}")
def edit_contact(knr: int, contact: ContactIn):
    if db.edit_contacts(knr, contact.fornavn, contact.etternavn, contact.adresse, contact.postnr):
        return {"success": True}
    raise HTTPException(status_code=400, detail="Could not edit contact")

## FastAPI funksjon for å slette kontakter
@app.delete("/api/contacts/{knr}")
def delete_contact(knr: int):
    if db.remove_contacts(knr):
        return {"success": True}
    raise HTTPException(status_code=400, detail="Could not delete contact")
