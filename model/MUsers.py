from utils.conexion import users_col, GenerarUuid
from typing import Union
from bson import ObjectId


def GetUserById(iduser: Union[str, ObjectId]):
    query = {"iduser": iduser} if isinstance(iduser, str) else {"_id": iduser}
    user_data = users_col.find_one(query)
    return user_data if user_data else None


def GetUserLogin(username: str, password: str):
    user_data = users_col.find_one(
        {"username": username, "password": password, "status": "A"}
    )
    return user_data if user_data else None


def RegUser(username: str, password: str):
    user_data = {"iduser": GenerarUuid(), "username": username, "password": password}
    result = users_col.insert_one(user_data)
    inserted_user = GetUserById(result.inserted_id)
    return inserted_user


def GetUsersList(**kwargs):
    buscar = kwargs.get("buscar", "")

    query = {}
    if buscar:
        query["$or"] = [
            {"username": {"$regex": "^" + buscar}},
            {"username": {"$regex": buscar, "$options": "i"}},
            {"nombre": {"$regex": "^" + buscar}},
            {"nombre": {"$regex": buscar, "$options": "i"}},
            {"apellido": {"$regex": "^" + buscar}},
            {"apellido": {"$regex": buscar, "$options": "i"}},
        ]

    users = users_col.find(query)
    return list(users)


def UpdateUserField(**kwargs):
    dato = kwargs["dato"]
    iduser = kwargs["iduser"]
    valor = kwargs["valor"]
    return users_col.update_one({"iduser": iduser}, {"$set": {dato: valor}})


def UpdateUserStatus(**kwargs):
    iduser = kwargs["iduser"]
    status = kwargs["status"]
    return users_col.update_one({"iduser": iduser}, {"$set": {"status": status}})


def UpdateProfile(**kwargs):
    iduser = kwargs["iduser"]
    del kwargs["iduser"]
    return users_col.update_one({"iduser": iduser}, {"$set": kwargs})


def GetUserByName(username: str):
    return users_col.find_one({"username": username})
