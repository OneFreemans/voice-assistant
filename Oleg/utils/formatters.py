def _format(count, one, few, many):
    count = int(count)

    if 11 <= count <= 19:
        return many

    last_digit = int(str(count)[-1])
    if last_digit == 1:
        return one
    elif 2 <= last_digit <= 4:
        return few
    else:
        return many


def mesh(count):
    return _format(count, 'мешок', 'мешка', 'мешков')


def rub(count):
    return _format(count, 'рубль', 'рубля', 'рублей')


def cop(count):
    return _format(count, 'копейка', 'копейки', 'копеек')


def min(count):
    return _format(count, 'минута', 'минуты', 'минут')