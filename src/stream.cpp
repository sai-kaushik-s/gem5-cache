#include <iostream>
#include <vector>
#include <cstdint>
#include <iomanip>
#include "gem5/m5ops.h"

int main(int argc, char** argv) { // args: n stride
    uint64_t n      = (argc > 1) ? std::stoull(argv[1]) : 1024ULL;	// default: 1K
    uint64_t stride = (argc > 2) ? std::stoull(argv[2]) : 1ULL;		// default: 1
    
	if (stride <= 0) {
		std::cout <<"stride should be larger than 1\n";
		stride = 1;
	}

    std::vector<double> A(n, 0.0), B(n, 1.0), C(n, 2.0);
    volatile double s = 1.0;
    volatile double checksum = 0.0;
    
	m5_work_begin(0, 0); 
    for (uint64_t i = 0; i < n; i += stride) {
        A[i] = B[i] + s * C[i];
        checksum += A[i];
    }
    m5_work_end(0,0);

    std::cout << std::fixed << std::setprecision(6)
              << "stream_checksum " << (double)checksum << "\n";
    return 0;
}

