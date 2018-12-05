#include <stdio.h>

#include "arithm.h"
#include "frexp.h"

double func_add(double x, double y)
{
	double z;
	unsigned long int a, b, xfrac, yfrac, frac, shift;
	int diff, scale, xexp, yexp, exp;

	if(x < 0 && y < 0)
	{
		return -1 * func_add(0 - x, 0 - y);
	}
	else if(x < 0 && y > 0)
	{
		return -1 * func_sub(0 - x, y);
	}
	else if(x > 0 && y < 0)
	{
		return func_sub(x, 0 - y);
	}
	else
	{
		a = *((unsigned long int *)&x);
		b = *((unsigned long int *)&y);
		// printf("[%f=%lx]\n[%f=%lx]\n", x, a, y, b);
		xexp = (a & 0x7FF0000000000000) >> 52;
		yexp = (b & 0x7FF0000000000000) >> 52;
		xfrac = a & 0xFFFFFFFFFFFFF;
		yfrac = b & 0xFFFFFFFFFFFFF;
		// printf("[%lx, %lx, %d, %d]\n", xfrac, yfrac, xexp - 1023, yexp - 1023);
		if(xexp > yexp)
		{
			diff = xexp - yexp;
			exp = xexp - 1023;
			// frac = (xfrac | 0x10000000000000) + (yfrac >> diff);
		}
		else if (xexp < yexp)
		{
			diff = yexp - xexp;
			exp = yexp - 1023;
			// frac = (yfrac | 0x10000000000000) + (xfrac >> diff);
			frac = (yfrac | 0x10000000000000) + ((xfrac | 0x10000000000000) >> diff);
		}
		else
		{
			exp = xexp;
			frac = (xfrac | 0x10000000000000) + (yfrac | 0x10000000000000);
			frac = frac >> 1;
			shift = 1;
			z = (1 + (frac & 0xFFFFFFFFFFFFF) / (double)(shift << 52)) * (1 << (exp + 2));
			return z;
		}
		// printf("[%lx, %d]\n", frac, exp);
		shift = 1;
		scale = (frac & 0xF0000000000000) >> 52;
		// printf("[%d, %d]\n", scale, (1 << exp));
		z = (scale + (frac & 0xFFFFFFFFFFFFF) / (double)(shift << 52)) * (1 << exp);
		return (xfrac == 0 && yfrac == 0) ? z : z + 2;
	}
}

double func_sub(double x, double y)
{
	double z;
	unsigned long int a, b, xfrac, yfrac, frac, shift;
	int diff, scale, sign, xexp, yexp, exp;
	
	if(x < 0 && y > 0)
	{
		return -1 * func_add(0 - x, y);
	}
	else if(x > 0 && y < 0)
	{
		return func_add(x, 0 - y);
	}
	else if(x < 0 && y < 0)
	{
		return -1 * func_sub(0 - x, 0 - y);
	}
	else
	{
		sign = ((x < 0 && y < 0) || (x > 0 && y > 0)) ? 1 : -1;
		a = *((unsigned long int *)&x);
		b = *((unsigned long int *)&y);
		// printf("[%f=%lx]\n[%f=%lx]\n", x, a, y, b);
		xexp = (a & 0x7FF0000000000000) >> 52;
		yexp = (b & 0x7FF0000000000000) >> 52;
		xfrac = a & 0xFFFFFFFFFFFFF;
		yfrac = b & 0xFFFFFFFFFFFFF;
		// printf("[%lx, %lx, %d, %d]\n", xfrac, yfrac, xexp - 1023, yexp - 1023);
		if(xexp > yexp)
		{
			diff = xexp - yexp;
			exp = xexp - 1023;
			frac = (xfrac | 0x10000000000000) - ((yfrac | 0x10000000000000) >> diff);
		}
		else if (xexp < yexp)
		{
			diff = yexp - xexp;
			exp = yexp - 1023;
			frac = (yfrac | 0x10000000000000) - ((xfrac | 0x10000000000000) >> diff);
		}
		else
		{
			xfrac = xfrac | 0x10000000000000;
			yfrac = yfrac | 0x10000000000000;
			exp = xexp - 1023;

			if(xfrac < yfrac)
			{
				sign = -1;
				frac = yfrac - xfrac;
			}
			else if(xfrac > yfrac)
			{
				sign = 1;
				frac = xfrac - yfrac;
			}
			else
			{
				return 0;
			}

			shift = 1;
			z = (frac & 0xFFFFFFFFFFFFF) / (double)(shift << 52) * (1 << exp);
			return sign * z;
		}
		// printf("[%lx, %d]\n", frac, exp);
		shift = 1;
		scale = (frac & 0xF0000000000000) >> 52;		
		// printf("[%d, %d]\n", scale, (1 << exp));
		z = (scale + (frac & 0xFFFFFFFFFFFFF) / (double)(shift << 52)) * (1 << exp);
		return sign * (z - 2);
	}
}

