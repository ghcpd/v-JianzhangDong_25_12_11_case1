from calc import add, div

def test_add():
    assert add(1, 2) == 3

def test_div():
    div(1, 0)

def test_syntax_error:
    assert True
