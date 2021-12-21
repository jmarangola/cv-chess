/**
 * @brief 
 * 
 * John Marangola - marangol@bc.edu
 */

#include "SerialBuffer.h"


String SerialBuffer::waitForSerialInput(String endl, int delayms) {
    String read;
    while (!Serial.available()) 
        delay(delayms);
    read = Serial.readStringUntil('\n', 120);
    Serial.write("rec\n");
    return read;
}

std::vector<double> SerialBuffer::parseSerial(String ln, char delim) {
    std::vector<double> coords;
    // Ignore signature bit
    int startIdx = 1;
    double ctemp;
    char * ptr;
    String tmp;
    for (int i = 0; i < 3; ++i) {
        tmp = "";
        for (int x = startIdx; x < ln.length(); ++x) {
            if (ln[x] == delim)
                break;
            tmp += ln[x];
        }   
        ctemp = strtod(tmp.c_str(), &ptr);
        // Add coord to vector
        coords.push_back(ctemp);
    }
    return coords;
}  

bool SerialBuffer::init(int delayms) {
    Serial.begin(this->_baud);
    delay(delayms);
    return (Serial) ? true: false;
}
