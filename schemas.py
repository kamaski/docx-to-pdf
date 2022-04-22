import os
from pydantic import BaseModel
from datetime import date
from thefuzz import fuzz
from transliterate import translit, detect_language
from db import get_sanctioned_people


class Client(BaseModel):
    """модель получемых данных"""
    first_name: str
    second_name: str
    last_name: str
    birth_date: date
    birth_place: str
    category: str
    nationality: str


def get_list_data_sanction():
    """получить обработанный список из базы данных"""
    # блэк лист из базы
    sanctioned_list = []
    fio_client_list = []
    sanctioned_people = get_sanctioned_people()
    for item in sanctioned_people:
        sanctioned_data = [str(item[5]).strip(), str(item[6]).strip(), str(item[7]).strip(), str(item[8].strftime('%Y-%m-%d')).strip(), str(item[9]).strip(), str(item[10]).strip(), str(item[11]).strip()]
        fio_data = [str(item[5]).strip(), str(item[6]).strip(), str(item[7]).strip()]
        fio_client_list.append(" ".join(fio_data))
        sanctioned_list.append(" ".join(sanctioned_data))
    return sanctioned_list, fio_client_list


def get_translit_client(client):
    """получить транслитерацию"""
    en_client = []
    en_fio_client = []
    ru_client = []
    ru_fio_client = []
    language = detect_language(client.first_name)
    if language == 'ru':
        # полные данные
        en_client.append(translit(client.first_name, language_code='ru', reversed=True))
        en_client.append(translit(client.second_name, language_code='ru', reversed=True))
        en_client.append(translit(client.last_name, language_code='ru', reversed=True))
        en_client.append(client.birth_date.strftime('%Y-%m-%d'))
        en_client.append(translit(client.birth_place, language_code='ru', reversed=True))
        en_client.append(translit(client.category, language_code='ru', reversed=True))
        en_client.append(translit(client.nationality, language_code='ru', reversed=True))
        # ФИО
        en_fio_client.append(translit(client.first_name, language_code='ru', reversed=True))
        en_fio_client.append(translit(client.second_name, language_code='ru', reversed=True))
        en_fio_client.append(translit(client.last_name, language_code='ru', reversed=True))
        return " ".join(en_client), " ".join(en_fio_client)
    if language == None:
        # полные данные
        ru_client.append(translit(client.first_name, 'ru'))
        ru_client.append(translit(client.second_name, 'ru'))
        ru_client.append(translit(client.last_name, 'ru'))
        ru_client.append(client.birth_date.strftime('%Y-%m-%d'))
        ru_client.append(translit(client.birth_place, 'ru'))
        ru_client.append(translit(client.category, 'ru'))
        ru_client.append(translit(client.nationality, 'ru'))

        # ФИО
        ru_fio_client.append(translit(client.first_name, 'ru'))
        ru_fio_client.append(translit(client.second_name, 'ru'))
        ru_fio_client.append(translit(client.last_name, 'ru'))

        return " ".join(ru_client), " ".join(ru_fio_client)


def compare_and_answer(data_list, client_data):
    for item in data_list:
        if fuzz.ratio(item, client_data) > int(os.getenv("COINCIDENCE")):
            return 1