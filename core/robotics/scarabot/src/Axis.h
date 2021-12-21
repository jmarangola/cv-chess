#pragma once
#include <stdlib.h>
#include <stdint.h>

class Axis {
    public:
        int8_t _pinStep, _pinDir, _spr;
        int32_t _maxSpeed, _acc;
        long _homePosition, _maximumPosition;
        double _reductiontionRatio;
        Axis(int8_t pStep, int8_t pDir, int32_t maxSpeed, int32_t acc, long homePosition, long maximumPosition, int8_t spr, double reducRat) 
            : _pinStep(pStep), _pinDir(pDir), _maxSpeed(maxSpeed), _acc(acc), _homePosition(homePosition), _maximumPosition(maximumPosition), _reductiontionRatio(reducRat) {};
};