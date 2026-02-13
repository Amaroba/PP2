class Father:
    def skills(self):
        print("Gardening")


class Mother:
    def talent(self):
        print("Cooking")


class Child(Father, Mother):   # inherits from both
    pass


c = Child()

c.skills()   # Gardening
c.talent()   # Cooking
