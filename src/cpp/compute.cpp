#include <iostream>
#include <iomanip>
#include <cstdint>
#include "gem5/m5ops.h"


int main(int argc, char** argv) {
    uint64_t iters = (argc > 1) ? std::stoull(argv[1]) : 1024ULL; //default: 1024

    volatile uint64_t a = 1, b = 2, c = 3, d = 4;
    volatile double   x = 1.0, y = 2.0;

    m5_work_begin(0, 0); 
    for (uint64_t i = 0; i < iters; ++i) {
        a = a + b;
        b = b + c;
        c = c + d;
        d = d + a;

        x = x * 1.0000001 + 0.1;
        y = y * 0.9999999 + 0.2;
    }
    m5_work_end(0,0);

    return 0;
}

