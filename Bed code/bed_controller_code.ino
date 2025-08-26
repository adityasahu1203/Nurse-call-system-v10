#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <EEPROM.h>
#include <FS.h>
/************************************************************
 * Virtual I²C over RS-485 (vI2C) Patch for ESP8266 Bed Controller
 * File: Nurse_call_system_production_R9_V1_0.ino
 * 
 * Adds: frame parser, CRC16, register map
 * Keeps: existing logic for CALL, CODE BLUE, RESET, LEDs, RELAY
 ************************************************************/

// ==== RS485 DE/RE pin (choose a free GPIO; check schematic) ====
#define RS485_DE  15   // Example: GPIO15 (D8) tied to MAX485 DE/RE

// ==== Device address (unique per bed, stored in EEPROM if needed) ====
uint8_t my_addr = 5;  // Example address; load from EEPROM in setup()

// ==== vI2C Command codes ====
#define CMD_WRITE_REG   0x10
#define CMD_READ_REG    0x11
#define CMD_ACK         0x12
#define CMD_RESP_DATA   0x13

// ==== Register map values (example) ====
bool call = false;
bool codeblue = false;
bool nurseComing = false;
uint8_t ledCmd = 0;

// CRC16 (IBM)
uint16_t crc16(const uint8_t *data, size_t len) {
  uint16_t crc = 0x0000;
  for (size_t i = 0; i < len; i++) {
    crc ^= (uint16_t)data[i];
    for (uint8_t j = 0; j < 8; j++) {
      if (crc & 1) crc = (crc >> 1) ^ 0xA001;
      else crc >>= 1;
    }
  }
  return crc;
}

// Enable TX
void rs485_txEnable() {
  digitalWrite(RS485_DE, HIGH);
  delayMicroseconds(10);
}
// Enable RX
void rs485_rxEnable() {
  delayMicroseconds(10);
  digitalWrite(RS485_DE, LOW);
}

// Send frame
void sendFrame(uint8_t addr, uint8_t cmd, const uint8_t *payload, uint8_t len) {
  uint8_t header[4] = {0x01, addr, cmd, len};
  uint16_t crc = crc16(payload, len);

  rs485_txEnable();
  Serial.write(header, 4);
  if (len > 0) Serial.write(payload, len);
  Serial.write((uint8_t*)&crc, 2);   // little-endian
  Serial.write(0x04);
  Serial.flush();
  rs485_rxEnable();
}

// Read frame (blocking with timeout)
bool readFrame(uint8_t &addr, uint8_t &cmd, uint8_t *payload, uint8_t &len, uint16_t timeout=200) {
  uint32_t start = millis();
  while (millis() - start < timeout) {
    if (Serial.available() && Serial.peek() == 0x01) {
      break;
    }
  }
  if (!Serial.available()) return false;

  if (Serial.read() != 0x01) return false; // SOH
  addr = Serial.read();
  cmd = Serial.read();
  len = Serial.read();
  for (uint8_t i = 0; i < len; i++) {
    while (!Serial.available());
    payload[i] = Serial.read();
  }
  uint8_t crclo = Serial.read();
  uint8_t crchi = Serial.read();
  uint8_t eot   = Serial.read();
  if (eot != 0x04) return false;
  uint16_t crc = (uint16_t)crchi << 8 | crclo;
  if (crc != crc16(payload, len)) return false;
  return true;
}

// Handle register read
uint8_t handleReadRegister(uint8_t reg, uint8_t *out) {
  switch (reg) {
    case 0x01: // STATUS
      out[0] = (call ? 0x01 : 0) | (codeblue ? 0x02 : 0) | (nurseComing ? 0x04 : 0);
      return 1;
    case 0x02: // CALL_TYPE
      out[0] = codeblue ? 2 : (call ? 1 : 0);
      return 1;
    case 0x03: // LED_CMD
      out[0] = ledCmd;
      return 1;
    case 0x06: // FIRMWARE_VER
      out[0] = 'R'; out[1] = '9'; out[2] = 'V'; out[3] = '1';
      return 4;
    default:
      out[0] = 0x00;
      return 1;
  }
}

