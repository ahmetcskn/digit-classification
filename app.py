from flask import Flask, render_template, request, jsonify, session
import numpy as np
import tensorflow as tf
from PIL import Image
import io
import base64
import pickle
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

model = tf.keras.models.load_model('digit_classifier.h5')
training_data = []
TRAINING_DATA_FILE = 'training_data.pkl'
LOG_FILE = 'training_log.txt'


def save_training_data():
    with open(TRAINING_DATA_FILE, 'wb') as f:
        pickle.dump(training_data, f)


def load_training_data():
    global training_data
    try:
        with open(TRAINING_DATA_FILE, 'rb') as f:
            training_data = pickle.load(f)
    except FileNotFoundError:
        training_data = []


def log_training(message):
    with open(LOG_FILE, 'a') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"{timestamp} - {message}\n")


def validate_image(image_array):
    total_pixels = np.sum(image_array)
    print(f"Validating image, total pixels: {total_pixels}")
    if total_pixels < 30:
        return False, "Image is too empty."
    pixel_density = np.sum(image_array > 0.1) / (28 * 28)
    print(f"Pixel density: {pixel_density}")
    if pixel_density < 0.03:
        return False, "Image density too low."
    return True, "Image validated."


def plot_training_results(history=None):
    plt.figure(figsize=(10, 6))
    plt.plot(history.history['accuracy'] if history else [0], label='Accuracy')
    plt.title('Model Training Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    plt.savefig('static/training_accuracy.png')
    plt.close()


def calculate_training_stats():
    stats = {
        'total_digits': len(training_data),
        'unique_digits': len(set([item[1] for item in training_data])),
        'training_time': 0
    }
    return stats


load_training_data()
log_training("Application started.")


@app.route('/')
def index():
    session['current_digit'] = session.get('current_digit', 0)
    log_training("User navigated to index page.")
    return render_template('index.html', current_digit=session['current_digit'], message='')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.form['image'].split(',')[1]
        image_data = base64.b64decode(data)
        image = Image.open(io.BytesIO(image_data)).convert('L')
        image = image.resize((28, 28))
        image_array = np.array(image).astype('float32') / 255.0
        image_array = image_array.reshape(1, 28, 28)

        total_pixels = np.sum(image_array)
        print(f"Total pixels in predict: {total_pixels}")
        if total_pixels < 30:
            log_training("Prediction failed: Canvas is empty.")
            return jsonify({'message': 'Draw a digit.'})

        prediction = model.predict(image_array)
        predicted_digit = np.argmax(prediction, axis=1)[0]
        log_training(f"Prediction made: Predicted digit {predicted_digit}")
        return jsonify({'digit': int(predicted_digit)})
    except Exception as e:
        log_training(f"Prediction error: {str(e)}")
        return jsonify({'message': 'Error processing image.'})


@app.route('/train', methods=['GET', 'POST'])
def train():
    global training_data, model
    start_time = time.time()
    if request.method == 'GET':
        session['current_digit'] = 0
        message = f"Draw digit {session['current_digit']}. Press Done when ready."
        log_training(f"Training session started at digit {session['current_digit']}")
        return render_template('index.html', current_digit=session['current_digit'], message=message)

    elif request.method == 'POST':
        try:
            data = request.form['image'].split(',')[1]
            digit = int(request.form['digit'])
            print(f"Received digit: {digit}")
            image_data = base64.b64decode(data)
            image = Image.open(io.BytesIO(image_data)).convert('L')
            image = image.resize((28, 28))
            image_array = np.array(image).astype('float32') / 255.0
            image_array = image_array.reshape(28, 28)  # 4D’den 2D’ye düzeltildi

            is_valid, validation_message = validate_image(image_array.reshape(1, 28, 28))  # Doğrulama için 3D
            if not is_valid:
                log_training(f"Validation failed for digit {digit}: {validation_message}")
                message = validation_message
                return render_template('index.html', current_digit=session['current_digit'], message=message)

            training_data.append((image_array, digit))
            log_training(f"Added training data for digit {digit}")
            save_training_data()

            session['current_digit'] += 1
            if session['current_digit'] <= 9:
                message = f"Draw digit {session['current_digit']}. Press Done when ready."
                log_training(f"Proceeded to digit {session['current_digit']}")
                return render_template('index.html', current_digit=session['current_digit'], message=message)
            else:
                if training_data:
                    X_train = np.array([item[0] for item in training_data])
                    y_train = np.array([item[1] for item in training_data])
                    X_train = X_train.reshape(X_train.shape[0], 28, 28)  # Model için 3D
                    history = model.fit(X_train, y_train, epochs=5, verbose=1)
                    model.save('digit_classifier.h5')
                    plot_training_results(history)
                    training_time = time.time() - start_time
                    stats = calculate_training_stats()
                    stats['training_time'] = training_time
                    log_training(f"Model retrained. Training time: {training_time}s, Stats: {stats}")
                    print("Model retrained and saved!")
                message = f"Training completed! Model updated. Time: {training_time:.2f}s, Stats: {stats}"
                session['current_digit'] = 0
                return render_template('index.html', current_digit=session['current_digit'], message=message)
        except Exception as e:
            log_training(f"Training error at digit {session['current_digit']}: {str(e)}")
            message = f"Error during training: {str(e)}"
            return render_template('index.html', current_digit=session['current_digit'], message=message)


if __name__ == '__main__':
    app.run(debug=True)
    print()
