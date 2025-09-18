#Задание 1
weight = float(input("Введите вес посылки (кг): "))

if weight <= 2:
    cost = 300
elif 2 < weight <= 5:
    cost = 500
elif 5 < weight <= 10:
    cost = 800
else:
    cost = 1200

print(f"Стоимость доставки: {cost} руб.")



#Задание 1
weight = float(input("Введите ваш вес (кг): "))
height = float(input("Введите ваш рост (м): "))

bmi = weight / (height ** 2)

if bmi < 18.5:
    category = "Недостаточный вес"
elif 18.5 <= bmi < 25:
    category = "Нормальный вес"
elif 25 <= bmi < 30:
    category = "Избыточный вес"
else:
    category = "Ожирение"

print(f"Ваш ИМТ: {bmi:.2f} ({category})")


#Задание 1
ticket_price = 500
money = float(input("Сколько у вас денег? "))

if money >= ticket_price:
    change = money - ticket_price
    print(f"Вы можете купить билет. Ваша сдача: {change:.2f} руб.")
else:
    print("У вас недостаточно денег для покупки билета.")



#Задание 1
    number = int(input("Введите число: "))

if number % 2 == 0:
    parity = "четное"
else:
    parity = "нечетное"

if number > 0:
    sign = "положительное"
elif number < 0:
    sign = "отрицательное"
else:
    sign = "ноль"

print(f"Число {number} — {parity} и {sign}.")



#Задание 1
month = int(input("Введите номер месяца (1-12): "))

if 1 <= month <= 2 or month == 12:
    season = "Зима"
elif 3 <= month <= 5:
    season = "Весна"
elif 6 <= month <= 8:
    season = "Лето"
elif 9 <= month <= 11:
    season = "Осень"
else:
    season = "Ошибка: введите число от 1 до 12"

print(f"Сезон: {season}")





#Задание 1
age = int(input("Введите ваш возраст: "))
salary = float(input("Введите вашу зарплату (руб): "))

if (21 <= age <= 65 and salary > 30000) or (salary > 50000 and age >= 18):
    print("Вы можете получить кредит!")
else:
    print("К сожалению, вы не можете получить кредит.")




#Задание 1
    day = int(input("Введите номер дня недели (1-7): "))

if day == 1:
    print("Понедельник")
elif day == 2:
    print("Вторник")
elif day == 3:
    print("Среда")
elif day == 4:
    print("Четверг")
elif day == 5:
    print("Пятница")
elif day == 6:
    print("Суббота")
elif day == 7:
    print("Воскресенье")
else:
    print("Ошибка: введите число от 1 до 7")