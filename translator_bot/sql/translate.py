import threading

from translator_bot.sql import BASE, SESSION
from sqlalchemy import Column, String, UnicodeText


class Translate(BASE):
    __tablename__ = "translate"
    id = Column(String, primary_key=True)
    translated_text = Column(UnicodeText, nullable=False)

    def __init__(self, id: int, translated_text: str) -> None:
        self.id = id
        self.translated_text = translated_text

    def __repr__(self) -> str:
        return f"<Translate(id={self.id}, translated_text='{self.translated_text}')>"


Translate.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def get_translation(id: int) -> str:
    try:
        result = SESSION.query(Translate).get(id)
    finally:
        SESSION.close()
    return result.translated_text if result else "Translation not found :("


def save_translation(id: int, translated_text: str) -> None:
    with INSERTION_LOCK:
        try:
            translation = SESSION.query(Translate).get(id)
            if not translation:
                translation = Translate(id, translated_text)
                SESSION.add(translation)
        finally:
            SESSION.commit()
            SESSION.close()
