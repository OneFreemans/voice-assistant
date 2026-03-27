import pyttsx3


# ---------------------------Функции озвучивания и перезапуска--------------------
def say_text(text, wait=True):
    """Озвучивает текст (с пересозданием движка для надежности)"""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'irina' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.say(text)
        if wait:
            engine.runAndWait()
    except Exception as e:
        print(f"Ошибка озвучки: {e}")


def process_result_and_restart(result, success_message=None):
    """Обрабатывает результат функции: выводит, озвучивает"""
    if isinstance(result, dict):
        if 'error' in result:
            say_text(result['error'])
            print(result['error'])
        elif 'message' in result:
            say_text(result['message'])
            print(result['message'])
        elif 'data' in result:
            say_text(result['data'])
            print(result['data'])
    elif result:
        say_text(result)
        print(result)

    if success_message:
        say_text(success_message)
        print(success_message)