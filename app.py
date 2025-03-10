from flask import Flask, render_template, request, jsonify
import numpy as np
import tensorflow as tf
from PIL import Image
import io
import base64

app = Flask(__name__)

#Load the trained model
model = tf.keras.models.load_model('digit_classifier.h5')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    #Take the image (base64 format)
    data = request.form['image']
    #Remove"data:image/png;base64,"
    data = data.split(',')[1]
    #Turn Base64 to binary
    image_data = base64.b64decode(data)

    #Open the image with PIL and convert to grayscale
    image = Image.open(io.BytesIO(image_data)).convert('L')
    image = image.resize((28, 28))  #Resize to 28x28 for MNIST

    #Turn image to a numpy array and normalize
    image_array = np.array(image).astype('float32') / 255.0
    image_array = image_array.reshape(1, 28, 28)  #Make the model look as expected

    #Predict
    prediction = model.predict(image_array)
    predicted_digit = np.argmax(prediction, axis=1)[0]

    return jsonify({'digit': int(predicted_digit)})


if __name__ == '__main__':
    app.run(debug=True)
