from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from joblib import dump


def build_model(texts, k=3):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)


    model = KMeans(n_clusters=k, n_init=10)
    model.fit(X)

    dump((vectorizer, model), "model.bin")
    return model.labels_