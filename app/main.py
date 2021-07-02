from sqlalchemy.sql.sqltypes import DateTime
from app.db import Base, Guest
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.db import Base, Guest, engine, session as db
from sqlalchemy import or_, and_
import datetime
import qrcode
import qrcode.image.svg
from fastapi.responses import FileResponse

ORIGINS = [
    "http://localhost:3000",
    "https://ashkev.peterboroughtenants.app",
    "https://ashkev.alexhall.dev",
]

QR_URL = "https://ashkev.peterboroughtenants.app/rsvp"


Base.metadata.create_all(engine)


# RSVP Request model
class Rsvp(BaseModel):
    accomodation: Optional[bool] = False
    requirements: Optional[str] = None
    attending: bool

    class Config:
        orm_mode = True


# New guest model
class NewGuest(BaseModel):
    id: Optional[str] = None
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    linked_to: Optional[str] = None

    class Config:
        orm_mode = True


# Full guest model
class GuestFull(BaseModel):
    id: str
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    linked_to: Optional[str] = None
    accomodation: Optional[bool] = None
    requirements: Optional[str] = None
    attending: bool
    responded_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/rsvp/{token}", response_model=List[NewGuest])
def get_invite(token):
    guests = (
        db.query(Guest)
        .filter(
            or_(
                and_(Guest.id == token, Guest.linked_to == None),
                Guest.linked_to == token,
            )
        )
        .all()
    )

    if len(guests) == 0:
        raise HTTPException(status_code=404, detail="Guest not found")

    return guests


@app.post("/api/rsvp/{token}")
async def rsvp(token, rsvp: Rsvp):
    guest: Guest = db.query(Guest).filter_by(id=token).first()
    if guest is None:
        raise HTTPException(status_code=404, detail="Guest not found")

    guest.accomodation = rsvp.accomodation
    guest.attending = rsvp.attending
    guest.requirements = rsvp.requirements

    guest.responded_at = datetime.datetime.now()

    db.commit()
    return {"OKAY"}


@app.get("/api/guests", response_model=List[GuestFull])
async def guests():
    guests = db.query(Guest).all()
    return guests


@app.post("/api/guests", response_model=GuestFull)
async def new_guest(guest: NewGuest):
    new_guest = Guest(
        guest.first_name, guest.last_name, guest.display_name, guest.linked_to
    )

    db.add(new_guest)
    db.commit()

    return new_guest


@app.delete("/api/guests/{token}")
async def delete_guest(token: str):
    (
        db.query(Guest)
        .filter(
            or_(
                and_(Guest.id == token, Guest.linked_to == None),
                Guest.linked_to == token,
            )
        )
        .delete()
    )

    db.commit()
    return Response('', 204)


@app.get("/api/qr-code/{token}")
async def qr_code(token: str):
    url = f"{QR_URL}/{token}"
    code_factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(url, image_factory=code_factory)
    img.save(f'./codes/{token}.svg', 'SVG')

    return FileResponse(f'./codes/{token}.svg', media_type="image/svg+xml", filename=f"{token}.svg")
