import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.losses import SparseCategoricalCrossentropy
import numpy as np


class DigitClassification:
    def __init__(self):
        # Load MNIST data
        (self.X_train, self.y_train), (self.X_test, self.y_test) = tf.keras.datasets.mnist.load_data()

        # Normalize the data (0-255 -> 0-1)
        self.X_train = self.X_train.astype('float32') / 255.0
        self.X_test = self.X_test.astype('float32') / 255.0

        # Create the model
        self.model = Sequential([
            Flatten(input_shape=(28, 28)),
            Dense(units=128, activation='relu'),
            Dense(units=64, activation='relu'),
            Dense(units=10, activation='softmax')
        ])

        # Compile the model
        self.model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    def train(self):
        trained = self.model.fit(self.X_train, self.y_train, epochs=5, validation_split=0.2)
        return trained

    def predict(self, X_test):
        prediction = self.model.predict(X_test)
        predicted_classes = np.argmax(prediction, axis=1)
        return predicted_classes


# Test the model
if __name__ == "__main__":
    digit_classifier = DigitClassification()
    digit_classifier.train()
    predictions = digit_classifier.predict(digit_classifier.X_test)
    print("Tahmin edilen ilk 10 rakam:", predictions[:10])
    print("Gerçek ilk 10 etiket:", digit_classifier.y_test[:10])
