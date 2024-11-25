import db


def add_shot(shot: str) -> str:

    now_date = db.get_now_datetime()
    now_date_repr = db.date_formatted(now_date)

    inserted_row_id = db.insert("shots", {
        "date_create": now_date,
        "date_create_repr": now_date_repr,
        "side": shot
    })

    return f'добавлен укол {shot} {now_date_repr}'

