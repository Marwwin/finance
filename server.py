from typing import Annotated

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import db

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    bucket_keys = ["daily_expenses", "smile", "fire_extinguisher", "splurge"]
    return templates.TemplateResponse(
        "index.html", {"request": request, "buckets": bucket_keys}
    )


@app.get("/income", response_class=HTMLResponse)
def income(request: Request):
    bucket = db.get_bucket("income")
    return templates.TemplateResponse(
        "bucket.html", {"request": request, "key": "income", "bucket": bucket}
    )


@app.get("/bucket/{key}", response_class=HTMLResponse)
def bucket(request: Request, key: str):
    bucket = db.get_bucket(key)
    return templates.TemplateResponse(
        "bucket.html", {"request": request, "key": key, "bucket": bucket}
    )


@app.get("/sum/{key}", response_class=HTMLResponse)
def get_sum(request: Request, key: str):
    bucket = db.get_bucket(key)
    bucket_sum = str(sum([row[2] for row in bucket]))
    return HTMLResponse(content=f"Sum: {bucket_sum}")


@app.delete("/deleteTransaction/{bucket}/{transactionId}", response_class=HTMLResponse)
def add_transaction_form(request: Request, bucket: str, transactionId: int):
    db.delete_transaction(bucket, transactionId)
    return HTMLResponse(content="", status_code=200, headers={"HX-Trigger": f"{bucket}-reload-sum"})


@app.post("/addTransaction/{bucket}", response_class=HTMLResponse)
def add_transaction(
    request: Request,
    bucket: str,
    name: Annotated[str, Form()],
    amount: Annotated[int, Form()],
):
    transaction = db.add_transaction(bucket, name, amount)
    return templates.TemplateResponse(
        "transaction.html",
        {"request": request, "key": bucket, "transaction": transaction},
        headers={"HX-Trigger": f"{bucket}-reload-sum"},
    )
