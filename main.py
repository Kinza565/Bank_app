from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict

app = FastAPI(title="Banking Homework App", version="1.0.0")

# ------------------------------
# In-Memory User Database
# ------------------------------
users: Dict[str, Dict[str, float]] = {
    "user1": {"pin": "1234", "balance": 1000.0},
    "user2": {"pin": "5678", "balance": 500.0}
}

# ------------------------------
# Pydantic Models
# ------------------------------
class AuthenticateRequest(BaseModel):
    name: str = Field(..., example="user1")
    pin_number: str = Field(..., example="1234")

class AuthenticateResponse(BaseModel):
    message: str
    balance: float

class DepositRequest(BaseModel):
    name: str = Field(..., example="user1")
    amount: float = Field(..., gt=0, example=500.0)

class DepositResponse(BaseModel):
    message: str
    balance: float

class TransferRequest(BaseModel):
    sender_name: str = Field(..., example="user1")
    receiver_name: str = Field(..., example="user2")
    amount: float = Field(..., gt=0, example=200.0)

class TransferResponse(BaseModel):
    message: str
    sender_balance: float
    receiver_balance: float

# ------------------------------
# Endpoints
# ------------------------------

@app.post("/authenticate", response_model=AuthenticateResponse, tags=["Authentication"])
def authenticate_user(request: AuthenticateRequest):
    """
    Authenticate a user using their name and pin number.
    Returns the current balance if successful.
    """
    user = users.get(request.name)
    if not user or user["pin"] != request.pin_number:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Authentication successful", "balance": user["balance"]}


@app.post("/deposit", response_model=DepositResponse, tags=["Transactions"])
def deposit_funds(request: DepositRequest):
    """
    Deposit a positive amount into a user's account.
    """
    user = users.get(request.name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["balance"] += request.amount
    return {"message": "Deposit successful", "balance": user["balance"]}


@app.post("/bank-transfer", response_model=TransferResponse, tags=["Transactions"])
def bank_transfer(request: TransferRequest):
    """
    Transfer funds from one user to another.
    Deducts from sender and adds to receiver.
    """
    sender = users.get(request.sender_name)
    receiver = users.get(request.receiver_name)

    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    if sender["balance"] < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    sender["balance"] -= request.amount
    receiver["balance"] += request.amount

    return {
        "message": "Transfer successful",
        "sender_balance": sender["balance"],
        "receiver_balance": receiver["balance"]
    }
