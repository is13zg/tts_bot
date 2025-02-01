import requests
import uuid
from config import Salut_speech_keys
import time

AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
SYNTHESIS_URL = "https://smartspeech.sber.ru/rest/v1/text:synthesize"
ASYNC_SYNTHESIS_URL = "https://smartspeech.sber.ru/rest/v1/text:async_synthesize"
TASK_STATUS_URL = "https://smartspeech.sber.ru/rest/v1/task:get"
DOWNLOAD_URL = "https://smartspeech.sber.ru/rest/v1/data:download"


# Уникальный идентификатор запроса (RqUID)

def get_token(key_number):
    # Тело запроса (выберите нужный scope)
    payload = {'scope': 'SALUTE_SPEECH_PERS'}

    # Заголовки запроса
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),  # Сгенерированный уникальный идентификатор запроса
        'Authorization': f'Basic {Salut_speech_keys[key_number]}'
        # Ваш ключ авторизации
    }

    # Отправка запроса
    response = requests.post(AUTH_URL, headers=headers, data=payload, verify="russiantrustedca.pem")
    return response.json()['access_token']


def synthesize_speech(text, key_number=0, voice="Bys_24000", output_file="output.wav"):
    token = get_token(key_number)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/text",
        "X-Request-ID": str(uuid.uuid4())
    }
    params = {
        "format": "wav16",
        "voice": voice
    }

    response = requests.post(SYNTHESIS_URL, headers=headers, params=params, data=text, verify="russiantrustedca.pem")
    response.raise_for_status()

    with open(output_file, "wb") as f:
        f.write(response.content)

    return output_file
