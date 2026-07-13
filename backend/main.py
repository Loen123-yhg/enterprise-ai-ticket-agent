import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
import os
from openai import OpenAI

ai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "tickets.db"
ai_client = OpenAI()

class TicketCreate(BaseModel):
    user_name: str
    question: str
    priority: Literal["low", "medium", "high"] = "low"


class TicketUpdate(BaseModel):
    user_name: str | None = None
    question: str | None = None
    priority: Literal["low", "medium", "high"] | None = None
    status: Literal["open", "in_progress", "closed"] | None = None


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                question TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def health_check():
    return {"message": "API is running"}


@app.post("/tickets")
def create_ticket(ticket: TicketCreate):
    with get_conn() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tickets (user_name, question, priority, status)
            VALUES (?, ?, ?, ?)
            """,
            (ticket.user_name, ticket.question, ticket.priority, "open"),
        )
        ticket_id = cursor.lastrowid

    return {
        "id": ticket_id,
        "user_name": ticket.user_name,
        "question": ticket.question,
        "priority": ticket.priority,
        "status": "open",
    }


@app.get("/tickets")
def list_tickets():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, user_name, question, priority, status
            FROM tickets
            ORDER BY id
            """
        ).fetchall()

    return [dict(row) for row in rows]


@app.get("/tickets/search")
def search_tickets(
    q: str | None = None,
    priority: Literal["low", "medium", "high"] | None = None,
    status: Literal["open", "in_progress", "closed"] | None = None,
):
    sql = """
        SELECT id, user_name, question, priority, status
        FROM tickets
        WHERE 1 = 1
    """
    params = []

    if q:
        sql += " AND (user_name LIKE ? OR question LIKE ?)"
        keyword = f"%{q}%"
        params.extend([keyword, keyword])

    if priority:
        sql += " AND priority = ?"
        params.append(priority)

    if status:
        sql += " AND status = ?"
        params.append(status)

    sql += " ORDER BY id"

    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()

    return [dict(row) for row in rows]


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, user_name, question, priority, status
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return dict(row)


@app.patch("/tickets/{ticket_id}")
def update_ticket(ticket_id: int, update: TicketUpdate):
    update_data = update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    fields = ", ".join([f"{key} = ?" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(ticket_id)

    with get_conn() as conn:
        cursor = conn.execute(
            f"""
            UPDATE tickets
            SET {fields}
            WHERE id = ?
            """,
            values,
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ticket not found")

        row = conn.execute(
            """
            SELECT id, user_name, question, priority, status
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,),
        ).fetchone()

    return dict(row)
@app.post("/tickets/{ticket_id}/ai-analysis")
def analyze_ticket(ticket_id: int):
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, user_name, question, priority, status
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket = dict(row)

    prompt = f"""
你是企业 IT 工单助手。

请根据下面的工单内容，给出：
1. 问题分类
2. 建议优先级，只能是 low、medium、high
3. 给客服人员的处理建议
4. 给用户的回复话术

工单信息：
用户：{ticket["user_name"]}
问题：{ticket["question"]}
当前优先级：{ticket["priority"]}
当前状态：{ticket["status"]}
"""

    response = ai_client.responses.create(
        model="gpt-5.5",
        input=prompt,
    )

    return {
        "ticket": ticket,
        "ai_analysis": response.output_text,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
