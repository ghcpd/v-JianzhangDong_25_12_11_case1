from app.text_processor import normalize_text


def test_nltk():
    try:
        tokens = normalize_text("Hello World!")
        print(tokens)
        print("case_2 OK")
    except Exception as e:
        print("Dependency error in case_2:", e)
        raise