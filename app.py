from flask import Flask, render_template, request, jsonify
import numpy as np
import tensorflow as tf
from PIL import Image
import io
import base64

app = Flask(__name__)

# Load the trained model
model = tf.keras.models.load_model('digit_classifier.h5')
training_data = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.form['image'].split(',')[1]
    image_data = base64.b64decode(data)
    image = Image.open(io.BytesIO(image_data)).convert('L')
    image = image.resize((28, 28))
    image_array = np.array(image).astype('float32') / 255.0
    image_array = image_array.reshape(1, 28, 28)
    prediction = model.predict(image_array)
    predicted_digit = np.argmax(prediction, axis=1)[0]
    return jsonify({'digit': int(predicted_digit)})

@app.route('/train', methods=['POST'])
def train():
    data = request.form['image'].split(',')[1]
    digit = int(request.form['digit'])
    image_data = base64.b64decode(data)
    image = Image.open(io.BytesIO(image_data)).convert('L')
    image = image.resize((28, 28))
    image_array = np.array(image).astype('float32') / 255.0
    image_array = image_array.reshape(1, 28, 28, 1)

    training_data.append((image_array, digit))
    print(f"Added training data for digit {digit}")

    return jsonify({'message': f'Digit {digit} training data received'})

if __name__ == '__main__':
    app.run(debug=True)