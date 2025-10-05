#include <iostream>
#include <fstream>
#include <cstdint>
#include "gem5/m5ops.h"

struct Node {
    Node* next;
    uint64_t data;
};

int main(int argc, char** argv) {
    uint64_t n_nodes = (argc > 1) ? std::stoull(argv[1]) : 1024ULL;
    uint64_t traverses = (argc > 2) ? std::stoull(argv[2]) : 4ULL;
    if (n_nodes < 2) n_nodes = 2;

    Node* head = nullptr;
    Node* prev = nullptr;
    for (uint64_t i = 0; i < n_nodes; ++i) {
        Node* node = new Node;
        node->data = i;
        node->next = nullptr;
        if (!head)
            head = node;
        else
            prev->next = node;
        prev = node;
    }

    m5_work_begin(0, 0);
    volatile Node* p;
    uint64_t sum = 0;
    for (uint64_t r = 0; r < traverses; ++r) {
        for (p = head; p != nullptr; p = p->next) {
            sum += p->data;
        }
    }
    m5_work_end(0, 0);

    p = head;
    while (p != nullptr) {
        Node* tmp = const_cast<Node*>(p);
        p = p->next;
        delete tmp;
    }

    return 0;
}
