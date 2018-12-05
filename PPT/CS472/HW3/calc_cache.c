#include <stdio.h>
#include <malloc.h>
#include <time.h>

#include "main.h"

void func_cache()
{
    clock_t tick;
    int size, mod, i, count;
    int *array;
    array = (int *)malloc(ARRAY_SIZE * sizeof(int));
    count = 1;

    for(size = 0; size * KILOBYTE < ARRAY_SIZE; size += 16, count ++)
    {
        tick = clock();
        mod = size * KILOBYTE - 1;

        for(i = 0; i < STEP; i ++)
        {
            array[(i * 16) % mod] ++;
        }

        if(count % 5 == 0)
        {
            printf("%d(KB): %.3f(s)", (mod + 1) / KILOBYTE, (double)(clock() - tick) / CLOCKS_PER_SEC);
            printf("\n");
        }
        else
        {
            printf("%d(KB): %.3f(s)<-->", (mod + 1) / KILOBYTE, (double)(clock() - tick) / CLOCKS_PER_SEC);
        }
    }

    printf("\nL1 Cache: (%dKB, %dKB)\nL2 Cache: %dKB\nL3 Cache: %dKB\n", 32, 32, 256, 12288);
    printf("Because there is a obvious leap of time cost at each value above, I think the three caches' sizes are 32KB/32KB, 256KB, and 12288KB on flip\n");
    array = NULL;
    free(array);
}

// void func_cache()
// {
//     clock_t tick;
//     double rec;
//     int size, mod, i, j;
//     int *array;
//     int size_array[] = {
//         1 * KILOBYTE, 2 * KILOBYTE, 4 * KILOBYTE, 8 * KILOBYTE,
//         16 * KILOBYTE, 32 * KILOBYTE, 64 * KILOBYTE, 128 * KILOBYTE,
//         256 * KILOBYTE, 512 * KILOBYTE, 1 * MEGABYTE, 2 * MEGABYTE,
//         3 * MEGABYTE, 4 * MEGABYTE, 5 * MEGABYTE, 6 * MEGABYTE,
//         7 * MEGABYTE, 8 * MEGABYTE, 9 * MEGABYTE, 10 * MEGABYTE,
//         11 * MEGABYTE, 12 * MEGABYTE, 13 * MEGABYTE, 14 * MEGABYTE,
//         15 * MEGABYTE, 16 * MEGABYTE
//     };
//     array = (int *)malloc(SIZE * sizeof(int));
//
//     for(size = 0; size < sizeof(size_array) / sizeof(int); size ++)
//     {
//         for(j = 0; j < 8; j ++)
//         {
//             tick = clock();
//             mod = size_array[size] / sizeof(int) - 1;
//
//             for(i = 0; i < STEP; i ++)
//             {
//                 array[(i * 16) % mod] ++;
//             }
//
//             rec = (double)(clock() - tick) / CLOCKS_PER_SEC;
//         }
//
//         printf("%d(KB): %f(s)\n", size_array[size] / KILOBYTE, rec);
//     }
//
//     array = NULL;
//     free(array);
// }
