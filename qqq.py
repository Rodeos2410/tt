#Задание 1
a = int(input("Введите первую цифру: "))
b = int(input("Введите вторую цифру: "))
c = int(input("Введите третью цифру: "))

number = a * 100 + b * 10 + c
print("Полученное число:", number)

#Задание 2
number = input("Введите четырёхзначное число: ")

product = 1
for digit in number:
    product *= int(digit)

print("Произведение цифр:", product)



#Задание 3
meters = float(input("Введите количество метров: "))

centimeters = meters * 100
decimeters = meters * 10
millimeters = meters * 1000
miles = meters * 0.000621371

print(f"{meters} м = {centimeters} см")
print(f"{meters} м = {decimeters} дм")
print(f"{meters} м = {millimeters} мм")
print(f"{meters} м = {miles} миль")


#Задание 4
base = float(input("Введите основание треугольника: "))
height = float(input("Введите высоту треугольника: "))

area = 0.5 * base * height
print("Площадь треугольника:", area)


#Задание 5
number = input("Введите четырёхзначное число: ")

reversed_number = number[::-1]
print("Перевёрнутое число:", reversed_number)