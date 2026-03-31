import shutil

# Move file
shutil.move("sample.txt", "test_folder/sample.txt")

# Copy file
shutil.copy("test_folder/sample.txt", "copy_sample.txt")