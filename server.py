import json
from typing import Annotated, Union

from fastapi import FastAPI, Form, Request
from fastapi.encoders import jsonable_encoder
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


@app.get("/bucket/{bucket_key}", response_class=HTMLResponse)
def bucket(request: Request, bucket_key: str):
    bucket = db.get_bucket(bucket_key)
    return templates.TemplateResponse(
        "bucket.html",
        {"request": request, "bucket": bucket_key, "transactions": bucket},
    )


@app.delete("/deleteTransaction/{bucket}/{transactionId}", response_class=HTMLResponse)
def add_transaction_form(request: Request, bucket: str, transactionId: int):
    db.delete_transaction(bucket, transactionId)
    return HTMLResponse(
        content="",
        status_code=200,
        headers={
            "HX-Trigger": json.dumps({"reload-sum": "", "reload-stats": ""})
        },
    )


@app.post("/addTransaction/{bucket}", response_class=HTMLResponse)
def add_transaction(
    request: Request,
    bucket: str,
    name: Annotated[str, Form()],
    amount: Annotated[float, Form()],
):
    transaction = db.add_transaction(bucket, name, amount)
    return templates.TemplateResponse(
        "transaction.html",
        {"request": request, "bucket": bucket, "transaction": transaction},
        headers={
            "HX-Trigger": json.dumps({"reload-sum": "", "reload-stats": ""})
        },
    )


@app.get("/edit/{bucket}/{transaction_id}")
def get_edit_form(
    request: Request,
    bucket: str,
    transaction_id: int,
    value: Union[str, int],
    name: str,
):
    return templates.TemplateResponse(
        "editInput.html",
        {
            "request": request,
            "bucket": bucket,
            "field_name": name,
            "value": value,
            "transaction_id": transaction_id,
        },
    )


@app.post("/edit/{bucket}/{transaction_id}")
async def edit_transaction(request: Request, bucket: str, transaction_id: int):
    form = await request.form()
    data = jsonable_encoder(form)

    edit = list(data.items())[0]
    db.edit_transaction(bucket, transaction_id, edit)

    transaction = db.get_transaction_by_id(bucket, transaction_id)
    return templates.TemplateResponse(
        "transaction.html",
        {
            "request": request,
            "bucket": bucket,
            "transaction": transaction,
        },
        headers={
            "HX-Trigger": json.dumps({"reload-sum": "", "reload-stats": ""})
        },
    )


@app.get("/sum/{bucket_key}", response_class=HTMLResponse)
def get_sum(request: Request, bucket_key: str):
    bucket = sum_of_bucket(db.get_bucket(bucket_key))
    if bucket_key == "income":
        return HTMLResponse(
            content=f"""
            <div class='bucket_sum'>Sum: {bucket}</div>""",
        )

    income_bucket = sum_of_bucket(db.get_bucket("income"))
    return HTMLResponse(
        content=f"""
            <div class='bucket_sum'>Sum: {bucket}</div>
            <div>Percentage: {bucket/income_bucket*100:.2f}%</div>""",
    )


@app.get("/stats", response_class=HTMLResponse)
def get_stats(request: Request):
    buckets = db.get_all_buckets()
    income_bucket = sum_of_bucket(buckets["income"])
    total = 0
    for key in buckets.keys():
        if not key == "income":
            total += sum_of_bucket(buckets[key])

    return templates.TemplateResponse(
        "stats.html",
        {"request": request, "income": income_bucket, "out": total},
    )


def sum_of_bucket(bucket):
    return sum([row[2] for row in bucket])