// Handle register write
void handleWriteRegister(uint8_t reg, uint8_t *data, uint8_t dlen) {
  switch (reg) {
    case 0x03: // LED_CMD
      if (dlen >= 1) {
        ledCmd = data[0];
        // Apply to actual LEDs
        if (ledCmd & 0x01) digitalWrite(CB_LED, HIGH); else digitalWrite(CB_LED, LOW);
        if (ledCmd & 0x02) digitalWrite(CW_LED, HIGH); else digitalWrite(CW_LED, LOW);
      }
      break;
    case 0x04: // ACK
      if (dlen >= 1 && data[0] == 1) {
        call = false;
        codeblue = false;
        nurseComing = true;  // example behavior
      }
      break;
    default:
      break;
  }
}

// Parse incoming frames
void parseFrameFromMaster() {
  uint8_t addr, cmd, len;
  uint8_t payload[64];
  if (!readFrame(addr, cmd, payload, len, 50)) return;
  if (addr != my_addr) return; // not for me

  if (cmd == CMD_READ_REG) {
    uint8_t reg = payload[0];
    uint8_t n   = payload[1];
    uint8_t rdata[16];
    uint8_t rlen = handleReadRegister(reg, rdata);
    sendFrame(my_addr, CMD_RESP_DATA, rdata, rlen);
  } else if (cmd == CMD_WRITE_REG) {
    uint8_t reg = payload[0];
    handleWriteRegister(reg, &payload[1], len - 1);
    uint8_t ack = 1;
    sendFrame(my_addr, CMD_ACK, &ack, 1);
  }
}

// ==== Arduino setup & loop ====
void setup() {
  pinMode(RS485_DE, OUTPUT);
  rs485_rxEnable();
  Serial.begin(115200);

  // Setup GPIOs for LEDs/Relay as in original code
  pinMode(RELAY, OUTPUT);
  pinMode(CB_LED, OUTPUT);
  pinMode(CW_LED, OUTPUT);
  digitalWrite(RELAY, LOW);
}

void loop() {
  // Existing button handling (call, codeblue, reset) …
  // Update 'call' and 'codeblue' flags accordingly

  // Poll RS485 bus for commands
  parseFrameFromMaster();
}



#define D0 16
#define D1 5
#define D2 4
#define D3 0
#define D4 2
#define D5 14
#define D6 12
#define D7 13
#define D8 15

#define RELAY D2
#define RING_TONE_GND D1
#define CALL_SW D3
#define RESET_SW D0
#define CB_SW D4
#define CB_LED D5
#define PWM D6
#define CW_LED D7

#define EEPROM_SIZE 16  // Size of EEPROM for initialization, adjust as needed
#define selfAddressAddress 0x00
#define BRAddress 0x05
#define yledAddress 0x08
#define bledAddress 0x09
#define callAddress 0x0A
#define codeblueAddress 0x0B
#define yblinkAddress 0x0C
#define bblinkAddress 0x0D
#define dataptrAddress 0x0E

#define EEPROM_SIZE 512
#define SELF_ADDRESS_ADDRESS 0
#define LOCAL_IP_ADDRESS 20
#define SERVER_IP_ADDRESS 40
#define MAX_STRING_LENGTH 16

byte selfAddress = 0;
String local_ip = "192.168.1.100";
String server_ip = "192.168.1.1";

volatile bool waitForCommand = false;
volatile bool waitForAck = false;
volatile int trycount = 0;
volatile char receive;
int dataArrayPointer = 0;

bool nurseComing = false;
bool blueComing = false;
bool call = false;
bool codeblue = false;
bool yblink = false;
bool bblink = false;
bool Save = false;
//byte selfAddress;
char dataArray[3] = { '\0', '\0', '\0' };
bool yled = false;
bool bled = false;
bool yled1 = false;
bool bled1 = false;
bool yblink1 = false;
bool bblink1 = false;

unsigned long previousMillisCB = 0;
unsigned long previousMillisCW = 0;
const long interval = 500;  // Interval for blinking LEDs (milliseconds)
int counter=0;
int discon=60;
unsigned long curMil, preMil;
int intervalTime=1000;
int inactivityTime=180;

