from sklearn.ensemble import RandomForestClassifier

def train_model():
    # Training data
    X = [
        [10, 0],  # attack
        [1, 5],   # normal
        [8, 0],   # attack
        [0, 3],   # normal
    ]

    y = ["HIGH", "LOW", "HIGH", "LOW"]

    model = RandomForestClassifier()
    model.fit(X, y)

    return model


def predict_threat(model, failed, success):
    return model.predict([[failed, success]])[0]
