#include <Arduino.h>
#include <vector>
#include <stdlib.h>
#include <stdio.h>

class SerialBuffer {
    public:
        SerialBuffer(int baudrate) : _baud(baudrate) {};
        String waitForSerialInput(String endl, int delayms); 
        bool init(int delayms);
        std::vector<double> parseSerial(String ln, char delim);

    private:
        int8_t _com;
        int _baud;        
};