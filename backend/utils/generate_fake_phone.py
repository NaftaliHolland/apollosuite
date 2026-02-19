import uuid


def generate_fake_phone() -> str:
    unique_part = uuid.uuid4().int % 10**10
    return f"+999{str(unique_part).zfill(10)}"
