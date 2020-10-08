#include <Servo.h>

int c_x = 90;
int c_y = 90;
Servo pan;
Servo tilt;


void setup() {
  pan.attach(10);
  tilt.attach(9);
  Serial.begin(9600);
  pan.write(c_x);
  tilt.write(c_y);
  pinMode(2, OUTPUT);
  digitalWrite(2,HIGH);
}

void loop()
{
   if(Serial.available() > 0)
   {
    String input = Serial.readString();

    if(input.length() <= 10)
    {
      int x = 0;
      int y = 0;

      int i = 0;
      int j = 0;

      while(i < input.length() && input[i] != ';')
      {
        if(input[i] == ',')
        {
          x = input.substring(0, i).toInt();
          j = i+1;
        }
        i++;
      }
      y = input.substring(j, i).toInt();

      if(x == 181 && y == 181)
      {
        c_x = 90;
        c_y = 90;
        pan.write(90);
        tilt.write(90);
      }else
      {
        c_x -= x;
        c_y -= y;
        pan.write(c_x);
        tilt.write(c_y);
        digitalWrite(2,LOW);
        delay(750);
        digitalWrite(2,HIGH);
      }
    }
    Serial.flush();
   }
}