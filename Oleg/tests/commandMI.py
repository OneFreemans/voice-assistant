commandOleg_valid = (
                     "Сколько время", "Погода - (город)", "Расскажи анекдот", "Открой - (сайт)",
                     "Какой сегодня день", "Курс - (валюта)",
                     "Сердце - (кол-во - цвет)", "Яндекс - (запрос в поисковике яндекса)",
                     "Отправь сообщение - (Подпись человека в вк - текст смс)", "Стоп\Олег стоп", "Последние сообщение",
                     "Ответь на сообщение - (текс смс)", "Запусти - (название приложения)",
                     "Включи\выключи - (название устройства умного дома)",
                     "Таймер - (время в минутах\секундах\часах)"
                     )


commandOleg_error = {

                     }

commandOleg_bug = {
                "Рассчитай стяжку - (следуйте инструкции)(требует проверки и оптимизации)",
                     }


print("""1: Работает 
2: Не работает 
3: С ошибками
4: Вывести все""")

numbers_command = int(input("Введите номер команды: "))


if numbers_command == 1:
    print("\n====================Работают======================")
    print(str(len(commandOleg_valid)))
    for i in commandOleg_valid:
        print(i)


elif numbers_command == 2:
    print("\n====================Не работают====================")
    print(str(len(commandOleg_error)))
    for i in commandOleg_error:
        print(i)


elif numbers_command == 3:
    print("\n====================С ошибками====================")
    print(str(len(commandOleg_bug)))
    for i in commandOleg_bug:
        print(i)


elif numbers_command == 4:
    print("\n====================Работают======================")
    print(str(len(commandOleg_valid)))
    for i in commandOleg_valid:
        print(i)

    print("\n====================Не работают====================")
    print(str(len(commandOleg_error)))
    for i in commandOleg_error:
        print(i)

    print("\n====================С ошибками====================")
    print(str(len(commandOleg_bug)))
    for i in commandOleg_bug:
        print(i)


print("\n\n====================Итог====================")
print("Работают - " + str(len(commandOleg_valid)))
print("Не работают - " + str(len(commandOleg_error)))
print("С ошибками - " + str(len(commandOleg_bug)))