// Define static IP address and network settings
const char* ssid = "INCMS-R9 BED ";
const char* password = "INCMS-R9";
IPAddress staticIP(192, 168, 1, 254);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

ESP8266WebServer server(80);  // Create a web server object that listens on port 80

void setup() {
  
  
  Serial.begin(9600);

  EEPROM.begin(EEPROM_SIZE);
  delay(3000);
  // Initialize EEPROM with default data if it's not already initialized
  selfAddress = EEPROM.read(selfAddressAddress);
   Serial.println("EEPROM values loaded1:");
    Serial.print("selfAddress: "); Serial.println(selfAddress);
    
  if (selfAddress == 0x00) {
    initializeEEPROM();
    resetFlags();
  } else {
    // Initialize EEPROM values
    selfAddress = EEPROM.read(selfAddressAddress);
    yled = EEPROM.read(yledAddress);
    bled = EEPROM.read(bledAddress);
    call = EEPROM.read(callAddress);
    if(call){
      dataArray[0] = 'C';
    }
    codeblue = EEPROM.read(codeblueAddress);
    if(codeblue){
      dataArray[1] = 'B';
    }
    yblink = EEPROM.read(yblinkAddress);
    bblink = EEPROM.read(bblinkAddress);
    dataArrayPointer = EEPROM.read(dataptrAddress);

    /*
    Serial.println("EEPROM values loaded:");
    Serial.print("selfAddress: "); Serial.println(selfAddress);
    Serial.print("yled: "); Serial.println(yled);
    Serial.print("bled: "); Serial.println(bled);
    Serial.print("call: "); Serial.println(call);
    Serial.print("codeblue: "); Serial.println(codeblue);
    Serial.print("yblink: "); Serial.println(yblink);
    Serial.print("bblink: "); Serial.println(bblink);
    Serial.print("dataArrayPointer: "); Serial.println(dataArrayPointer);
    */
    selfAddress = EEPROM.read(SELF_ADDRESS_ADDRESS);
    local_ip = readStringFromEEPROM(LOCAL_IP_ADDRESS);
    server_ip = readStringFromEEPROM(SERVER_IP_ADDRESS);

  }

  // Initialize GPIO
  pinMode(RELAY, OUTPUT);
  pinMode(RING_TONE_GND, OUTPUT);
  pinMode(CALL_SW, INPUT);
  pinMode(RESET_SW, INPUT);
  pinMode(CB_SW, INPUT);
  pinMode(CB_LED, OUTPUT);
  pinMode(PWM, OUTPUT);
  pinMode(CW_LED, OUTPUT);

  // Set initial states for LEDs
  digitalWrite(CB_LED, bled ? HIGH : LOW);
  digitalWrite(CW_LED, yled ? HIGH : LOW);

}

