from calc import add, div

def test_add():
    assert add(1, 2) == 3

def test_div():
    # Bug: ZeroDivisionError 未处理
    div(1, 0)

# SyntaxError: 缺失括号
def test_syntax_error:
    assert True
