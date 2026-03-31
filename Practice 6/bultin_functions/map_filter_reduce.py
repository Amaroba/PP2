from functools import reduce

numbers = [1, 2, 3, 4, 5]

# map
squared = list(map(lambda x: x**2, numbers))
print(squared)

# filter
even = list(filter(lambda x: x % 2 == 0, numbers))
print(even)

# reduce
sum_numbers = reduce(lambda a, b: a + b, numbers)
print(sum_numbers)