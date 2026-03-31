names = ["Alice", "Bob", "Charlie"]
scores = [85, 90, 78]

# enumerate
for index, name in enumerate(names):
    print(index, name)

# zip
for name, score in zip(names, scores):
    print(name, score)

# sorted
numbers = [5, 2, 9, 1]
print(sorted(numbers))

# type conversions
print(int("10"))
print(float("3.14"))
print(str(100))