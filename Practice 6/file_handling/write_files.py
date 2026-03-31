# Writing to a file

with open("sample.txt", "w") as f:
    f.write("Hello\n")
    f.write("This is a sample file\n")

# Appending to a file

with open("sample.txt", "a") as f:
    f.write("New line added\n")