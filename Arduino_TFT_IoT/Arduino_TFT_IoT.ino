
#include <Arduino.h>
#include <SoftwareSerial.h>
#include "DFRobot_BME280.h"
#include "Wire.h"

typedef DFRobot_BME280_IIC    BME;    // ******** use abbreviations instead of full names ********

BME   bme(&Wire, 0x77);   // select TwoWire peripheral and set sensor address

#define SEA_LEVEL_PRESSURE    1015.0f
//Initialize OBLOQ
//Obloq olq(&softSerial, "SeiferNet", "7106230000", "iot_s1.dfrobot.com","1883", "HJ-LCn_HS7", "HJzUCnurSm");

//wifi SSID and password
#define WIFISSID "MiFibra-2A9D"
#define WIFIPWD  "UQpXQH9X"

//Azure IOT device connection string, this string need modification when connect to different devices
const String connectionString = "HostName=dfrobot.azure-devices.cn;DeviceId=temperature;SharedAccessKey=CR5gUclNaT7skX9WP+e6oIB/BnkZnTIEReKBX870SNY=";
const String separator = "|";
bool pingOn = true;
bool createIoTClientSuccess = false;

static unsigned long previoustGetTempTime = 0;
static unsigned long pingInterval = 2000;
static unsigned long sendMessageInterval = 10000;
unsigned long previousPingTime = 0;
String receiveStringIndex[10] = {};

//Disconnected wifi detection variable
bool wifiConnect = false;
bool wifiAbnormalDisconnect = false;

SoftwareSerial softSerial(10,11);

enum state{
    WAIT,
    PINGOK,
    WIFIOK,
    AZURECONNECT
}obloqState;

/********************************************************************************************
Function    : sendMessage
Description : send message via serial port
Params      : message : message content, it is a string
Return      : None
********************************************************************************************/
void sendMessage(String message)
{
    softSerial.print(message+"\r");
}

/********************************************************************************************
Function    : ping
Description : Check if the serial communication is normal. When Obloq serial port receives the pingcommand, it will return: |1|1|\r
Return      : None
********************************************************************************************/
void ping()
{
    String pingMessage = F("|1|1|");
    sendMessage(pingMessage);
}

/********************************************************************************************
Function    : connectWifi
Description : Connect wifi, once successfully connected Obloq returns: |2|3|ip|\r
Params      : ssid : wifi SSID
Params      : pwd :  wifi password
Return      : None
********************************************************************************************/
void connectWifi(String ssid,String pwd)
{
    String wifiMessage = "|2|1|" + ssid + "," + pwd + separator;
    sendMessage(wifiMessage);
}

/********************************************************************************************
Function    : createIoTClient
Description : Create device client handle, once successfully created Obloq returns: |4|2|1|1|\r
Params      : connecttionString  device connection string
Return      : None
********************************************************************************************/
void createIoTClient(String connecttionString)
{
    String azureConnectMessage = "|4|2|1|" + connecttionString + separator;
    sendMessage(azureConnectMessage);
}

/********************************************************************************************
Function    : subscribeDevice
Description : Subscribe to device. Obloq returns message content after the device receives message.
Params      : None
Return      : None
********************************************************************************************/
void subscribeDevice()
{
    String subscribeDeviceMessage = "|4|2|2|";
    sendMessage(subscribeDeviceMessage);
}

/********************************************************************************************
Function    : unsubscribeDevice
Description : Unsubscribe to device. Once successfully unsubscribed, Obloq returns: |4|2|6|1|\r
Params      : None
Return      : None
********************************************************************************************/
void unsubscribeDevice()
{
    String unsubscribeDeviceMessage = "|4|2|6|";
    sendMessage(unsubscribeDeviceMessage);
}


/********************************************************************************************
Function    : publish
Description : Publish message. Before this command you must create device client handle first.
Params      : message: message content to publish, once successfully sent, OBloq returns :  |4|2|3|1|\r
Return      : None
********************************************************************************************/
void publish(String message)
{
    String publishMessage = "|4|2|3|" + message + separator;
    sendMessage(publishMessage);
}

/********************************************************************************************
Function    : disconnect
Description : destroy device client handle: |4|2|4|1|\r
Params      : None
Return      : None
********************************************************************************************/
void distoryIotClient()
{
    String distoryIotClientMessage = "|4|2|4|";
    sendMessage(distoryIotClientMessage);
}

/********************************************************************************************
Function    : recreateIoTClient
Description : Recreate device client handle, once created successfully, Obloq returns : |4|2|1|1|\r
Params      : None
Return      : None
********************************************************************************************/
void recreateIoTClient()
{
    String recreateIoTClientMessage = "|4|2|5|";
    sendMessage(recreateIoTClientMessage);
}

/********************************************************************************************
Function    : splitString
Description : split a string
Params      : data:  save the cutted char array
Params      : str: the string that will be cutted
Params      : delimiters: the delimiter that cut string
Return      : None
********************************************************************************************/
int splitString(String data[],String str,const char* delimiters)
{
  char *s = (char *)(str.c_str());
  int count = 0;
  data[count] = strtok(s, delimiters);
  while(data[count]){
    data[++count] = strtok(NULL, delimiters);
  }
  return count;
}

