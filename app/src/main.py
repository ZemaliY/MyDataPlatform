from enum import Enum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google.cloud import bigquery
import json

app = FastAPI()

class Category(Enum):
    TOOLS = 'tools'
    CONSUMABLES = 'consumables'

class Item(BaseModel):
    name: str
    price: float
    count: int
    id: int
    category: Category
    ts_vac : str

class InitMessage(BaseModel):
    raw_pattern: str
    id_traitement: str
    ts_vac: str
    is_update: bool = Field(default=False)
    other_field: str

json_data = '''
[
    {
        "name": "Hammer",
        "price": 9.99,
        "count": 20,
        "id": 0,
        "category": "consumables",
        "ts_vac" : "2023-08-01"
    },
    {
        "name": "Pliers",
        "price": 1.99,
        "count": 200,
        "id": 2,
        "category": "tools",
        "ts_vac" : "2023-08-05"
    },
    {
        "name": "Nails",
        "price": 1.99,
        "count": 200,
        "id": 2,
        "category": "tools",
        "ts_vac" : "2023-08-01"
    }
]
'''


items = {
    0: Item(name="Hammer", price=9.99, count=20, id=0, category=Category.TOOLS, ts_vac="2023-08-01"),
    1: Item(name="Pliers", price=5.99, count=20, id=1, category=Category.TOOLS, ts_vac="2023-08-05"),
    2: Item(name="Nails", price=1.99, count=100, id=2, category=Category.CONSUMABLES, ts_vac="2023-08-01")
}

def delete_data(bigquery_client,init_messag):
    table_id = f"sbx-mydataplatform.test.table_item"

    # Construire la requête SQL de suppression
    query = f""" DELETE FROM `{table_id}` WHERE ts_vac = @ts_vac_value """

    # Configurer les paramètres de la requête
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("ts_vac_value", "STRING", init_messag.ts_vac)
        ]
    )

    # Exécuter la requête
    query_job = bigquery_client.query(query, job_config=job_config)

    # Attendre la fin de la requête
    query_job.result()

    print(f"Lignes supprimées de la table {table_id} où ts_vac = {init_messag.ts_vac}")

# FastAPI handles JSON serialization and deserialization for us.
# We can simply use built-in python and Pydantic types, in this case dict[int, Item].
@app.get("/v1/items")
def index() -> dict[str, dict[int, Item]]:
    return {"items": items}

@app.post("/items")
def add_item(item: Item) -> dict[str, Item]:

    if item.id in items:
        HTTPException(status_code=400, detail=f"Item with {item.id=} already exists.")

    items[item.id] = item
    return {"added": item}

@app.post("/v1/checkFiles")
def load_files_run(init_messag: InitMessage):

    is_update=init_messag.is_update
    bigquery_client = bigquery.Client(project='sbx-mydataplatform')
    schema = bigquery_client.schema_from_json("src/schema.json")

    destination = 'sbx-mydataplatform.test.table_item'

    job_config = bigquery.LoadJobConfig(
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        schema=schema,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    )

    records = json.loads(json_data)
    load_job = bigquery_client.load_table_from_json(
        json_rows= records,
        destination=destination,
        job_config=job_config
    )

    load_job.result()

    print("#######The GCS Raw file was correctly loaded to the BigQuery table#######")
    if is_update:
        print( f"Update : {is_update}")
        delete_data(bigquery_client,init_messag)

    else :
        print( f"Update : {is_update}")