double func_mul(double x, double y)
{
	double z;
	unsigned long int a, b, xfrac, yfrac, frac, temp, shift;
	int xexp, yexp, exp, scale, sign;
	sign = ((x < 0 && y < 0) || (x > 0 && y > 0)) ? 1 : -1;
	a = *((unsigned long int *)&x);
	b = *((unsigned long int *)&y);
	// printf("[%f=%lx]\n[%f=%lx]\n", x, a, y, b);
	xexp = (a & 0x7FF0000000000000) >> 52;
	yexp = (b & 0x7FF0000000000000) >> 52;
	xfrac = a & 0xFFFFFFFFFFFFF;
	yfrac = b & 0xFFFFFFFFFFFFF;
	// printf("[%lx, %lx, %d, %d]\n", xfrac, yfrac, xexp - 1023, yexp - 1023);
	if(xexp > yexp)
	{
		xfrac = xfrac | 0x10000000000000;
		xfrac = xfrac >> 20;
		yfrac = yfrac | 0x10000000000000;
		yfrac = yfrac >> 24;
	}
	else if (xexp < yexp)
	{
		yfrac = yfrac | 0x10000000000000;
		yfrac = yfrac >> 20;
		xfrac = xfrac | 0x10000000000000;
		xfrac = xfrac >> 24;
	}
	else
	{
		xfrac = xfrac | 0x10000000000000;
		xfrac = xfrac >> 24;
		yfrac = yfrac | 0x10000000000000;
		yfrac = yfrac >> 24;
		exp = xexp - 1023 + yexp - 1023;
		frac = shift = 0;

		do
		{
			temp = xfrac;

			if((yfrac & 0x01) == 1)
			{
				temp = temp << shift;
				frac += temp;
			}
			
			yfrac = yfrac >> 1;
			shift ++;
		}
		while(yfrac != 0);

		shift = 1;
		scale = (frac & 0xF00000000000000) >> 56;
		z = sign * (scale + (frac & 0xFFFFFFFFFFFFFF) / (double)(shift << 56)) * (1 << exp);
		return z;
	}

	exp = xexp - 1023 + yexp - 1023;
	// printf("[%lx, %lx, %lx, %d]\n", xfrac, yfrac, xfrac * yfrac, exp);
	frac = shift = 0;

	do
	{
		temp = xfrac;

		if((yfrac & 0x01) == 1)
		{
			temp = temp << shift;
			frac += temp;
		}
		
		yfrac = yfrac >> 1;
		shift ++;
	}
	while(yfrac != 0);
	// printf("[%lx, %lx]\n", frac, (frac & 0xF000000000000000) >> 60);
	shift = 1;
	scale = (frac & 0xF000000000000000) >> 60;
	z = sign * (scale + (frac & 0xFFFFFFFFFFFFFFF) / (double)(shift << 60)) * (1 << exp);
	return z;
}

