#include <iostream>
#include <vector>
#include <cstdint>
#include <iomanip>
#include "gem5/m5ops.h"
#include <fstream>

struct Node {
    Node* next;
    uint64_t data;
};

int main(int argc, char** argv) {
    // args: [n_nodes] [traverses]
    uint64_t n_nodes = (argc > 1) ? std::stoull(argv[1]) : 1024ULL; //default: 1024
    uint64_t traverses  = (argc > 2) ? std::stoull(argv[2]) : 4ULL;	//default: 4
    if (n_nodes < 2) n_nodes = 2;

    // allocate and link sequentially into a cycle
    std::vector<Node> nodes(n_nodes);
    for (uint64_t i = 0; i < n_nodes; ++i) {
        nodes[i].next = &nodes[(i + 1) % n_nodes];
        nodes[i].data  = i;
    }
	nodes[n_nodes-1].next=NULL;

    // pointer chase: dependent loads; minimal MLP
    volatile Node* p;
    uint64_t sum = 0;

    m5_work_begin(0, 0); 
//	std::ofstream logFile;
//	logFile.open("test_log.txt");
  //  logFile << "ARGC" <<n_nodes<<"\n";
    //logFile << "ARGC2" <<traverses<<"\n";
	for (uint64_t r = 0; r < traverses; ++r) {
		p=&nodes[0];
		for (p=&nodes[0];p!=NULL;p=p->next){
			sum+=p->data;
        }
    }
//	logFile << "chase_checksum " << sum << "\n";
//	logFile.close();
    m5_work_end(0,0);
	
    return 0;
}

