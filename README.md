# hse-kpo-hw4

---
# ИДЗ №4 по предмету "Конструирование программного обеспечения"

# 2 курс ПИ, ФКН, НИУ ВШЭ

# Тема: Система обработки заказов ресторана

---

## *Цель задания:*

Разработать два отдельных микросервиса на основе RESTful API для системы обработки заказов в ресторане, первый из которых реализует авторизацию пользователей с различными ролями, а второй – управляет заказами и отслеживает запас блюд.

---

## *Структура проекта*

Полное описание условий задания можно найти [тут](https://github.com/kamilarakhimova/hse-kpo-hw4/blob/main/Условие%20дз4-КПО-2023.pdf).

В самом начале нам необходимо создать в папке [databases](https://github.com/kamilarakhimova/hse-kpo-hw4/blob/main/databases) базы данных "users.db" и "dishes_orders.db" (при их отсутствии) для дальнейшей корректной работы микросервисов. Сделаем это одним действием, запустив программу [main.py](https://github.com/kamilarakhimova/hse-kpo-hw4/blob/main/main.py) следующей командой в терминале:
```
$ python3 main.py
```

Файл для запуска микросервиса 1 "Авторизация пользователей" располагается в [данной](https://github.com/kamilarakhimova/hse-kpo-hw4/blob/main/enter) папке. Можно отдельно запустить только его, введя в терминал следующую команду:

```
$ python3 enter/app1.py
```

Аналогично для запуска микросервиса 2 "Обработка заказов" можно воспользоваться находящимся в [этой](https://github.com/kamilarakhimova/hse-kpo-hw4/blob/main/orders) директории программой. Для запуска только указанного микросервиса, набираем в терминале команду:

```
$ python3 orders/app2.py
```

Запустить всё вместе работать можно, введя две последние описанные команды в двух разных терминалах.

[надо ещё описать про postman и как вводить запросы]()

#### *Задание выполнено с расчётом на получение оценки в 10/10 баллов.* (пока что правда только на 4 наберется, но я собираюсь ещё поколдовать, мне интересно само задание)

---

### где милая картинка для восстановления поседевших волос препода после увиденной им моей работы??
