
import rect_area
import square_area
import circ_area

print("Enter 1 : Area of Rectangle")
print("Enter 2 : Area of Square")
print("Enter 3 : Area of Circle")

inp = int(input("Enter the number:"))

if(inp == 1):
    len = int(input("Enter the length :"))
    br = int(input("Enter the breadth: "))
    rect_area.rect_area(len,br)
elif(inp == 2):
    len = int(input("Enter the length: "))
    square_area.square_area(len)
elif ( inp == 3):
    rad = int(input("Enter the radius : "))
    circ_area.circ_area(rad)
else:
    print("Invalid Input!")