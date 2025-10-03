from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
import cv2
import numpy as np
from ultralytics import YOLO
import os
import tempfile
import json
import io

app = FastAPI(
    title="Mango Detection API",
    description="API for detecting ripe and unripe mangoes using YOLO",
    version="1.0.0"
)

# Allow CORS (for React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load best model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "best.pt")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model {MODEL_PATH} not found!")
model = YOLO(MODEL_PATH)

# Class names from data.yaml
CLASS_NAMES = ["ripe mango", "unripe mango"]

@app.post("/detect/video")
async def detect_video(file: UploadFile = File(...)):
    if not file.filename.endswith(('.mp4', '.avi', '.mov')):
        raise HTTPException(status_code=400, detail="Invalid video format")

    # Save uploaded video temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    cap = cv2.VideoCapture(tmp_path)
    if not cap.isOpened():
        os.unlink(tmp_path)  # Clean up input file
        raise HTTPException(status_code=500, detail="Could not open video")

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0 or fps > 60:
        fps = 30  # Default to 30 fps if cannot be determined or too high
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define output with X264 codec for better browser support
    output_path = tempfile.mktemp(suffix='.mp4')
    
    # Try X264 first, fall back to mp4v
    codecs_to_try = ['X264', 'x264', 'H264', 'h264', 'mp4v', 'MP4V']
    out = None
    working_codec = None
    
    for codec in codecs_to_try:
        try:
            fourcc = cv2.VideoWriter_fourcc(*codec)
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            if out.isOpened():
                working_codec = codec
                break
            out.release()
        except:
            continue
    
    if out is None or not out.isOpened():
        cap.release()
        os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail="Could not create output video writer with any codec")

    try:
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Run YOLO inference on every frame with lower confidence threshold
            # conf=0.15 means it will detect objects with 15% confidence or higher
            # imgsz=640 sets the inference size for better detection
            results = model(frame, conf=0.15, iou=0.4, imgsz=640)
            annotated_frame = results[0].plot()  # Draws boxes and labels

            out.write(annotated_frame)
            frame_count += 1
    finally:
        cap.release()
        out.release()
        os.unlink(tmp_path)  # Clean up input file

    # Check if output file was created and has content
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        if os.path.exists(output_path):
            os.unlink(output_path)
        raise HTTPException(status_code=500, detail="Failed to create output video")
    
    print(f"Video created successfully: {frame_count} frames processed, codec: {working_codec}, size: {os.path.getsize(output_path)} bytes")

    media_type = "video/mp4"

    # Create a generator that cleans up after streaming
    def iterfile():
        try:
            with open(output_path, mode="rb") as f:
                yield from f
        finally:
            # Clean up output file after streaming is complete
            if os.path.exists(output_path):
                os.unlink(output_path)

    return StreamingResponse(
        iterfile(), 
        media_type=media_type,
        headers={
            "Content-Disposition": f"inline; filename=detected_video.mp4",
            "Accept-Ranges": "bytes"
        }
    )


@app.post("/detect/image")
async def detect_image(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(status_code=400, detail="Invalid image format")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Run detection with lower confidence threshold for better detection
    results = model(img, conf=0.15, iou=0.4, imgsz=640)
    annotated_img = results[0].plot()

    # Convert back to JPEG
    _, buffer = cv2.imencode('.jpg', annotated_img)
    return StreamingResponse(io.BytesIO(buffer), media_type="image/jpeg")


@app.post("/detect/webcam-frame")
async def detect_webcam_frame(file: UploadFile = File(...)):
    """For real-time frame-by-frame detection from webcam"""
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Run detection with lower confidence threshold
    results = model(img, conf=0.15, iou=0.4, imgsz=640)
    detections = []

    for box in results[0].boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        xyxy = box.xyxy[0].tolist()
        class_name = CLASS_NAMES[cls]

        detections.append({
            "class": class_name,
            "confidence": conf,
            "bbox": xyxy
        })

    return JSONResponse({"detections": detections})


@app.get("/")
def read_root():
    return {
        "message": "Mango Detection API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "image_detection": "/detect/image",
            "video_detection": "/detect/video",
            "webcam_detection": "/detect/webcam-frame"
        }
    }


@app.get("/health")
def health():
    return {"status": "OK", "model_loaded": MODEL_PATH}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)