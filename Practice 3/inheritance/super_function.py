class Animal:
    def speak(self):
        print("Animal makes a sound")


class Dog(Animal):
    def speak(self):
        super().speak()        # call parent method
        print("Dog says Woof") # extra behavior


d = Dog()
d.speak()
