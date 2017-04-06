#ifndef _FREXP_H_
#define _FREXP_H_

#define F64_SIGN_MASK 0x8000000000000000
#define F64_EXP_MASK  0x7FF0000000000000
#define F64_FRAC_MASK 0xFFFFFFFFFFFFF

#define F64_SIGN_SHIFT 63
#define F64_EXP_SHIFT  52
#define F64_FRAC_SHIFT 13

double func_frexp(double, int *);

#endif