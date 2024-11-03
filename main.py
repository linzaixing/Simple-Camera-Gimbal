import cv2
import serial
import onnx_yolov8_detect as onnx_yolo

# 定义串口参数
SERIAL_PORT = 'COM6'  # 串口端口号
BAUDRATE = 115200  # 波特率

# 定义舵机控制参数
SERVO_MIN_ANGLEX = 0  # 舵机最小角度
SERVO_MAX_ANGLEX = 180  # 舵机最大角度

SERVO_MIN_ANGLEY = 90  # 舵机最小角度
SERVO_MAX_ANGLEY = 180  # 舵机最大角度

# 初始化串口
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)

ai_detector = onnx_yolo.YoloUtil()
# model_path = r"E:\pythonProject\DuduBot\models\yolov8s.onnx"
model_path = r"face_detctor.onnx"
session, model_inputs, input_width, input_height = ai_detector.init_detect_model(model_path)

# 打开USB相机
cap = cv2.VideoCapture(0)

# 假设这些变量是在函数外定义的
last_detection = (0, 0) # 用来存储上一次的检测结果


def detect_head_in_image(frame, ai_detector):
    global last_detection  # 声明我们要使用的全局变量
    # 这里应该是你的人头检测代码，返回人头框的位置(x, y, w, h)
    output_image, boxes = onnx_yolo.detect_run(frame,
                                               ai_detector,
                                               session,
                                               model_inputs,
                                               input_width,
                                               input_height)

    if boxes:  # 如果boxes不为空
        # 为了示例，我们假设人头框在图像中央
        x1, y1, width, height = boxes[0]
        # cv2.rectangle(frame, (x1, y1), (x1 + width, y1 + height), (0, 255, 0), 2)  # 绘制人头框
        x0 = x1 + width // 2
        y0 = y1 + height // 2
        last_detection = (x0, y0)  # 更新上一次的检测结果
        return x0, y0
    else:
        # 如果boxes为空，返回上一次的结果
        return last_detection if last_detection else (None, None)


def calculate_servo_angle(x, y, width, height):
    # 根据人头框的x,y位置计算舵机的角度
    # 这里只是一个简单的线性映射示例
    anglex = int((SERVO_MAX_ANGLEX - SERVO_MIN_ANGLEX) * (x / width)) + SERVO_MIN_ANGLEX
    angley = int((SERVO_MAX_ANGLEY - SERVO_MIN_ANGLEY) * (y / height)) + SERVO_MIN_ANGLEY
    return max(SERVO_MIN_ANGLEX, min(anglex, SERVO_MAX_ANGLEX)), max(SERVO_MIN_ANGLEX, min(angley, SERVO_MAX_ANGLEY))  # 限制角度在有效范围内


def send_angle_to_mcu(anglex, angley):
    try:
        if not ser.isOpen():
            ser.open()
        ser.write((str(anglex) + "\t" + str(angley) + '\n').encode('utf-8'))  # 发送数据并附加换行符
        print(f"Sent anglex: {anglex}, Sent angley: {angley}")

        # 处理接收
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').rstrip()
            print(f"Received from Arduino: {response}")

    except serial.SerialException as e:
        print(f"Error sending angle: {e}")

try:
    while True:
        # 读取一帧图像
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # 检测人头框
        x, y = detect_head_in_image(frame, ai_detector)

        # 计算舵机角度
        anglex, angley = calculate_servo_angle(x, y, input_width, input_height)

        # 发送角度到下位机
        send_angle_to_mcu(anglex, angley)

        # 显示图像
        cv2.imshow('Frame', frame)

        # 按'q'退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()
    ser.close()