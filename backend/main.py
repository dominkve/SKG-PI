from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

conn = sqlite3.connect("pi.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS pi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    throws INTEGER NOT NULL DEFAULT 0,
    crossings INTEGER NOT NULL DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

cursor.execute(
    "INSERT INTO pi (throws, crossings) VALUES (0, 0)"
)

conn.commit()

conn.close()

class Entry(BaseModel):
    throws: int
    crossings: int


app = FastAPI()

app.mount("/static", StaticFiles(directory="static", name="static"))

"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""

@app.get("/")
async def root():
    return FileResponse("static/index.html")
@app.post("/submit/")
async def submit(Entry: Entry):

    if Entry.throws <= 0:
        raise HTTPException(status_code=400,
                            detail="Broj bacanja mora biti pozitivan.")
    
    if Entry.crossings < 0 or Entry.crossings > Entry.throws:
        raise HTTPException(status_code=400,
                            detail="Nevaljan broj križanja.")
    
    conn = sqlite3.connect("pi.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO pi(throws, crossings) VALUES(?, ?)",
        (Entry.throws, Entry.crossings)
    )

    conn.commit()
    conn.close()

    return {
        "status": "ok",
        "throws": Entry.throws,
        "crossings": Entry.crossings
    }

@app.get("/stats/")
async def stats():
    conn = sqlite3.connect("pi.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT SUM(throws), SUM(crossings) FROM pi"
    )

    data = cursor.fetchall()

    conn.close()

    if (data[0][1]):
        pi_estimate = 2*data[0][0] / data[0][1]
    else:
        pi_estimate = None


    return {
        "total_throws": data[0][0],
        "total_crossings": data[0][1],
        "pi": pi_estimate
    }
    