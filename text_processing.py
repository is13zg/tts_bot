import os
import pdfplumber
from docx import Document
import requests
from bs4 import BeautifulSoup
import re

def extract_text_from_file(file_path):
    """Извлекает текст из переданного файла"""
    _, ext = os.path.splitext(file_path)
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".pdf":
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    elif ext == ".docx":
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return "Формат файла не поддерживается. Поддерживаются: .txt, .pdf, .docx"

def extract_text_from_url(url):
    """Извлекает основной текст из веб-страницы"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        return "\n".join([p.get_text() for p in paragraphs])  # Ограничиваем 4000 символами
    except Exception as e:
        return f"Ошибка при получении текста с сайта: {str(e)}"


import re


def split_text(text, max_len=4000):
    # Регулярное выражение для поиска ссылок (http, https, www)
    url_pattern = re.compile(r'(https?://\S+|www\.\S+)')
    # Получаем список кортежей (начало, конец) для найденных ссылок
    url_spans = [match.span() for match in url_pattern.finditer(text)]

    parts = []
    offset = 0
    text_length = len(text)

    while offset < text_length:
        end = offset + max_len
        if end >= text_length:
            parts.append(text[offset:].strip())
            break

        chunk = text[offset:end]

        # Ищем с конца подстроки точку, которая не входит в ссылку
        dot_index = None
        pos = chunk.rfind('.')
        while pos != -1:
            absolute_pos = offset + pos
            # Проверяем, находится ли точка в пределах какой-либо ссылки
            if any(start <= absolute_pos < end_ for start, end_ in url_spans):
                pos = chunk.rfind('.', 0, pos)
                continue
            else:
                dot_index = pos
                break

        if dot_index is not None:
            split_point = dot_index + 1  # включаем точку
        else:
            # Если подходящая точка не найдена, ищем последний пробел
            last_space = chunk.rfind(' ')
            if last_space != -1:
                split_point = last_space
            else:
                split_point = max_len

        parts.append(text[offset:offset + split_point].strip())
        offset += split_point

    return parts


