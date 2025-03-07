from flask import Flask, render_template, request, jsonify
import numpy as np
import tensorflow as tf
from PIL import Image
import io
import base64

app = Flask(__name__)

# Eğitilmiş modeli yükle
model = tf.keras.models.load_model('digit_classifier.h5')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    # Kullanıcının çizdiği görüntüyü al (base64 formatında)
    data = request.form['image']
    # "data:image/png;base64," kısmını kaldır
    data = data.split(',')[1]
    # Base64'ü binary'ye çevir
    image_data = base64.b64decode(data)

    # Görüntüyü PIL ile aç ve gri tonlamaya çevir
    image = Image.open(io.BytesIO(image_data)).convert('L')
    image = image.resize((28, 28))  # MNIST için 28x28 boyutuna getir

    # Görüntüyü numpy dizisine çevir ve normalize et
    image_array = np.array(image).astype('float32') / 255.0
    image_array = image_array.reshape(1, 28, 28)  # Modelin beklediği şekle getir

    # Tahmin yap
    prediction = model.predict(image_array)
    predicted_digit = np.argmax(prediction, axis=1)[0]

    return jsonify({'digit': int(predicted_digit)})


if __name__ == '__main__':
    app.run(debug=True)