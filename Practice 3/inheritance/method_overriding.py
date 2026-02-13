class Animal:
    def speak(self):
        print("Animal makes a sound")


class Dog(Animal):   # Dog inherits from Animal
    def speak(self):  # overriding the method
        print("Dog says Woof")


a = Animal()
d = Dog()

a.speak()   # Animal makes a sound
d.speak()   # Dog says Woof
