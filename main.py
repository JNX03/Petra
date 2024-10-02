import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt
from ultralytics import YOLO

model = YOLO("best.pt")
cap = cv2.VideoCapture(0)

speed_values = []
peak_flow_values = []
previous_positions = []
cc_per_sec = 0

def update_peak_flow_graph():
    plt.clf()
    plt.plot(peak_flow_values, label='Peak Flow', color='blue')
    plt.title("Peak Flow Over Time")
    plt.xlabel("Frames")
    plt.ylabel("Peak Flow")
    plt.legend()
    plt.pause(0.001)

plt.ion()

grid_size = 15
frame_height, frame_width = 480, 640
square_height = frame_height // grid_size
square_width = frame_width // grid_size

performance_thresholds = {
    "Low": (0, 1),
    "Medium": (1, 2),
    "High": (2, 3)
}

last_patient_class = "N/A"
frame_count = 0
update_interval = 10

try:
    while True:
        frame_count += 1
        ret, frame = cap.read()
        if not ret:
            break

        for i in range(1, grid_size):
            cv2.line(frame, (0, i * square_height), (frame_width, i * square_height), (255, 255, 255), 1)
            cv2.line(frame, (i * square_width, 0), (i * square_width, frame_height), (255, 255, 255), 1)

        with torch.no_grad():
            results = model(frame)

        detections = results[0].boxes.xyxy.cpu().numpy()
        current_positions = []
        ball_count = len(detections)
        cc_per_sec = ball_count * 600

        classified_patient_class = "N/A"

        for detection in detections:
            x1, y1, x2, y2 = detection[:4]
            current_positions.append((int((x1 + x2) / 2), int((y1 + y2) / 2)))
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        if previous_positions:
            for current_pos in current_positions:
                for prev_pos in previous_positions:
                    if current_pos != prev_pos:
                        x_move = (current_pos[0] // square_width) - (prev_pos[0] // square_width)
                        y_move = (current_pos[1] // square_height) - (prev_pos[1] // square_height)
                        speed = np.sqrt(x_move ** 2 + y_move ** 2)
                        speed_values.append(speed)
                        peak_flow = np.mean(speed_values)
                        peak_flow_values.append(peak_flow)
                        for patient_class, (lower, upper) in performance_thresholds.items():
                            if lower <= speed < upper:
                                classified_patient_class = patient_class
                                break

        last_patient_class = classified_patient_class if classified_patient_class != "N/A" else last_patient_class
        cv2.putText(frame, f"Patient Class: {last_patient_class}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(frame, f"CC/sec: {cc_per_sec}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        previous_positions = current_positions
        cv2.imshow("Object Detection", frame)

        if frame_count % update_interval == 0:
            update_peak_flow_graph()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    plt.ioff()
    plt.show()
