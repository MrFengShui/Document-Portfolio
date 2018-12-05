#include <stdio.h>
#include <string.h>
#include <math.h>

#include "arithm.h"
#include "frexp.h"
#include "extract.h"

#define NUM 1024
#define SIZE 9

static double LHS[] = {1, 16.895, 3.1, -3.2, -3.2, 7.1, 3.336, 3.2, 34.2};
static double RHS[] = {2.5, 16.895, -3.2, 3.3, -7.1, 3.2, 17.425, 127.1, 127.1};
static double SQRT[] = {2, 3, 4, 5, 2.1, 11.2, 64, 72.5, 109.786};

static __inline unsigned long int func_tick()
{
	unsigned long int eax, edx;

	__asm__ __volatile__ (
		"cpuid;rdtsc"
		: "=edx" (edx), "=eax" (eax)
	);

	return (unsigned long int)((edx << 32) | eax);
}

int main(int argc, char *argv[])
{
	printf("----------------------------PART I----------------------------\n");
	{
		double fraction;
		int exponent;

		fraction = func_frexp(NUM, &exponent);
		printf("Fraction: %f\n", fraction);
		printf("Exponent: %d\n", exponent);

		fraction = frexp(NUM, &exponent);
		printf("Fraction: [%f]\n", fraction);
		printf("Exponent: [%d]\n", exponent);
	}
	printf("----------------------------PART II---------------------------\n");
	{
		unsigned long int start, end;
		double rs;
		int i;

		for(i = 0; i < SIZE; i ++)
		{
			printf("-----------------Round %d-----------------\n", i + 1);

			start = func_tick();
			rs = func_add(LHS[i], RHS[i]);
			end = func_tick();
			printf("Addtion: [%f + %f = %f] (%fs)\n", LHS[i], RHS[i], rs, (double)((end - start) / 2660219000.00));

			start = func_tick();
			rs = func_sub(LHS[i], RHS[i]);
			end = func_tick();
			printf("Subtract: [%f - %f = %f] (%fs)\n", LHS[i], RHS[i], rs, (double)((end - start) / 2660219000.00));

			start = func_tick();
			rs = func_mul(LHS[i], RHS[i]);
			end = func_tick();
			printf("Multiply: [%f * %f = %f] (%fs)\n", LHS[i], RHS[i], rs, (double)((end - start) / 2660219000.00));

			start = func_tick();
			rs = func_div(LHS[i], RHS[i]);
			end = func_tick();
			printf("Division: [%f / %f = %f] (%fs)\n", LHS[i], RHS[i], rs, (double)((end - start) / 2660219000.00));

			start = func_tick();
			rs = func_sqrt(SQRT[i]);
			end = func_tick();
			printf("Square: [%f --> %f] (%fs)\n", SQRT[i], rs, (double)((end - start) / 2660219000.00));
		}
	}
	printf("----------------------------PART II---------------------------\n");
	{
		bit_pattern_t bit;

		bit.floating = 3.1415926;
		bit.integer = 0;
		bit.string[0] = '\0';
		func_pattern(&bit);
		printf("Value: %f\n-->sign: %d\n-->exponent: %d\n-->mantissa: %lx\n", bit.floating, bit.sign, bit.exponent, bit.mantissa);

		bit.floating = 0;
		bit.integer = -31415926;
		bit.string[0] = '\0';
		func_pattern(&bit);
		printf("Value: %ld\n-->sign: %d\n-->exponent: %d\n-->mantissa: %lx\n", bit.integer, bit.sign, bit.exponent, bit.mantissa);

		bit.floating = 0;
		bit.integer = 0;
		memcpy(bit.string, "HelloYou", 8);
		func_pattern(&bit);
		printf("Value: %s(%ld)\n-->sign: %d\n-->exponent: %d\n-->mantissa: %lx\n", bit.string, *((unsigned long int *)bit.string), bit.sign, bit.exponent, bit.mantissa);
	}

	return 0;
}