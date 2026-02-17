def square_numbers(n):
    for i in range(n + 1):
        yield i ** 2

def even_numbers(n):
    for i in range(n + 1):
        if i % 2 == 0:
            yield i

def divisible_by_3_and_4(n):
    for i in range(n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

def squares(a, b):
    for i in range(a, b + 1):
        yield i ** 2

def countdown(n):
    for i in range(n, -1, -1):
        yield i