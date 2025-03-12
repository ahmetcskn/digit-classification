const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let drawing = false;

ctx.lineWidth = 15;
ctx.lineCap = 'round';
ctx.strokeStyle = 'white';

canvas.onmousedown = e => {
    drawing = true;
    const { left, top } = canvas.getBoundingClientRect();
    ctx.beginPath();
    ctx.moveTo(e.clientX - left, e.clientY - top);
    console.log("Mouse down at:", e.clientX - left, e.clientY - top);
};

canvas.onmouseup = canvas.onmouseout = () => (drawing = false);

canvas.onmousemove = e => {
    if (!drawing) return;
    const { left, top } = canvas.getBoundingClientRect();
    const x = e.clientX - left, y = e.clientY - top;
    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
};

function clearCanvas() {
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    document.getElementById('result').innerText = '';
}

function predict() {
    const dataURL = canvas.toDataURL('image/png');
    console.log("DataURL length:", dataURL.length);
    fetch('/predict', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: `image=${encodeURIComponent(dataURL)}` })
        .then(res => {
            if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            document.getElementById('result').innerText = data.message || `Predicted digit: ${data.digit}`;
            console.log("Prediction response:", data);
        })
        .catch(err => {
            console.error('Hata:', err);
            document.getElementById('result').innerText = 'Error during prediction.';
        });
}