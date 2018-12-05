#include "extract.h"

void func_pattern(bit_pattern_t *bit)
{
	unsigned long int a;

	if(bit -> integer == 0)
	{
		a = *((unsigned long int *)&(bit -> floating));
	}
	else if(bit -> floating == 0)
	{
		a = bit -> integer;
	}
	else
	{
		a = *((unsigned long int *)(bit -> string));
	}

	bit -> sign = (a & 0x8000000000000000) >> 63;
	bit -> exponent = ((a & 0x3FF0000000000000) >> 52) - 1023;
	bit -> mantissa = a & 0xFFFFFFFFFFFFF;
}
