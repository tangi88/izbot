import db


def add_location(longitude: float, latitude: float) -> str:
    now_date = db.get_now_datetime()
    now_date_repr = db.date_formatted(now_date)

    inserted_row_id = db.insert("locations", {
        "date_create": now_date,
        "date_create_repr": now_date_repr,
        "latitude": latitude,
        "longitude": longitude
    })

    return f'добавлена локация {longitude},{latitude} {now_date_repr}'


def see_location() -> str:
    last_location = db.select_date_create("locations", [
        "date_create",
        "date_create_repr",
        "latitude",
        "longitude",
    ])

    if not last_location:
        return 'Не найдены локации'

    location = last_location[0]
    date_create, date_create_repr, latitude, longitude = location

    return f'https://nakarte.me/#nktp={latitude}/{longitude}/{date_create_repr}'

