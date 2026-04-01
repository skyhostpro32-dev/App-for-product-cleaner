import React, { useRef, useState } from "react";
import axios from "axios";

function App() {
  const canvasRef = useRef(null);
  const [drawing, setDrawing] = useState(false);
  const [imgFile, setImgFile] = useState(null);

  const handleUpload = (e) => {
    const file = e.target.files[0];
    setImgFile(file);

    const img = new Image();
    img.src = URL.createObjectURL(file);

    img.onload = () => {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");

      canvas.width = img.width;
      canvas.height = img.height;

      ctx.drawImage(img, 0, 0);
    };
  };

  const draw = (e) => {
    if (!drawing) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    ctx.fillStyle = "rgba(255,0,0,0.4)";
    ctx.beginPath();
    ctx.arc(x, y, 15, 0, 2 * Math.PI);
    ctx.fill();
  };

  const removeObject = async () => {
    const canvas = canvasRef.current;

    const maskBlob = await new Promise((resolve) =>
      canvas.toBlob(resolve, "image/png")
    );

    const formData = new FormData();
    formData.append("image", imgFile);
    formData.append("mask", maskBlob);

    const res = await axios.post(
      "http://localhost:8000/remove-object/",
      formData,
      { responseType: "blob" }
    );

    const url = URL.createObjectURL(res.data);
    window.open(url);
  };

  return (
    <div style={{ textAlign: "center" }}>
      <h2>AI Object Remover</h2>

      <input type="file" onChange={handleUpload} />

      <br /><br />

      <canvas
        ref={canvasRef}
        style={{ border: "1px solid black", cursor: "crosshair" }}
        onMouseDown={() => setDrawing(true)}
        onMouseUp={() => setDrawing(false)}
        onMouseMove={draw}
      />

      <br /><br />

      <button onClick={removeObject}>Remove Object</button>
    </div>
  );
}

export default App;
