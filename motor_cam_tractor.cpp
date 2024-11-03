#include <Arduino.h>
#include <Servo.h>

// 定义舵机控制引脚
#define SERVO_PIN_X 2  // 使用数字引脚2控制X轴舵机
#define SERVO_PIN_Y 3  // 使用数字引脚3控制Y轴舵机

// 创建舵机对象
Servo servoX;
Servo servoY;

int angleX;  // 用户指令数据X轴
int angleY;  // 用户指令数据Y轴
String inputString = "";  // 用于存储从串口读取的字符串

void setup() {
  // 将舵机附加到对应的引脚上
  servoX.attach(SERVO_PIN_X);
  servoY.attach(SERVO_PIN_Y);
  
  // 设置舵机的初始位置为90度
  servoX.write(90);
  servoY.write(90);

  Serial.begin(115200);
  Serial.println("++++++++++++++++++++++++++++++++++");     
  Serial.println("+ Servos motor head tracker Demo +");   
  Serial.println("+                                +");  
  Serial.println("++++++++++++++++++++++++++++++++++");  
}

void loop() {
  // 检查是否有数据可读
  while (Serial.available() > 0) {
    char c = Serial.read();  // 读取一个字节
    inputString += c;  // 将字符添加到字符串
    if (c == '\n') {  // 如果读取到换行符，停止读取
      int tabPos = inputString.indexOf('\t');  // 查找制表符位置
      if (tabPos != -1) {
        String angleXStr = inputString.substring(0, tabPos);  // 获取第一个角度值字符串
        String angleYStr = inputString.substring(tabPos + 1);  // 获取第二个角度值字符串
        angleX = angleXStr.toInt();  // 尝试将第一个角度值字符串转换为整数
        angleY = angleYStr.toInt();  // 尝试将第二个角度值字符串转换为整数

        if (angleX != 0 || angleXStr == "0") {  // 检查第一个角度值转换是否成功
          Serial.print("Received angleX: ");
          Serial.println(angleX);
          servoX.write(180-angleX);  // 写入角度到X轴舵机
        } else {
          Serial.println("Invalid input for angleX, using last known good value.");
        }

        if (angleY != 0 || angleYStr == "0") {  // 检查第二个角度值转换是否成功
          Serial.print("Received angleY: ");
          Serial.println(angleY);
          servoY.write(angleY);  // 写入角度到Y轴舵机
        } else {
          Serial.println("Invalid input for angleY, using last known good value.");
        }

        inputString = "";  // 清空字符串以备下次读取
      }
    }
  }

  delay(5);
}