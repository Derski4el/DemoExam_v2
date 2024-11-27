from fastapi import FastAPI, Form, Request, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime
from typing import Optional

app = FastAPI()
templates = Jinja2Templates(directory="templates")

alert = []
class Orders:
    def __init__(self, id, start_date, oborodovanie, problema, opicanieproblem, client, status, worker, com):
        self.id = id
        self.startDate = start_date
        self.oborodovanie = oborodovanie
        self.problema = problema
        self.opicanieproblem = opicanieproblem
        self.client = client
        self.status = status
        self.worker = worker
        self.com = com
        self.endDate = None

        if self.status == "Завершено":
            self.endDate = datetime.now()

repo = [
    Orders(1, datetime(2024, 11, 25), "Рука", "Что-то", "Болит", "9", "Завершено", "Помогите пж", "Вася"),
    Orders(2, datetime(2024, 9, 22), "Нога", "Где-то", "Работает", "10", "Ожидания", "Помогите пж", "Вася"),
    Orders(3, datetime(2024, 10, 23), "Голова", "Когда-то", "Греется", "11", "Ожидания", "Помогите пж", "Вася"),
    Orders(4, datetime(2024, 10, 24), "Другая нога", "Почему-то", "Красная", "12", "Завершено", "Помогите пж", "Вася"),
    Orders(5, datetime(2024, 10, 25), "Рука", "Что-то", "Синяя", "9", "Ожидания", "Помогите пж", "Вася"),
    Orders(6, datetime(2024, 10, 26), "Нога", "Где-то", "Прикольная", "10", "Ожидания", "Помогите пж", "Вася"),
    Orders(7, datetime(2024, 10, 27), "Голова", "Когда-то", "Живая", "11", "Ожидания", "Помогите пж", "Вася"),
    Orders(8, datetime(2024, 10, 28), "Другая нога", "Почему-то", "Ходит", "12", "Завершено", "Помогите пж", "Вася")
]


@app.get("/", response_class=HTMLResponse)
def get_orders(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request, "orders": repo})

@app.get("/repo", response_class=HTMLResponse)
def get_orders(request: Request):
    return templates.TemplateResponse("repo.html", {"request": request, "orders": repo, "alert": alert})

@app.post("/postdata")
def postdata(
    id: int = Form(),
    startDate: str = Form(),
    oborodovanie: str = Form(),
    problema: str = Form(),
    opicanieproblem: str = Form(),
    client: str = Form(),
    status: str = Form(),
    worker: str = Form(default="Не назначен"),
    com: str = Form(default="")
):
    if any(order.id == id for order in repo):
        raise HTTPException(status_code=400, detail="Заявка с таким ID уже существует")
    
    try:
        start_date = datetime.strptime(startDate, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Некорректный формат даты")

    # Создание нового заказа
    new_order = Orders(
        id=id,
        start_date=start_date,
        oborodovanie=oborodovanie,
        problema=problema,
        opicanieproblem=opicanieproblem,
        client=client,
        status=status,
        worker=worker,
        com=com
    )
    
    if status == "Завершено":
        new_order.endDate = datetime.now()

    repo.append(new_order)

    return RedirectResponse(url="/", status_code=303)

@app.get("/edit", response_class=HTMLResponse)
def edit_order_by_id(request: Request, order_id: int = Query(...)):
    order_to_edit = next((order for order in repo if order.id == order_id), None)
    if order_to_edit is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    return templates.TemplateResponse("edit_order.html", {"request": request, "order": order_to_edit})

@app.post("/update")
def update_order(
    id: int = Form(),
    startDate: str = Form(),
    oborodovanie: str = Form(),
    problema: str = Form(),
    opicanieproblem: str = Form(),
    client: str = Form(),
    status: str = Form(),
    worker: str = Form(default="Не назначен"),
    com: str = Form(default="")
):

    order_to_update = next((order for order in repo if order.id == id), None)
    if order_to_update is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")


    try:
        start_date = datetime.strptime(startDate, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Некорректный формат даты")

    if order_to_update.status != status:
        alert.append(f"Обновленна статутс {order_to_update.id} заменен на  {order_to_update.status}")

    order_to_update.startDate = start_date
    order_to_update.oborodovanie = oborodovanie
    order_to_update.problema = problema
    order_to_update.opicanieproblem = opicanieproblem
    order_to_update.client = client
    order_to_update.status = status
    order_to_update.worker = worker
    order_to_update.com = com

    return RedirectResponse(url="/", status_code=303)

@app.get("/stats/1", response_class=HTMLResponse)
def stats_1(request: Request):
    completed_orders = [o for o in repo if o.status == "Завершено"]
    return templates.TemplateResponse("stats.html", {"request": request, "orders": completed_orders, "stat_type": "completed_orders"})

@app.get("/stats/2", response_class=HTMLResponse)
def stats_2(request: Request):
    problem_counts = {}
    for o in repo:
        if o.problema in problem_counts:
            problem_counts[o.problema] += 1
        else:
            problem_counts[o.problema] = 1

    return templates.TemplateResponse("stats.html", {"request": request, "problem_counts": problem_counts, "stat_type": "problem_counts"})

@app.get("/stats/3", response_class=HTMLResponse)
def stats_3(request: Request):
    completed_orders = [o for o in repo if o.status == "Завершено" and o.endDate is not None]
    
    if not completed_orders:
        average_time = None
    else:
        times = [(o.endDate - o.startDate).days for o in completed_orders]
        average_time = sum(times) / len(times)
    
    return templates.TemplateResponse("stats.html", {"request": request, "average_time": average_time, "stat_type": "average_time"})

