#include <stdint.h>
#include "statistics.h"

#define MEMORY_ACCESS_TIME      100 /* 100 ns */
#define DISK_ACCESS_TIME   10000000 /* 10 million ns = 10 ms */

double compute_emat() {
    /* FIX ME - Compute the average mean access time.  You should only need the
    * numbers contained in the following variables. You may or may not need to
    * use them all:
    *    count_pagefaults   - the number of page faults that occurred
    *                         (note: this _does_ include the unavoidable page
    *                                fault when a process is first brought into
    *                                memory upon starting)
    *    count_tlbhits      - the number of tlbhits that occurred
    *    count_writes       - the number of stores/writes that occurred
    *    count_reads        - the number of reads that occurred
    *
    * Any other values you might need are composites of the above values.  Some
    * of these computations have been done for you, in case you need them.
    */

    /* uint64_t total_accesses = count_writes + count_reads; */
    /* uint64_t tlb_misses     = total_accesses - count_tlbhits; */

    return tlb_misses * 2 * MEMORY_ACCESS_TIME + count_pagefaults * DISK_ACCESS_TIME;
}
