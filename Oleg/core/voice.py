import os
import tempfile
from typing import Optional
import soundfile as sf
import pygame
import torch
from num2words import num2words
from Oleg.utils.logger import logger
import time


_silero_model = None


def _get_silero_model():
    """Загружает модель Silero TTS (один раз)."""
    global _silero_model
    if _silero_model is not None:
        return _silero_model

    device = torch.device("cpu")
    torch.set_num_threads(4)
    model, _ = torch.hub.load(
        repo_or_dir="snakers4/silero-models",
        model="silero_tts",
        language="ru",
        speaker="v4_ru",
    )
    model.to(device)
    _silero_model = model
    logger.info("Silero TTS модель загружена")
    return _silero_model


def _numbers_to_words(text: str) -> str:
    """Заменяет целые числа на слова."""
    result = []
    for word in text.split():
        stripped = word.lstrip("-")
        if stripped.isdigit():
            try:
                result.append(num2words(int(stripped), lang="ru"))
            except Exception:
                result.append(word)
        else:
            result.append(word)
    return " ".join(result)


def say_text(text: str) -> None:
    """Озвучивает текст через Silero TTS."""
    model = _get_silero_model()
    prepared = _numbers_to_words(text)

    audio = model.apply_tts(
        text=prepared,
        speaker="eugene",
        sample_rate=48000,
        put_accent=True,
        put_yo=True,
    )

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, audio.numpy(), 48000)

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(tmp.name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


def process_result_and_restart(text: Optional[str]) -> None:
    """Озвучивает результат."""
    if text:
        logger.info(f"Ответ: {text}")
        say_text(text)
    else:
        logger.info("Нечего озвучивать")


def get_text_from_microphone() -> Optional[str]:
    """Распознавание речи с микрофона."""
    try:
        import speech_recognition as sr
    except ImportError:
        logger.error("speech_recognition не установлен")
        return None

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            return recognizer.recognize_google(audio, language="ru-RU").lower()
        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            return None


# ---------------------------Голосовой ввод для расчета материалов--------------------
def get_text_from_microphone_cal() -> Optional[str]:
    """Распознавание речи с подсказкой (для расчёта материалов)."""
    print("Скажите: N квадратов(площадь), X сантиметров(толщина)")
    print("Пример: 40 квадратов 5 сантиметров")
    for i in range(3, 0, -1):
        print(i, end=" ")
        time.sleep(1)
    print("\nГоворите!")

    return get_text_from_microphone()
