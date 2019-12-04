from insilico import InsilicoClassifier


def test_environment():
    clf = InsilicoClassifier(auto_length=False)
    df = clf.get_sample_data()
    clf.fit(None, None).predict(df.iloc[:5])
