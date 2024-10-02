# Petra - [InDev] 🔴🟢🔵

## Requirements

Before running the project, make sure you have the following installed:
- Python 3.x
- OpenCV (`cv2`)
- PyTorch (`torch`)
- NumPy (`numpy`)
- Matplotlib (`matplotlib`)
- Ultralytics YOLO (`ultralytics`) - YoloV10

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/JNX03/Petra.git
   ```
   
2. Install the required Python packages:
   ```bash
   pip install opencv-python torch numpy matplotlib ultralytics
   ```

3. Ensure you have the pre-trained YOLO model file `best.pt` in the working directory.

## Usage

### Running the Main Script

1. Navigate to the project directory:
   ```bash
   cd Petra
   ```

2. Run the main script:<br><br>
   Tesing the AI (original code by Khett)
   ```bash
   python Main.py #For Testing
   ```
   <br>Game
   ```bash
   python GameOb.py #For Game
   ```

### How it Works

- The script captures video input from your webcam.
- It uses a YOLO model to detect objects in real-time.
- A grid is drawn on the video stream to track object movement.
- The speed of objects is calculated to classify performance into three categories: "Low", "Medium", and "High".
- The current classification and the rate of detected objects (`CC/sec`) are displayed on the video stream.
- The peak flow over time is plotted in a separate graph, which updates at regular intervals.

### Controls

- Press `q` to quit the video stream and stop the script.

## Notes

- The script automatically updates the peak flow graph every 10 frames.
- Modify the performance thresholds and other parameters in the script as needed for different use cases.

## This Project under MIT-LICENSE
```
MIT License

Copyright (c) 2024 Chawabhon netisingha

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
