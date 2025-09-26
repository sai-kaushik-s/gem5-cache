#include <iostream>
#include <fstream>
#include "gem5/m5ops.h"

int main(int argc, char** argv){
    m5_work_begin(0, 0);

    std::ofstream logFile("test_log.txt");
    if (logFile.is_open()) {
        logFile << argc << std::endl;
        for(int i = 0; i < argc; i++){
            logFile << "argv[" << i << "] = " << argv[i] << std::endl;
        }
        logFile.close();
    } else {
        std::cerr << "Unable to open log file." << std::endl;
    }

    m5_work_end(0,0);
    return 0;
}
