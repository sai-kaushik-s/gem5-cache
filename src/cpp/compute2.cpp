#include <iostream>
#include <vector>
#include <cstdint>
#include <cmath>
#include <iomanip>
#include "gem5/m5ops.h"

#if defined(__GNUC__) || defined(__clang__)
#define NOINLINE __attribute__((noinline))
#else
#define NOINLINE
#endif

static inline uint64_t rotl64(uint64_t x, unsigned r) {
    return (x << r) | (x >> (64 - r));
}

NOINLINE uint64_t mix(uint64_t v) {
    // a tiny mixing function to add dependency + ALU pressure
    v ^= v >> 23;
    v *= 0x2127599bf4325c37ULL;
    v ^= v >> 47;
    return v;
}

NOINLINE double poly_approx(double z) {
    // cheap polynomial to keep FP units busy without heavy libm
    // Horner form: z + 0.5 z^2 - 0.1 z^3 + 0.01 z^4
    double z2 = z * z;
    return z + 0.5*z2 + (-0.1)*z2*z + 0.01*z2*z2;
}

int main(int argc, char** argv) {
    uint64_t iters = (argc > 1) ? std::stoull(argv[1]) : 1024ULL;       // outer iterations
    uint64_t N     = (argc > 2) ? std::stoull(argv[2]) : (1u << 16);    // array size (power-of-two helps masking)

    // --- state & sinks ---
    volatile uint64_t a = 1, b = 2, c = 3, d = 4;
    volatile double   x = 1.0, y = 2.0, z = 0.5;

    // --- memory to touch (cache + TLB) ---
    std::vector<uint64_t> mem1(N, 0xdeadbeefULL);
    std::vector<uint64_t> mem2(N, 0xcafef00dULL);

    // --- build a pointer-chasing ring (linked list) ---
    struct Node { Node* next; uint64_t val; };
    std::vector<Node> nodes(1 << 12); // 4096 nodes
    for (size_t i = 0; i < nodes.size(); ++i) {
        nodes[i].next = &nodes[(i * 73 + 19) % nodes.size()]; // pseudo-random ring
        nodes[i].val  = (i * 0x9e3779b97f4a7c15ULL) ^ (i << 7);
    }
    Node* cursor = &nodes[123];

    // xorshift PRNG for unpredictable control flow & indices
    auto next_rand = [&](uint64_t& s)->uint64_t {
        s ^= s << 13;
        s ^= s >> 7;
        s ^= s << 17;
        return s;
    };

    uint64_t rng = 0x123456789abcdefULL ^ (iters << 32) ^ N;

    // volatile sinks to force side-effects
    volatile uint64_t checksum = 0;
    volatile double   fsum = 0.0;

    m5_work_begin(0, 0);
    for (uint64_t i = 0; i < iters; ++i) {
        // 1) Tight integer dependency chains
        a = a + b;  b = b + c;  c = c + d;  d = d + a;
        a += a + b; b += b + c; c += c + d; d += d + a;

        // 2) FP mix with data dependency and small polynomial
        x = x * 1.0000001 + 0.1;
        y = y * 0.9999999 + 0.2;
        z = poly_approx((x - y) * 0.0001 + z);

        // 3) PRNG + bit twiddling (rotates, mixes)
        uint64_t r = next_rand(rng);
        uint64_t p = mix(r ^ (uint64_t)x ^ (uint64_t)y);
        a ^= rotl64(p, (unsigned)(r & 63));
        b += p ^ rotl64(a, 17);
        c = (c * 0x9e3779b97f4a7c15ULL) + (d ^ (p >> 13));
        d ^= (a + b + c) | (p << 3);

        // 4) Unpredictable branches (roughly 50/50 on random bit)
        if (r & 1ULL) {
            // path A: memory-heavy with one stride
            uint64_t idxA = (r ^ a ^ (a >> 7)) & (N - 1);
            mem1[idxA] = mix(mem1[idxA] + a + (r << 5));
            x += (double)(mem1[idxA] & 0xFFFF) * 1e-6;
            // pointer chase
            cursor = cursor->next->next;
            a ^= cursor->val;
        } else {
            // path B: different stride & store pattern
            uint64_t idxB = (r + b + (b << 9)) & (N - 1);
            mem2[idxB] ^= (r * 0x5851f42d4c957f2dULL) ^ b;
            y += (double)((mem2[idxB] >> 8) & 0xFFFF) * 1e-6;
            // deeper pointer chase
            cursor = cursor->next->next->next;
            b += cursor->val;
        }

        // 5) Another control split with switch to add front-end pressure
        switch ((unsigned)((r >> 1) & 3)) {
            case 0:
                c ^= (c << 7) ^ (c >> 9);
                x += x * 1.0000001 + 0.1;
                break;
            case 1:
                d += (d << 5) | (d >> 11);
                y += y * 0.9999999 + 0.2;
                break;
            case 2:
                a += (a ^ b) + mix(c);
                z = poly_approx(z + 1e-4);
                break;
            default:
                b ^= (a + c + d);
                x += y * 1e-7;
                break;
        }

        // 6) Cross-iteration coupling via memory-derived feedback
        uint64_t feed = mem1[(a ^ r) & (N - 1)] ^ mem2[(b + r) & (N - 1)];
        a += feed; d ^= rotl64(feed, 29);

        // 7) Light “population count” flavor without builtin (keeps ALU busy)
        uint64_t t = (a ^ b ^ c ^ d) * 0x0101010101010101ULL;
        t = (t >> 56) + ((t >> 48) & 0xFF) + ((t >> 40) & 0xFF) +
            ((t >> 32) & 0xFF) + ((t >> 24) & 0xFF) + ((t >> 16) & 0xFF) +
            ((t >> 8) & 0xFF)  + (t & 0xFF);
        c += t;

        // accumulate sinks to avoid DCE
        checksum ^= a + (b << 1) + (c << 2) + (d << 3);
        fsum     += x + y + z * 1e-3;
    }
    m5_work_end(0, 0);

    // prevent optimizing away
    std::cout << "checksum=" << std::hex << checksum
              << " fsum=" << std::dec << std::setprecision(6) << fsum << "\n";

    return 0;
}

