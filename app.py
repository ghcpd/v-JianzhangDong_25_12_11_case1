import numpy as np
from calc import add, div

def main():
    print("Mini App Running")
    a = input("Enter number A: ")
    b = input("Enter number B: ")
    result1 = add(a, b)
    result2 = div(a, b)
    print("Add:", result1)
    print("Div:", result2)

if __name__ == "__main__":
    main()
