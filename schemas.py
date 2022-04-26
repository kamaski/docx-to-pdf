import os
from pydantic import BaseModel
from thefuzz import fuzz
from transliterate import translit, detect_language
from db import get_sanctioned_people


class Client(BaseModel):
    """модель получемых данных"""
    name: str
    surname: str
    pater_name: str
    date_of_birth: str
    place_of_birth: str
    nationality: str


def get_list_data_sanction():
    """получить обработанный список из базы данных"""
    # блэк лист из базы
    sanctioned_list = []
    fio_client_list = []
    id = []
    sanctioned_people = get_sanctioned_people()
    for item in sanctioned_people:
        sanctioned_data = [str(item[4]).strip(), str(item[5]).strip(), str(item[9]).strip(), str(item[7].strip()), str(item[8]).strip(), str(item[10]).strip()]
        fio_data = [str(item[4]).strip(), str(item[5]).strip(), str(item[9]).strip()]
        fio_client_list.append(" ".join(fio_data))
        sanctioned_list.append(" ".join(sanctioned_data))
        id.append(item[0])
    return sanctioned_list, fio_client_list, id


def get_translit_client(client):
    """получить транслитерацию"""
    en_client = []
    en_fio_client = []
    ru_client = []
    ru_fio_client = []
    language = detect_language(client.name)
    if language == 'ru':
        # полные данные
        en_client.append(translit(client.name, language_code='ru', reversed=True))
        en_client.append(translit(client.surname, language_code='ru', reversed=True))
        en_client.append(translit(client.pater_name, language_code='ru', reversed=True))
        en_client.append(client.date_of_birth)
        en_client.append(translit(client.place_of_birth, language_code='ru', reversed=True))
        en_client.append(translit(client.nationality, language_code='ru', reversed=True))
        # ФИО
        en_fio_client.append(translit(client.name, language_code='ru', reversed=True))
        en_fio_client.append(translit(client.surname, language_code='ru', reversed=True))
        en_fio_client.append(translit(client.pater_name, language_code='ru', reversed=True))
        return " ".join(en_client), " ".join(en_fio_client)
    if language == None:
        # полные данные
        ru_client.append(translit(client.name, 'ru'))
        ru_client.append(translit(client.surname, 'ru'))
        ru_client.append(translit(client.pater_name, 'ru'))
        ru_client.append(client.date_of_birth)
        ru_client.append(translit(client.place_of_birth, 'ru'))
        ru_client.append(translit(client.nationality, 'ru'))

        # ФИО
        ru_fio_client.append(translit(client.name, 'ru'))
        ru_fio_client.append(translit(client.surname, 'ru'))
        ru_fio_client.append(translit(client.pater_name, 'ru'))

        return " ".join(ru_client), " ".join(ru_fio_client)


def compare_and_answer(data_list, client_data, id):
    i = 0
    for item in data_list:
        if fuzz.ratio(item, client_data) > int(os.getenv("COINCIDENCE")):
            return id[i]
        i += 1