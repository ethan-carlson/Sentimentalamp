
int num_input;

#include <Adafruit_NeoPixel.h>
#include <Wire.h>

#define PIN 13
#define blue 25
#define pixels 16

Adafruit_NeoPixel strip = Adafruit_NeoPixel(pixels, PIN, NEO_GRB + NEO_KHZ800);

void setup() {  
  Serial.begin(9600); 
  strip.begin();
  clearStrip();
  introSequence();
  clearStrip();
  while (!Serial) {
    ;  
  }  
}  
  
void loop() {
  int neg_bright, pos_bright;
   
  while(!Serial.available()){}
  if(Serial.available() > 0) {
    num_input = Serial.parseInt();
  }
  Serial.print("Positive Percentage: ");
  Serial.print(num_input);
  Serial.println(".");

  pos_bright = num_input;
  
  while(!Serial.available()){}
  if(Serial.available() > 0) {
    num_input = Serial.parseInt();
  }
  Serial.print("Negative Percentage: ");
  Serial.print(num_input);
  Serial.println(".");

  neg_bright = num_input;

  clearStrip();
  for(int i=0;i < pixels;i++){
    strip.setPixelColor(i,neg_bright*3,pos_bright*3,blue);
  }
  strip.show();
} 

void clearStrip(){    //Set all LEDs off
  for(int i=0;i < pixels;i++){
    strip.setPixelColor(i,0);
  }
  strip.show();
}

void introSequence(){
  for(int i=0;i<150;i++){
    for(int j=0;j<pixels;j++){
    strip.setPixelColor(j,i,(150-i),blue);
    }
    strip.show();
    delay(15);
  }
  for(int i=0;i<150;i++){
    for(int j=0;j<pixels;j++){
    strip.setPixelColor(j,(150-i),i,blue);
    }
    strip.show();
    delay(15);
  }
}
