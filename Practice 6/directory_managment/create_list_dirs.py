import os

# Create directory
os.mkdir("test_folder")

# Create nested directories
os.makedirs("parent/child/grandchild")

# List files and folders
print(os.listdir())

# Current directory
print(os.getcwd())