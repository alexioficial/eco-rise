from flask import request, Response, after_this_request
from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv
from uuid import uuid4
from itsdangerous import Signer, BadSignature
from datetime import datetime

load_dotenv()

SECRET_KEY = getenv("SECRET_KEY")
signer = Signer(SECRET_KEY)

client = MongoClient(getenv("MONGO_URI"))
db = client[getenv("MONGO_DB")]

users_col = db["users"]
session_col = db["session_col"]
log_col = db["log_col"]
boss_col = db["boss"]
worker_col = db["worker"]
client_col = db["client"]
main_variables_col = db["main-variables"]
field_data_col = db["field-data"]
calculated_data_col = db["data"]


def GenerateUuid(sequences=1) -> str:
    result = ""
    for _ in range(sequences):
        result += uuid4().hex
    return result


class SessionMeta(type):
    def __getitem__(cls, key, sessionidsession=None):
        instance = cls(sessionidsession)
        instance._update_last_acceded()
        return instance[key]

    get = __getitem__

    def __setitem__(cls, key, value, sessionidsession=None):
        instance = cls(sessionidsession)
        instance._update_last_acceded()
        instance[key] = value

    def __contains__(cls, key):
        temp_session = cls()
        result = session_col.find_one({"__idsession": temp_session.idsession})
        return key in result.get("__data", {}) if result else False

    def to_dict(cls, sessionidsession=None):
        instance = cls(sessionidsession)
        doc = session_col.find_one({"__idsession": instance.idsession})
        return doc.get("__data", {}) if doc else {}


class Session(metaclass=SessionMeta):
    def __init__(self, sessionidsession=None):
        cookie_signed = request.cookies.get("idsession")
        self.idsession = None

        if sessionidsession:
            self.idsession = sessionidsession
        elif cookie_signed:
            try:
                self.idsession = signer.unsign(cookie_signed).decode()
            except BadSignature:
                self.idsession = str(uuid4())

        if not self.idsession:
            self.idsession = str(uuid4())

        self._update_last_acceded()

        host = request.host.split(":")[0]
        is_local = host in ["127.0.0.1", "localhost"]

        @after_this_request
        def set_cookie(response: Response):
            signed_value = signer.sign(self.idsession).decode()
            response.set_cookie(
                "idsession",
                signed_value,
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                secure=not is_local,
                samesite="Lax",
            )
            return response

    def _update_last_acceded(self):
        current_time = datetime.now()
        session_col.update_one(
            {"__idsession": self.idsession},
            {"$set": {"__last_acceded": current_time}},
            upsert=True,
        )

    def __setitem__(self, key, value):
        if value is None:
            return

        self._update_last_acceded()

        session_col.update_one(
            {"__idsession": self.idsession},
            {"$set": {f"__data.{key}": value}},
            upsert=True,
        )

    def __getitem__(self, key):
        self._update_last_acceded()

        doc = session_col.find_one({"__idsession": self.idsession})
        return doc.get("__data", {}).get(key) if doc else None

    @classmethod
    def clear(cls):
        cookie_signed = request.cookies.get("idsession")
        if not cookie_signed:
            return

        try:
            idsession_to_clear = signer.unsign(cookie_signed).decode()
        except BadSignature:
            idsession_to_clear = None

        if idsession_to_clear:
            session_col.delete_one({"__idsession": idsession_to_clear})

        host = request.host.split(":")[0]
        is_local = host in ["127.0.0.1", "localhost"]

        @after_this_request
        def delete_cookie(response: Response):
            response.set_cookie(
                "idsession",
                "",
                max_age=0,
                httponly=True,
                secure=not is_local,
                samesite="Lax",
            )
            return response
