from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database, os

database.init_db()
app = FastAPI(title="Debre Gelila Emmanuel Cathedral Ticket System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. ሁነቶችን ማምጣት
@app.get("/api/events")
def get_events(db: Session = Depends(get_db)):
    return db.query(database.Event).all()

# 2. የባንክ አካውንቶችን ማምጣት
@app.get("/api/banks")
def get_banks(db: Session = Depends(get_db)):
    return db.query(database.BankAccount).all()

# 3. ትዕዛዝ መፍጠር (Order Checkout)
@app.post("/api/orders")
def create_order(
    event_id: int = Form(...),
    buyer_name: str = Form(...),
    buyer_phone: str = Form(...),
    quantity: int = Form(...),
    selected_bank: str = Form(...),
    db: Session = Depends(get_db)
):
    event = db.query(database.Event).filter(database.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="ሁነቱ አልተገኘም")
    
    total = event.price * quantity
    prefix = "LOT" if event.category == "lottery" else "GRAD"
    order_code = f"{prefix}-2019-{os.urandom(2).hex().upper()}"
    
    new_order = database.Order(
        order_code=order_code,
        event_id=event_id,
        buyer_name=buyer_name,
        buyer_phone=buyer_phone,
        quantity=quantity,
        total_amount=total,
        selected_bank=selected_bank
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return {"status": "success", "order_code": order_code, "total_amount": total}

# 4. ደረሰኝ በመጫን ማረጋገጥ
@app.post("/api/verify-receipt")
async def verify_receipt(
    order_code: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    order = db.query(database.Order).filter(database.Order.order_code == order_code).first()
    if not order:
        raise HTTPException(status_code=404, detail="ትዕዛዙ አልተገኘም")
    
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    order.receipt_image = file_path
    order.status = "pending_admin"
    db.commit()
    
    return {"status": "success", "message": "ደረሰኝዎ ተቀብሏል፤ በአድሚን ማረጋገጫ ላይ ይገኛል።"}

# 5. አድሚን ትዕዛዝ ማጽደቅ እና ቲኬት ማመንጨት
@app.post("/api/admin/orders/{order_code}/approve")
def approve_order(order_code: str, db: Session = Depends(get_db)):
    order = db.query(database.Order).filter(database.Order.order_code == order_code).first()
    if not order:
        raise HTTPException(status_code=404, detail="ትዕዛዙ አልተገኘም")
    
    order.status = "approved"
    
    tickets = []
    for i in range(order.quantity):
        t_num = f"TKT-{order.order_code}-{i+1}"
        ticket = database.Ticket(ticket_number=t_num, order_code=order.order_code, event_id=order.event_id)
        db.add(ticket)
        tickets.append(t_num)
        
    db.commit()
    return {"status": "success", "tickets": tickets}