void loop() {
  // Handle serial input
  if(digitalRead(RESET_SW) == LOW && digitalRead(CB_SW) == LOW){
    counter++;
    //Serial.print("counter: "); Serial.println(counter);
    if(counter>100 && yblink1==0 && yblink1==0){
      
      yblink1=1;
      bblink1=1;
      wifiHotspot();
    }
  }else if(counter>100 && yblink1==1 && yblink1==1){
    
    
    server.handleClient();  // Handle incoming client requests

  }else{
    counter=0;
    yblink1=0;
    bblink1=0;
  }
  
  curMil=millis();
  if (curMil - preMil >= intervalTime) {
      preMil = curMil;
      
      if(counter<100){
        if(discon>0)discon--;
        else{
          
          //Serial.print("discon: "); Serial.println(discon);
          yled1=1;
          bled1=1;
        
        }

      }else{
        if(inactivityTime>0){
          inactivityTime--;
        }else{
          ESP.restart();

        }
        
      }
      
  }
  if (Serial.available()) {
    receive = Serial.read();

    if (receive == selfAddress) {
      waitForCommand = true;
    } else if (waitForCommand && receive >= 124 && receive <= 127) {
      waitForCommand = false;

      if (receive == 127) {
        delay(12);
        Uart_send_char(selfAddress);
        discon=60;
        yled1=0;
        bled1=0;

        if (dataArray[dataArrayPointer] == '\0') {
          Uart_send_char('L');
        } else {
          Uart_send_char(dataArray[dataArrayPointer]);
          waitForAck = true;
          trycount++;
          if (trycount > 5) {
            resetFlags();
            Save = true;
          }
        }

      } else if (receive == 126) {
        trycount = 0;
        if ((dataArray[dataArrayPointer] == 's' || dataArray[dataArrayPointer] == 'S') && waitForAck) {
          waitForAck = false;
          resetFlags();
          Save = true;
        } else if (waitForAck) {
          waitForAck = false;
          processAck();
          Save = true;
        }

      } else if (receive == 124) {
        updateStates();
        Save = true;
      }
    } else {
      waitForCommand = false;
    }
  }
  
  // Handle switches
  handleSwitches();
  saveIfNeeded();

  // Update LED states
  if((yled1==1 && bled1==1)||(yblink1==1 && bblink1==1)){
    updateLEDs1();

  }else{
    updateLEDs();
  }
  
  
  
}

void handleSwitches() {
  if (digitalRead(CALL_SW) == LOW && dataArray[0] == '\0') {
    dataArray[0] = 'C';
  } else if (digitalRead(CB_SW) == LOW && dataArray[1] == '\0' && dataArray[0] != '\0') {
    dataArray[1] = 'B';
  } else if (digitalRead(RESET_SW) == LOW && dataArray[2] == '\0' && dataArray[0] != '\0' && dataArray[1] != 's') {
    if (dataArray[1] == 'B') dataArray[2] = 'S';
    else dataArray[1] = 's';
  }
}

void resetFlags() {
  memset(dataArray, '\0', 3);
  dataArrayPointer = 0;
  yled = false;
  bled = false;
  nurseComing = false;
  blueComing = false;
  call = false;
  codeblue = false;
  yblink = false;
  bblink = false;
  trycount = 0;
}

void processAck() {
  if (dataArray[dataArrayPointer] == 'C') {
    yled = true;
    bled = false;
    call = true;
  } else if (dataArray[dataArrayPointer] == 'B') {
    yled = false;
    bled = true;
    codeblue = true;
    nurseComing = false;
    yblink = false;
  }
  dataArrayPointer++;
}

void updateStates() {
  if (yled) {
    yled = false;
    nurseComing = true;
    bblink = false;
    yblink = true;
  } else if (bled) {
    bled = false;
    blueComing = true;
    nurseComing = false;
    bblink = true;
    yblink = false;
  }
}

void saveIfNeeded() {
  if (Save) {
    EEPROM.write(yledAddress, yled ? 1 : 0);
    EEPROM.write(bledAddress, bled ? 1 : 0);
    EEPROM.write(callAddress, call ? 1 : 0);
    EEPROM.write(codeblueAddress, codeblue ? 1 : 0);
    EEPROM.write(yblinkAddress, yblink ? 1 : 0);
    EEPROM.write(bblinkAddress, bblink ? 1 : 0);
    EEPROM.write(dataptrAddress, dataArrayPointer);
    EEPROM.commit();
    Save = false;
  }
}
void updateLEDs1() {
  unsigned long currentMillis = millis();

  if (bblink1) {
    if (currentMillis - previousMillisCB >= interval) {
      previousMillisCB = currentMillis;
      int cbLedState = digitalRead(CB_LED);
      digitalWrite(CB_LED, !cbLedState);
    }
  } else if (bled1) {
    digitalWrite(CB_LED, HIGH);
  }else {
    digitalWrite(CB_LED, LOW);
  }

   if (yblink1) {
    if (currentMillis - previousMillisCW >= interval) {
      previousMillisCW = currentMillis;
      int cwLedState = digitalRead(CW_LED);
      digitalWrite(CW_LED, !cwLedState);
    }
  } else if (yled1) {
    digitalWrite(CW_LED, HIGH);
  } else{
    digitalWrite(CW_LED, LOW);
  }
}

