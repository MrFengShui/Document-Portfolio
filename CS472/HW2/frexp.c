#include "frexp.h"

double func_frexp(double x, int *exponent)
{
	double fraction;
	unsigned long int tmp, shift;
	
	tmp = *((unsigned long int *)&x);
	*exponent = (((tmp & F64_EXP_MASK) >> F64_EXP_SHIFT) - 1023) + 1;
	shift = 1;
	shift = (shift << F64_FRAC_SHIFT);
	shift = (shift << F64_FRAC_SHIFT);
	shift = (shift << F64_FRAC_SHIFT);
	shift = (shift << F64_FRAC_SHIFT);
	fraction = (double)(((tmp & F64_FRAC_MASK) / (double)shift) + 1) / 2;
	return fraction;
}