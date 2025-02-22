from dataclasses import dataclass


@dataclass
class MCT:
    airport: str
    origin_carrier: str
    dest_carrier: str
    time: int
    sender_mail_id: str
