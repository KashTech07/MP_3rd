import pandas as pd

from database.database import (
    create_table,
    insert_groundwater_data,
    get_groundwater_data
)


def load_data():

    df = pd.read_csv("data/groundwater.csv")

    for _, row in df.iterrows():

        data = (
            row["state"],
            row["district"],
            row["rainfall_mm"],
            row["recharge_mcm"],
            row["extraction_mcm"],
            row["groundwater_level_m"],
            row["category"]
        )

        insert_groundwater_data(data)


create_table()
load_data()

data = get_groundwater_data()

for row in data:
    print(row)