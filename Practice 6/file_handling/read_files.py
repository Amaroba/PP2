# Reading files

file = open("sample.txt", "r")
print(file.read())
file.close()

# Using context manager (better way)
with open("sample.txt", "r") as f:
    print(f.readline())
    print(f.readlines())