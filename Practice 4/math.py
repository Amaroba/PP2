import math

def degree_to_radian():
    degree = float(input("Input degree: "))
    radian = math.radians(degree)
    print("Output radian:", round(radian, 6))

def trapezoid_area():
    height = float(input("Height: "))
    base1 = float(input("Base, first value: "))
    base2 = float(input("Base, second value: "))
    area = 0.5 * (base1 + base2) * height
    print("Expected Output:", area)

def regular_polygon_area():
    n_sides = int(input("Input number of sides: "))
    side_length = float(input("Input the length of a side: "))
    area = (n_sides * side_length ** 2) / (4 * math.tan(math.pi / n_sides))
    print("The area of the polygon is:", round(area, 2))

def parallelogram_area():
    base = float(input("Length of base: "))
    height = float(input("Height of parallelogram: "))
    area = base * height
    print("Expected Output:", area)

