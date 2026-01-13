import turtle
import sys

# Recursive function for one edge
def drawEdge(length, depth):
    if depth == 0:
        turtle.forward(length)
        return

    part = length / 3

    drawEdge(part, depth - 1)

    turtle.left(60)
    drawEdge(part, depth - 1)

    turtle.right(120)
    drawEdge(part, depth - 1)

    turtle.left(60)
    drawEdge(part, depth - 1)

# Draw the polygon (counter-clockwise)
def drawPolygon(sides, length, depth):
    angle = 360 / sides
    for _ in range(sides):
        drawEdge(length, depth)
        turtle.left(angle)

def main():
    # Input validation
    try:
        sides = int(input("Enter the number of sides: "))
    except ValueError:
        print("Number of sides must be a whole number.")
        sys.exit()

    if sides < 3:
        print("A polygon must have at least 3 sides.")
        sys.exit()

    try:
        length = int(input("Enter the side length: "))
    except ValueError:
        print("Side length must be a whole number.")
        sys.exit()

    if length <= 0:
        print("Side length must be greater than zero.")
        sys.exit()

    try:
        depth = int(input("Enter the recursion depth: "))
    except ValueError:
        print("Recursion depth must be a whole number.")
        sys.exit()

    if depth < 0:
        print("Recursion depth cannot be negative.")
        sys.exit()

    if depth > 6:
        print("Recursion depth too large. Please use 6 or less.")
        sys.exit()

    # Turtle setup
    turtle.speed(0)
    turtle.hideturtle()
    turtle.tracer(False)

    turtle.penup()
    turtle.goto(-length / 2, -length / 2)
    turtle.setheading(0)
    turtle.pendown()

    drawPolygon(sides, length, depth)

    turtle.update()
    turtle.done()

main()