void updateLEDs() {
  unsigned long currentMillis = millis();

  if (bled) {
    digitalWrite(CB_LED, HIGH);
  } else if (bblink) {
    if (currentMillis - previousMillisCB >= interval) {
      previousMillisCB = currentMillis;
      int cbLedState = digitalRead(CB_LED);
      digitalWrite(CB_LED, !cbLedState);
    }
  } else {
    digitalWrite(CB_LED, LOW);
  }

  if (yled) {
    digitalWrite(CW_LED, HIGH);
  } else if (yblink) {
    if (currentMillis - previousMillisCW >= interval) {
      previousMillisCW = currentMillis;
      int cwLedState = digitalRead(CW_LED);
      digitalWrite(CW_LED, !cwLedState);
    }
  } else {
    digitalWrite(CW_LED, LOW);
  }
}

void Uart_send_char(char c) {
  Serial.write(c);
}

void initializeEEPROM() {
  // Define default EEPROM data
  byte defaultData[EEPROM_SIZE] = {
    200, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
  };

  // Check if EEPROM is already initialized
  if (EEPROM.read(0) == 0x00) {  // Check the first byte of EEPROM
    for (int i = 0; i < EEPROM_SIZE; i++) {
      EEPROM.write(i, defaultData[i]);
    }

    EEPROM.write(LOCAL_IP_ADDRESS, 0);
    EEPROM.write(SERVER_IP_ADDRESS, 0);
    EEPROM.commit();
    //Serial.println("EEPROM initialized with default data.");
  } else {
    //Serial.println("EEPROM already initialized.");
  }
}
void wifiHotspot(){
  

  // Dynamically set SSID using self address
  String ssidLocal = ssid + String(selfAddress);

  // Set up WiFi as an access point
  WiFi.softAP(ssidLocal.c_str(), password);
  WiFi.softAPConfig(staticIP, gateway, subnet);

  // Define routes for handling web requests
  server.on("/", HTTP_GET, handleRoot);
  server.on("/set", HTTP_GET, handleSet);
  server.on("/save", HTTP_GET, handleSave);
  server.serveStatic("/logo.png", SPIFFS, "/logo.png");
  server.begin();
  yled1=1;bled1=1;
}
void handleRoot() {
  // Prepare the status message from query parameters
  String statusMessage = server.hasArg("msg") ? server.arg("msg") : "";

  // Generate HTML content for the configuration page with improved design
  String html = "<html><head><style>"
                "body { font-family: Arial, sans-serif; text-align: center; background-color: #f4f4f4; }"
                "form { margin: 20px auto; padding: 20px; border-radius: 10px; background-color: #fff; box-shadow: 0 0 10px rgba(0,0,0,0.1); width: 80%; max-width: 500px; }"
                "label { display: block; margin: 10px 0 5px; text-align: left; font-weight: bold; color: #333; }"
                "input[type='text'] { width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ccc; border-radius: 5px; }"
                ".bed-address { background-color: #e7f1ff; padding: 15px; border-radius: 5px; margin-bottom: 15px; }"
                ".local-ip { background-color: #fffbe7; padding: 15px; border-radius: 5px; margin-bottom: 15px; }"
                ".server-ip { background-color: #e7ffe7; padding: 15px; border-radius: 5px; margin-bottom: 15px; }"
                "input[type='submit'] { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }"
                ".submit-button { background-color: #28a745; color: white; }"  /* Green color for Submit button */
                ".submit-button:hover { background-color: #218838; }"         /* Darker green on hover */
                ".quit-button { background-color: #dc3545; color: white; margin-left: 10px; }"  /* Red color for Quit button */
                ".quit-button:hover { background-color: #c82333; }"           /* Darker red on hover */
                "p { color: green; font-weight: bold; }"
                "img { max-width: 150px; margin: 20px auto; display: block; }"
                "h2 { background-color: #007BFF; color: white; padding: 10px; border-radius: 5px; }"
                "h4 { background-color: #0056b3; color: white; padding: 8px; border-radius: 5px; }"
                "</style></head><body>";
  html += "<h2>Manmind Automation Systems Private Limited</h2>";
  html += "<h4>Intelligent Nurse Call Monitoring System(INCMS-R9)</h4>";
  html += "<h4>BED Configuration</h4>";
  html += "<form action=\"/set\" method=\"GET\">";
  
  // BED Address Section
  html += "<div class=\"bed-address\">";
  html += "<label for=\"selfAddress\">BED ADDRESS:</label>";
  html += "<input type=\"text\" id=\"selfAddress\" name=\"selfAddress\" value=\"" + String(selfAddress) + "\"><br>";
  html += "</div>";
  
  // Local IP Section
  html += "<div class=\"local-ip\">";
  html += "<label for=\"localIP\">LOCAL  IP :</label>";
  html += "<input type=\"text\" id=\"localIP\" name=\"localIP\" value=\"" + local_ip + "\"><br>";
  html += "</div>";
  
  // Server IP Section
  html += "<div class=\"server-ip\">";
  html += "<label for=\"serverIP\">SERVER IP :</label>";
  html += "<input type=\"text\" id=\"serverIP\" name=\"serverIP\" value=\"" + server_ip + "\"><br>";
  html += "</div>";
  
  // Submit and Quit buttons
  html += "<input type=\"submit\" value=\"Submit\" class=\"submit-button\">";
  
 // html += "</form>";  // Close the first form

  html += "<form action=\"/save\" method=\"GET\" style=\"display:inline;\">";
  html += "<input type=\"submit\" value=\"Quit\" class=\"quit-button\">";
  html += "</form>";

  // Show status message
  if (statusMessage.length() > 0) {
    html += "<p>" + statusMessage + "</p>";
  }

  html += "</body></html>";
  server.send(200, "text/html", html);
  inactivityTime=120;
}

