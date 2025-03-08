import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Flatten
import numpy as np


class DigitClassification:
    def __init__(self):
        (self.X_train, self.y_train), (self.X_test, self.y_test) = tf.keras.datasets.mnist.load_data()
        self.X_train = self.X_train.astype('float32') / 255.0
        self.X_test = self.X_test.astype('float32') / 255.0
        self.model = Sequential([
            Flatten(input_shape=(28, 28)),
            Dense(units=128, activation='relu'),
            Dense(units=64, activation='relu'),
            Dense(units=10, activation='softmax')
        ])
        self.model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    def train(self):
        self.model.fit(self.X_train, self.y_train, epochs=5, validation_split=0.2)

    def save_model(self):
        self.model.save('digit_classifier.h5')
        print("Model başarıyla 'digit_classifier.h5' olarak kaydedildi!")

    def predict(self):
        prediction = self.model.predict(self.X_test)
        predicted_classes = np.argmax(prediction, axis=1)
        return predicted_classes


if __name__ == "__main__":
    digit_classifier = DigitClassification()
    digit_classifier.train()
    digit_classifier.save_model()
    predictions = digit_classifier.predict()
    print("Tahmin edilen ilk 10 rakam:", predictions[:10])
    print("Gerçek ilk 10 etiket:      ", digit_classifier.y_test[:10])
