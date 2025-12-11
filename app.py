import numpy as np
from calc import add, div

def main():
    print("Mini App Running")
    a = input("Enter number A: ")
    b = input("Enter number B: ")
    # Bug: 未进行 int 转换，导致 div 调用失败
    result1 = add(a, b)
    result2 = div(a, b)
    print("Add:", result1)
    print("Div:", result2)

if __name__ == "__main__":
    main()
