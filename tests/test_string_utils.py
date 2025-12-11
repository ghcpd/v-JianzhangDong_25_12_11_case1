from apps.string_utils import to_upper, reverse, concat

def test_to_upper():
    assert to_upper("abc") == "ABC"

def test_reverse():
    assert reverse("abc") == "cba"

def test_concat():
    assert concat("a", "b") == "ab"