void handleSet() {
  bool updated = false;

  if (server.hasArg("selfAddress")) {
    selfAddress = server.arg("selfAddress").toInt();
    EEPROM.write(SELF_ADDRESS_ADDRESS, selfAddress);
    updated = true;
  }
  if (server.hasArg("localIP")) {
    local_ip = server.arg("localIP");
    writeStringToEEPROM(LOCAL_IP_ADDRESS, local_ip);
    updated = true;
  }
  if (server.hasArg("serverIP")) {
    server_ip = server.arg("serverIP");
    writeStringToEEPROM(SERVER_IP_ADDRESS, server_ip);
    updated = true;
  }

  EEPROM.commit();

  String msg;
  if (updated) {
    msg = "Configuration updated successfully!<br>";
    msg += "BED ADDRESS: " + String(selfAddress) + "<br>";
    msg += "LOCAL IP: " + local_ip + "<br>";
    msg += "SERVER IP: " + server_ip;
  } else {
    msg = "No changes detected.";
  }

  server.sendHeader("Location", "/?msg=" + msg);
  server.send(302, "text/plain", "");
  inactivityTime=120;
}

void handleSave() {
  EEPROM.write(SELF_ADDRESS_ADDRESS, selfAddress);
  writeStringToEEPROM(LOCAL_IP_ADDRESS, local_ip);
  writeStringToEEPROM(SERVER_IP_ADDRESS, server_ip);
  EEPROM.commit();

  String msg = "Configuration saved successfully!<br>";
  msg += "BED ADDRESS: " + String(selfAddress) + "<br>";
  msg += "LOCAL IP: " + local_ip + "<br>";
  msg += "SERVER IP: " + server_ip;

  server.sendHeader("Location", "/?msg=" + msg);
  server.send(302, "text/plain", "");
  ESP.restart();
  
}

void writeStringToEEPROM(int address, String value) {
  for (int i = 0; i < value.length(); i++) {
    EEPROM.write(address + i, value[i]);
  }
  EEPROM.write(address + value.length(), '\0');
}

String readStringFromEEPROM(int address) {
  String value = "";
  char c;
  while ((c = EEPROM.read(address++)) != '\0') {
    value += c;
  }
  return value;
}
