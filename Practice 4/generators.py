def square_numbers(n):
    for i in range(n + 1):
        yield i ** 2

n = int(input("Enter N: "))
for value in square_numbers(n):
    print(value)

def even_numbers(n):
    for i in range(n + 1):
        if i % 2 == 0:
            yield i

n = int(input("Enter n: "))
print(",".join(str(num) for num in even_numbers(n)))

def divisible_by_3_and_4(n):
    for i in range(n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

n = int(input("Enter n: "))
for num in divisible_by_3_and_4(n):
    print(num)

def squares(a, b):
    for i in range(a, b + 1):
        yield i ** 2

a = int(input("Enter a: "))
b = int(input("Enter b: "))

for value in squares(a, b):
    print(value)

def countdown(n):
    for i in range(n, -1, -1):
        yield i

n = int(input("Enter n: "))
for num in countdown(n):
    print(num)