double func_div(double x, double y)
{
	double z;
	unsigned long int a, b, xfrac, yfrac, xtmp, ytmp, flag, frac, pos, shift;
	int diff, xexp, yexp, scale, sign;

	if(y == 0)
	{
		printf("Warning: Denumerator can't be ZERO.\n");
		return -1;
	}

	sign = ((x < 0 && y < 0) || (x > 0 && y > 0)) ? 1 : -1;
	a = *((unsigned long int *)&x);
	b = *((unsigned long int *)&y);
	// printf("[%f=%lx]\n[%f=%lx]\n", x, a, y, b);
	xexp = (a & 0x7FF0000000000000) >> 52;
	yexp = (b & 0x7FF0000000000000) >> 52;
	xtmp = xfrac = a & 0xFFFFFFFFFFFFF;
	ytmp = yfrac = b & 0xFFFFFFFFFFFFF;
	// printf("[%lx, %lx, %d, %d]\n", xfrac, yfrac, xexp - 1023, yexp - 1023);
	if(xexp > yexp)
	{
		diff = xexp - yexp;
		yfrac = yfrac | 0x10000000000000;
		yfrac = yfrac >> diff;
		yfrac = yfrac >> 24;
		xfrac = xfrac | 0x10000000000000;
		xfrac = xfrac >> 24;
	}
	else if (xexp < yexp)
	{
		diff = yexp - xexp;
		xfrac = xfrac | 0x10000000000000;
		xfrac = xfrac >> diff;
		xfrac = xfrac >> 24;
		yfrac = yfrac | 0x10000000000000;
		yfrac = yfrac >> 24;
	}
	else
	{
		if(xfrac == yfrac)
		{
			return 1;
		}
		else
		{
			diff = 0;
			xfrac = (xfrac | 0x10000000000000) >> 24;
			yfrac = (yfrac | 0x10000000000000) >> 24;
		}
	}

	frac = xfrac / yfrac;
	// printf("[%lx, %lx, %lx]\n", xfrac, yfrac, frac);
	if(frac > 1)
	{
		flag = frac;
		scale = (frac & 0xF0) >> 4;
		xfrac = xfrac - yfrac * frac;	
		shift = 4;

		while(shift <= 32 && xfrac != 0)
		{
			pos = shift;
		
			while(xfrac < yfrac)
			{
				xfrac = xfrac << 1;
				shift ++;
			}
			
			frac = (frac << (shift - pos)) + 1;
			xfrac = xfrac - yfrac;
		}
		// printf(">>>[%lx, %ld]\n", frac, shift);
		pos = shift;
		shift = 1;
		scale = flag;
		z = scale + frac / (double)(shift << pos);
	}
	else if(frac < 1)
	{
		frac = 1;
		shift = 0;
		
		while(shift <= 32 && xfrac != 0)
		{
			pos = shift;
		
			while(xfrac < yfrac)
			{
				xfrac = xfrac << 1;
				shift ++;
			}
			
			frac = (frac << (shift - pos)) + 1;
			xfrac = xfrac - yfrac;
		}
		printf("<<<[%lx, %ld]\n", frac, shift);
		pos = shift;
		shift = 1;

		if(xtmp == 0 && ytmp == 0)
		{
			scale = 0;
			z = scale + (frac & 0x01) / (double)(shift << pos);
		}
		else
		{
			scale = 0;
			z = scale + (frac & 0x1FFFFFFFF) / (double)(shift << (pos + 1));
			z *= 2;
		}
	}
	else
	{
		frac = 1;
		shift = 0;

		while(shift <= 32 && xfrac != 0)
		{
			pos = shift;
		
			while(xfrac < yfrac)
			{
				xfrac = xfrac << 1;
				shift ++;
			}
			
			frac = (frac << (shift - pos)) + 1;
			xfrac = xfrac - yfrac;
		}
		// printf("===[%lx, %ld]\n", frac, shift);
		pos = shift;
		shift = 1;
		scale = 1;
		z = scale + (frac & 0x1FFFFFFFF) / (double)(shift << (pos + 1));
	}
	
	return sign * z;
}

// double func_sqrt(double x)
// {
// 	unsigned long int a, frac, rmd, root, div;
// 	unsigned int exp, i;

// 	a = *((unsigned long int *)&x);
// 	exp = ((a & 0x7FF0000000000000) >> 52) - 1023;
// 	frac = a & 0xFFFFFFFFFFFFF;
// 	frac = frac | 0x10000000000000;
// 	printf("[%lx, %d]\n", frac, exp);
// 	if(exp % 2 == 1)
// 	{
// 		frac = frac << 1;
// 	}

// 	rmd = root = div = 0;

// 	for(i = 0; i < 16; i ++)
// 	{
// 		root = root << 1;
// 		rmd = (rmd << 2) + (frac >> 30);
// 		frac = frac << 2;
// 		div = (root << 1) + 1;

// 		if(div <= rmd)
// 		{
// 			rmd -= div;
// 			root ++;
// 		}
// 	}
// 	printf("[%lx]\n", root);
// 	return 0;
// }

// double func_sqrt(double x)
// {
// 	double eps, t;

// 	if(x < 0)
// 	{
// 		printf("Warning: Nagetive number can't be accepted.\n");
// 		return -1;
// 	}

// 	t = x;
// 	eps = 0.0000000000001;

// 	while(t * t - x > eps)
// 	{
// 		t = (t + x / t) / 2.0;
// 	}

// 	return t;
// }

double func_sqrt(double x)
{
	unsigned int a;
	float num, y, z;
	num = (float)x;
	z = num;
	a = *((unsigned int *)&z);
	a = 0x5F3759DF - (a >> 1);
	z = *((float *)&a);
	y = x * 0.5;
	z = z * (1.5 - (y * z * z));
	z = z * (1.5 - (y * z * z));
	z = z * (1.5 - (y * z * z));
	z = z * (1.5 - (y * z * z));
	z = z * (1.5 - (y * z * z));
	return 1 / (double)z;
}