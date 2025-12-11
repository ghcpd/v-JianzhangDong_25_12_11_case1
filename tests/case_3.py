from app.model import build_model


def test_model():
    try:
        labels = build_model(["hello world", "test input", "another string"])
        print(labels)
        print("case_3 OK")
    except Exception as e:
        print("Dependency error in case_3:", e)
        raise