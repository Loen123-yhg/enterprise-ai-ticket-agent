from fastapi import FastAPI
#用来检查用户传过来的数据格式。
from pydantic import BaseModel
#创建FastAPI实例
app = FastAPI()
tickets = []
class Ticketcreate(BaseModel):
    user_name: str
    question : str
    priority : str = 'low'

@app.get('/')
def health_check():
        return {'message':'API is runing'}
@app.post("/tickets")
def create_ticket(ticket: Ticketcreate):
        new_ticket = {
            "id": len(tickets) + 1,
            "user_name": ticket.user_name,
            "question": ticket.question,
            "priority": ticket.priority,
            "status": "open",
        }
        tickets.append(new_ticket)
        return new_ticket
@app.get('/tickets')
def list_tickets():
        return tickets
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
