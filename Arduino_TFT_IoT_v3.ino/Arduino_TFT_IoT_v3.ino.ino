#include "DFRobot_WiFi_IoT_Module.h"
    #include <SoftwareSerial.h>
    #include <ArduinoJson.h>
    #include "DFRobot_BME280.h"

    //UART mode
    //Use software serialport RX：10，TX：11
    SoftwareSerial    mySerial(10, 11);
    DFRobot_WiFi_IoT_Module_UART IoT (&mySerial);

    // ******** use abbreviations instead of full names ********
    //typedef DFRobot_BME280_IIC    BME;    
    // select TwoWire peripheral and set sensor address
    //BME   bme(&Wire, 0x77);   

    //Configure WiFi
    const char *WIFI_SSID             = "MiFibra-2A9D";   //WiFi Name 
    const char *WIFI_PASSWORD         = "UQpXQH9X";  //WiFi Password

    //Configure Thingspeak
    const char *SERVER_ADDRESS    = "52.72.84.66:8000";   //ThingSpeak address, not revise here 
     const char *ThingSpeak_ADDRESS    = "api.thingspeak.com";   //ThingSpeak address, not revise here 
    const char *THINGSPEAK_KEY    = "4I1G5SXC5PGU3HA4";  //Fill in the created event password on ThingSpeak  

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
/*void printLastOperateStatus(BME::eStatus_t eStatus)
{
  switch(eStatus) {
  case BME::eStatusOK:    Serial.println("everything ok"); break;
  case BME::eStatusErr:   Serial.println("unknow error"); break;
  case BME::eStatusErrDeviceNotDetected:    Serial.println("device not detected"); break;
  case BME::eStatusErrParameter:    Serial.println("parameter error"); break;
  default: Serial.println("unknow status"); break;
  }
}*/


    void setup() {
      //Use software serialport 9600 as communication port
      mySerial.begin(9600);

      //Use serialport 115200 as print port 
      Serial.begin(115200);

      //Init communication port 
      while(IoT.begin() != 0){  
        Serial.println("init ERROR!!!!");
        delay(100);
      }
      Serial.println("init Success");

      //Connect to WiFi
      while(IoT.connectWifi(WIFI_SSID, WIFI_PASSWORD) != 0){  
        Serial.print(".");
        delay(100);
      }
      Serial.println("Wifi Connect Success");

      while(IoT.HTTPBegin(SERVER_ADDRESS) != 0){
        Serial.println("Parameter is empty!");
        delay(100);
      }
      Serial.println("HTTP Configuration Success");

      /*while(IoT.thingSpeakBegin(THINGSPEAK_KEY) != 0){
        Serial.print("Parameter is empty!");
        delay(100);
      }
      Serial.println("ThingSpeak Configuration Success");*/
    }

    void loop() {

      Serial.println("bme begin success");
      char postRequest[100];
       snprintf(postRequest, sizeof(postRequest),"{\"monoxido_de_carbono\":%d,\"luz\":%d}", get_CO_concentration(),  getAmbient());

    //Upload current ambient light data to ThingSpeak every 1s
      IoT.HTTPPost("insertData/",postRequest);  
      delay(10000);
    }