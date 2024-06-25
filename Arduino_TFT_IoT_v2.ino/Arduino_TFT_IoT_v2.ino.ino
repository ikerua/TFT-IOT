#include "DFRobot_WiFi_IoT_Module.h"
#include <Arduino.h>
#include <SoftwareSerial.h>
#include "DFRobot_BME280.h"
#include <ArduinoJson.h>
#define SEA_LEVEL_PRESSURE    1015.0f
//UART mode
//Use software serialport RX：10，TX：11
SoftwareSerial    mySerial(10, 11);
DFRobot_WiFi_IoT_Module_UART IoT (&mySerial);


typedef DFRobot_BME280_IIC    BME;    // ******** use abbreviations instead of full names ********

BME   bme(&Wire, 0x77);   // select TwoWire peripheral and set sensor address
//Configure WiFi
char * WIFI_SSID= "MiFibra-2A9D";  //WiFi Name 
char * WIFI_PASS="UQpXQH9X";  //WiFi Password

//Configure Thingspeak
char * ADDRESS= "http://52.72.84.66:8000/";   //ADDRESS

float temperatura;
float altitud;
float humedad;
int monoxido_de_carbono;
int luz;
int presion;


/*******************************************************
Function:     getAmbient
Description:  Get light sensor value 
Params:
Return:       current light value 
******************************************************/
int getAmbient()
{
  int val;
  val = analogRead(A1);
  return val;
}
int get_CO_concentration()
{
  int val;
  val = analogRead(A0);
  return val;
}

// show last sensor operate status
void printLastOperateStatus(BME::eStatus_t eStatus)
{
  switch(eStatus) {
  case BME::eStatusOK:    Serial.println("everything ok"); break;
  case BME::eStatusErr:   Serial.println("unknow error"); break;
  case BME::eStatusErrDeviceNotDetected:    Serial.println("device not detected"); break;
  case BME::eStatusErrParameter:    Serial.println("parameter error"); break;
  default: Serial.println("unknow status"); break;
  }
}
void setup() {
  //Use software serialport 9600 as communication port
  mySerial.begin(9600);

  //Use serialport 115200 as print port 
  Serial.begin(115200);
  delay(100);

  //Init communication port 
  while(IoT.begin() != 0){  
    Serial.println("init ERROR!!!!");
    delay(100);
  }
  Serial.println("init Success");

  
  //Connect to WiFi
  while(IoT.connectWifi(WIFI_SSID, WIFI_PASS) != 0){  
    Serial.print(".");
    delay(100);
  }
  Serial.println("Wifi Connect Success");

  while(IoT.HTTPBegin(ADDRESS) != 0){
    Serial.println("Parameter is empty!");
    delay(100);
  }
  Serial.println("HTTP Configuration Success");

}

void loop() {
  char postRequest[100];
  char temperatura_str[8];
  char altitud_str[8];
  char humedad_str[8];
  
  temperatura= bme.getTemperature();
  presion= bme.getPressure();
  altitud= bme.calAltitude(SEA_LEVEL_PRESSURE, presion);
  humedad= bme.getHumidity();
  monoxido_de_carbono = get_CO_concentration();
  luz= getAmbient();

// Convertir los valores de punto flotante a cadenas de caractere

  dtostrf(bme.getTemperature(), 2, 2, temperatura_str); // Formato "%.2f" con 6 caracteres en total
  dtostrf(bme.calAltitude(SEA_LEVEL_PRESSURE, presion), 5, 2, altitud_str);
  dtostrf(bme.getHumidity(), 2, 2, humedad_str);

  Serial.println();
  Serial.println("======== start print ========");
  Serial.print("temperature (unit Celsius): "); Serial.println(temperatura_str);
  Serial.print("pressure (unit pa):         "); Serial.println(presion);
  Serial.print("altitude (unit meter):      "); Serial.println(altitud_str);
  Serial.print("humidity (unit percent):    "); Serial.println(humedad_str);
  Serial.print("CO (Parts per Million):     "); Serial.println(monoxido_de_carbono);
  Serial.print("LUZ:                        "); Serial.println(luz);
  Serial.println("========  end print  ========");

  


  // Buffer para la solicitud completa
  snprintf(postRequest, sizeof(postRequest),"{\"temperatura\":%s,\"presion\":%f,\"altitud\":%s,\"humedad\":%s,\"monoxido_de_carbono\":%d,\"luz\":%d}",temperatura_str, presion, altitud_str, humedad_str, monoxido_de_carbono, luz);
  Serial.println(postRequest);

  //Upload current ambient light data to ThingSpeak every 1s

  Serial.print("Posting data: ");
  Serial.println(postRequest);

  delay(1000);
  char url[] = "insertData/";

  String statusCode = IoT.HTTPPost(url, postRequest);
  Serial.print("HTTP Response code: ");
  Serial.println(statusCode);

  // Wait before sending next request
  delay(14000);
}