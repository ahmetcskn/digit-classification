const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let drawing = false;
let lastX = 0;
let lastY = 0;

ctx.lineWidth = 15;  // Kalem genişliğini artır
ctx.lineCap = 'round';
ctx.strokeStyle = 'white';  // Beyaz çizgi, siyah zemin için

canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mouseup', stopDrawing);
canvas.addEventListener('mouseout', stopDrawing);
canvas.addEventListener('mousemove', draw);

function startDrawing(event) {
  drawing = true;
  const rect = canvas.getBoundingClientRect();
  lastX = event.clientX - rect.left;
  lastY = event.clientY - rect.top;
}

function stopDrawing() {
  drawing = false;
  ctx.beginPath();
}

function draw(event) {
  if (!drawing) return;
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  ctx.beginPath();
  ctx.moveTo(lastX, lastY);
  ctx.lineTo(x, y);
  ctx.stroke();
  lastX = x;
  lastY = y;
}

function clearCanvas() {
  ctx.fillStyle = 'black';  // Siyah zemin
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.beginPath();
  document.getElementById('result').innerText = '';
}

function predict() {
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = imageData.data;
  let isEmpty = true;
  for (let i = 0; i < data.length; i += 4) {
    if (data[i + 3] !== 0) {
      isEmpty = false;
      break;
    }
  }
  if (isEmpty) {
    document.getElementById('result').innerText = 'Draw a digit.';
    return;
  }

  const dataURL = canvas.toDataURL('image/png');
  fetch('/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'image=' + encodeURIComponent(dataURL)
  })
    .then(response => response.json())
    .then(data => {
      document.getElementById('result').innerText = `Predicted digit: ${data.digit}`;
    })
    .catch(error => console.error('Hata:', error));
}