/********************************************************************************************
Function    : handleUart
Description : handle data received by serial port
Params      : None
Return      : None
********************************************************************************************/
void handleUart()
{
    while(softSerial.available() > 0)
    {
        String receivedata = softSerial.readStringUntil('\r');
        const char* obloqMessage = receivedata.c_str();
        if(strcmp(obloqMessage, "|1|1|") == 0)
        {
            Serial.println("Pong");
            pingOn = false;
            obloqState = PINGOK;
        }
        if(strcmp(obloqMessage, "|2|1|") == 0)
        {
            if(wifiConnect)
            {
                wifiConnect = false;
                wifiAbnormalDisconnect = true;
            }
        }
        else if(strstr(obloqMessage, "|2|3|") != 0 && strlen(obloqMessage) != 9)
        {
            Serial.println("Wifi ready");
            wifiConnect = true;
            if(wifiAbnormalDisconnect)
            {
                wifiAbnormalDisconnect = false;
                createIoTClientSuccess = true;
                return;
            }
            obloqState = WIFIOK;
        }
        else if(strcmp(obloqMessage, "|4|2|1|1|") == 0)
        {
            Serial.println("Azure ready");
            createIoTClientSuccess = true;
            obloqState = AZURECONNECT;
        }
    }
}

/********************************************************************************************
Function    : sendPing
Description : Check if serial port is communicating normally
Params      : None
Return      : None
********************************************************************************************/
void sendPing()
{
    if(pingOn && millis() - previousPingTime > pingInterval)
    {
        previousPingTime = millis();
        ping();
    }
}

/********************************************************************************************
Function    : execute
Description : send different command according to different status.
Params      : None
Return      : None
********************************************************************************************/
void execute()
{
    Serial.print(obloqState);
    switch(obloqState)
    {
        case PINGOK: connectWifi(WIFISSID,WIFIPWD); obloqState = WAIT; break;
        case WIFIOK: createIoTClient(connectionString);obloqState = WAIT; break;
        case AZURECONNECT : obloqState = WAIT; break;
        default: break;
    }
}

/********************************************************************************************
Function    : getTemp
Description : Get Carbon Monoxide measured by MQ7
Params      : None
Return      : None
********************************************************************************************/
float getCarbonMonoxide()
{
    uint16_t val;
    float dat;
    val=analogRead(A0);//Connect LM35 on Analog 0
    
    Serial.print(val);
    Serial.print("\n");
    
    dat = (float) val;
    return dat;
}

float getLight()
{
    uint16_t val;
    float dat;
    val=analogRead(A1);//Connect LM35 on Analog 0

    Serial.print(val);
    Serial.print("\n");
    
    dat = (float) val;
    return dat;
}

/********************************************************************************************
Function    : checkWifiState
Description : Callback function of receiving message
Params      : message: message content string that received
Return      : None
********************************************************************************************/
void checkWifiState()
{
    static unsigned long previousTime = 0;
    if(wifiAbnormalDisconnect && millis() - previousTime > 60000)  // reconnect once per minute after wifi abnormally disconnect
    {
        previousTime = millis();
        createIoTClientSuccess = false;
        connectWifi(WIFISSID,WIFIPWD);
    }
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
void setup()
{
    Serial.begin(9600);
    softSerial.begin(9600);
    bme.reset();
    while(bme.begin() != BME::eStatusOK) {
      Serial.println("bme begin faild");
      printLastOperateStatus(bme.lastOperateStatus);
      delay(2000);
    }
    Serial.println("bme begin success");
    delay(100);

}

void loop()
{
    sendPing();
    execute();
    handleUart();
    checkWifiState();
    // Espera de 5 segundos
    delay(5000);
    //EN CASO DE QUE LA CONEXIÓN SE HAYA REALIZADO CORRECTAMENTE LEEMOS 
    if(true){
      
      float   temp = bme.getTemperature();
      uint32_t    press = bme.getPressure();
      float   alti = bme.calAltitude(SEA_LEVEL_PRESSURE, press);
      float   humi = bme.getHumidity();

      Serial.println();
      Serial.println("======== start print ========");
      Serial.print("temperature (unit Celsius): "); Serial.println(temp);
      Serial.print("pressure (unit pa):         "); Serial.println(press);
      Serial.print("altitude (unit meter):      "); Serial.println(alti);
      Serial.print("humidity (unit percent):    "); Serial.println(humi);
      Serial.print("MONOXIDO DE CARBONO: "); Serial.println(getCarbonMonoxide());
      Serial.print("LUZ: "); Serial.println(getLight());
      Serial.println("========  end print  ========");
      
    }else{
      Serial.print("HA HABIDO UN ERROR A LA HORA DE REALIZAR LA PETICIÓN \n");
    }
}