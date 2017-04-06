#include <stdio.h>
#include <string.h>

#include "cpuid.h"

int main(int argc, char *argv[])
{
	printf("--------------------------Vendor ID----------------------------\n");
	func_vendor_info();
	printf("---------------------------L1 Cache----------------------------\n");
	func_l1_info();
	printf("---------------------------TLB Info----------------------------\n");
	func_tlb_info();
	printf("--------------------Memory Hierarchy Info----------------------\n");
	func_mem_info();
	printf("-------------------------Address Info--------------------------\n");
	func_addr_info();
	printf("------------------Number of Logical Processor------------------\n");
	func_number_info();
	printf("---------------------------CPU Info----------------------------\n");
	func_family_info();
	func_model_info();
	func_name_info();
	func_frequency_info();
	printf("-------------------------Feature Info--------------------------\n");
	func_feature_info();
	return 0;
}

void func_vendor_info()
{
	unsigned int eax, ebx, ecx, edx;
	
	char vendor[13];
	
	eax = 0x00;

	__asm__ __volatile__(
		"cpuid;"
		: "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
		: "a"(eax)
	);
	
	memcpy(vendor, (char*)&ebx, 4);
	memcpy(vendor + 4, (char*)&edx, 4);
	memcpy(vendor + 8, (char*)&ecx, 4);
	vendor[12] = 0;
	
	printf("Vendor ID: %s\n", vendor);
}

void func_l1_info()
{
	unsigned int eax, ebx, ecx, edx;
	unsigned int way, partition, set, line, size;
	unsigned int array[] = {0x00, 0x01}, i;
	char *type[] = {"Data", "Instruction"};
	
	for(i = 0; i < 2; i ++)
	{
		eax = 0x04;
		ecx = array[i];
			
		__asm__ __volatile__(
			"cpuid;"
			: "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
			: "a"(eax), "c"(ecx)
		);
		
		way = (ebx & 0xFFF00000) >> 22;
		partition = (ebx & 0x3FF000) >> 12;
		line = ebx & 0xFFF;
		set = ecx;	
		size = (way + 1) * (partition + 1) * (line + 1) * (set + 1);
		
		printf("L1 Cache %s Size: %d(bytes)\n", type[i], size);
	}
}

void func_check_tlb(unsigned int x)
{
	switch(x)
	{
		case 0x01:
			printf("Instruction TLB: 4 KByte pages, 4-way set associative, 32 entries\n");
			break;
		case 0x02:
			printf("Instruction TLB: 4 MByte pages, fully associative, 2 entries\n");
			break;
		case 0x03:
			printf("Data TLB: 4 KByte pages, 4-way set associative, 64 entries\n");
			break;
		case 0x04:
			printf("Data TLB: 4 MByte pages, 4-way set associative, 8 entries\n");
			break;
		case 0x05:
			printf("Data TLB1: 4 MByte pages, 4-way set associative, 32 entries\n");
			break;
		case 0x06:
			printf("1st-level instruction cache: 8 KBytes, 4-way set associative, 32 byte line size\n");
			break;
		case 0x08:
			printf("1st-level instruction cache: 16 KBytes, 4-way set associative, 32 byte line size\n");
			break;
		case 0x09:
			printf("1st-level instruction cache: 32KBytes, 4-way set associative, 64 byte line size\n");
			break;
		case 0x0A:
			printf("1st-level data cache: 8 KBytes, 2-way set associative, 32 byte line size\n");
			break;
		case 0x0B:
			printf("Instruction TLB: 4 MByte pages, 4-way set associative, 4 entries\n");
			break;
		case 0x0C:
			printf("1st-level data cache: 16 KBytes, 4-way set associative, 32 byte line size\n");
			break;
		case 0x0D:
			printf("1st-level data cache: 16 KBytes, 4-way set associative, 64 byte line size\n");
			break;
		case 0x0E:
			printf("1st-level data cache: 24 KBytes, 6-way set associative, 64 byte line size\n");
			break;
		case 0x1D:
			printf("2nd-level cache: 128 KBytes, 2-way set associative, 64 byte line size\n");
			break;
		case 0x21:
			printf("2nd-level cache: 256 KBytes, 8-way set associative, 64 byte line size\n");
			break;
		case 0x22:
			printf("3rd-level cache: 512 KBytes, 4-way set associative, 64 byte line size, 2 lines per sector\n");
			break;
		case 0x23:
			printf("3rd-level cache: 1 MBytes, 8-way set associative, 64 byte line size, 2 lines per sector\n");
			break;
		case 0x24:
			printf("2nd-level cache: 1 MBytes, 16-way set associative, 64 byte line size\n");
			break;
		case 0x25:
			printf("3rd-level cache: 2 MBytes, 8-way set associative, 64 byte line size, 2 lines per sector\n");
			break;
		case 0x29:
			printf("3rd-level cache: 4 MBytes, 8-way set associative, 64 byte line size, 2 lines per sector\n");
			break;
		case 0x2C:
			printf("1st-level data cache: 32 KBytes, 8-way set associative, 64 byte line size\n");
			break;
		case 0x30:
			printf("1st-level instruction cache: 32 KBytes, 8-way set associative, 64 byte line size\n");
			break;
		case 0x40:
			printf("No 2nd-level cache or, if processor contains a valid 2nd-level cache, no 3rd-level cache\n");
			break;
		case 0x41:
			printf("2nd-level cache: 128 KBytes, 4-way set associative, 32 byte line size\n");
			break;
		case 0x42:
			printf("2nd-level cache: 256 KBytes, 4-way set associative, 32 byte line size\n");
			break;
		case 0x43:
			printf("2nd-level cache: 512 KBytes, 4-way set associative, 32 byte line size\n");
			break;
		case 0x44:
			printf("2nd-level cache: 1 MByte, 4-way set associative, 32 byte line size\n");
			break;
		case 0x45:
			printf("2nd-level cache: 2 MByte, 4-way set associative, 32 byte line size\n");
			break;
		case 0x46:
			printf("3rd-level cache: 4 MByte, 4-way set associative, 64 byte line size\n");
			break;
		case 0x47:
			printf("3rd-level cache: 8 MByte, 8-way set associative, 64 byte line size\n");
			break;
		case 0x48:
			printf("2nd-level cache: 3MByte, 12-way set associative, 64 byte line size\n");
			break;
		case 0x49:
			printf("3rd-level cache: 4MB, 16-way set associative, 64-byte line size\n");
			break;
		case 0x4A:
			printf("3rd-level cache: 6MByte, 12-way set associative, 64 byte line size\n");
			break;
		case 0x4B:
			printf("3rd-level cache: 8MByte, 16-way set associative, 64 byte line size\n");
			break;
		case 0x4C:
			printf("3rd-level cache: 12MByte, 12-way set associative, 64 byte line size\n");
			break;
		case 0x4D:
			printf("3rd-level cache: 16MByte, 16-way set associative, 64 byte line size\n");
			break;
		case 0x4E:
			printf("2nd-level cache: 6MByte, 24-way set associative, 64 byte line size\n");
			break;
		case 0x4F:
			printf("Instruction TLB: 4 KByte pages, 32 entries\n");
			break;
		case 0x50:
			printf("Instruction TLB: 4 KByte and 2-MByte or 4-MByte pages, 64 entries\n");
			break;
		case 0x51:
			printf("Instruction TLB: 4 KByte and 2-MByte or 4-MByte pages, 128 entries\n");
			break;
		case 0x52:
			printf("Instruction TLB: 4 KByte and 2-MByte or 4-MByte pages, 256 entries\n");
			break;
		case 0x55:
			printf("Instruction TLB: 2-MByte or 4-MByte pages, fully associative, 7 entries\n");
			break;
		case 0x56:
			printf("Data TLB0: 4 MByte pages, 4-way set associative, 16 entrie\n");
			break;
		case 0x57:
			printf("Data TLB0: 4 KByte pages, 4-way associative, 16 entries\n");
			break;
		case 0x59:
			printf("Data TLB0: 4 KByte pages, fully associative, 16 entries\n");
			break;
		case 0x5A:
			printf("Data TLB0: 2 MByte or 4 MByte pages, 4-way set associative, 32 entries\n");
			break;
		case 0x5B:
			printf("Data TLB: 4 KByte and 4 MByte pages, 64 entries\n");
			break;
		case 0x5C:
			printf("Data TLB: 4 KByte and 4 MByte pages,128 entries\n");
			break;
		case 0x5D:
			printf("Data TLB: 4 KByte and 4 MByte pages,256 entries\n");
			break;
		case 0x60:
			printf("1st-level data cache: 16 KByte, 8-way set associative, 64 byte line size\n");
			break;
		case 0x61:
			printf("Instruction TLB: 4 KByte pages, fully associative, 48 entries\n");
			break;
		case 0x63:
			printf("Data TLB: 2 MByte or 4 MByte pages, 4-way set associative, 32 entries and a separate array with 1 GByte pages, 4-way set associative, 4 entries\n");
			break;
		case 0x64:
			printf("Data TLB: 4 KByte pages, 4-way set associative, 512 entries\n");
			break;
		case 0x66:
			printf("1st-level data cache: 8 KByte, 4-way set associative, 64 byte line size\n");
			break;
		case 0x67:
			printf("1st-level data cache: 16 KByte, 4-way set associative, 64 byte line size\n");
			break;
		case 0x68:
			printf("1st-level data cache: 32 KByte, 4-way set associative, 64 byte line size\n");
			break;
		case 0x6A:
			printf("uTLB: 4 KByte pages, 8-way set associative, 64 entries\n");
			break;
		case 0x6B:
			printf("DTLB: 4 KByte pages, 8-way set associative, 256 entries\n");
			break;
		case 0x6C:
			printf("DTLB: 2M/4M pages, 8-way set associative, 128 entries\n");
			break;
		case 0x6D:
			printf("DTLB: 1 GByte pages, fully associative, 16 entries\n");
			break;
		case 0x70:
			printf("Trace cache: 12 K-μop, 8-way set associative\n");
			break;
		case 0x71:
			printf("Trace cache: 16 K-μop, 8-way set associative\n");
			break;
		case 0x72:
			printf("Trace cache: 32 K-μop, 8-way set associative\n");
			break;
		case 0x76:
			printf("Instruction TLB: 2M/4M pages, fully associative, 8 entries\n");
			break;
		case 0x78:
			printf("2nd-level cache: 1 MByte, 4-way set associative, 64byte line size\n");
			break;
		case 0x79:
			printf("2nd-level cache: 128 KByte, 8-way set associative, 64 byte line size, 2 lines per sector\n");
			break;
		case 0x7A:
			printf("2nd-level cache: 256 KByte, 8-way set associative, 64 byte line size, 2 lines per sector\n");
			break;
		case 0x7B:
			printf("2nd-level cache: 512 KByte, 8-way set associative, 64 byte line size, 2 lines per sector\n");
			break;
		case 0x7C:
			printf("2nd-level cache: 1 MByte, 8-way set associative, 64 byte line size, 2 lines per sector\n");
			break;
		case 0x7D:
			printf("2nd-level cache: 2 MByte, 8-way set associative, 64byte line size\n");
			break;
		case 0x7F:
			printf("2nd-level cache: 512 KByte, 2-way set associative, 64-byte line size\n");
			break;
		case 0x80:
			printf("2nd-level cache: 512 KByte, 8-way set associative, 64-byte line size\n");
			break;
		case 0x82:
			printf("2nd-level cache: 256 KByte, 8-way set associative, 32 byte line size\n");
			break;
		case 0x83:
			printf("2nd-level cache: 512 KByte, 8-way set associative, 32 byte line size\n");
			break;
		case 0x84:
			printf("2nd-level cache: 1 MByte, 8-way set associative, 32 byte line size\n");
			break;
		case 0x85:
			printf("2nd-level cache: 2 MByte, 8-way set associative, 32 byte line size\n");
			break;
		case 0x86:
			printf("2nd-level cache: 512 KByte, 4-way set associative, 64 byte line size\n");
			break;
		case 0x87:
			printf("2nd-level cache: 1 MByte, 8-way set associative, 64 byte line size\n");
			break;
		case 0xA0:
			printf("DTLB: 4k pages, fully associative, 32 entries\n");
			break;
		case 0xB0:
			printf("Instruction TLB: 4 KByte pages, 4-way set associative, 128 entries\n");
			break;
		case 0xB1:
			printf("Instruction TLB: 2M pages, 4-way, 8 entries or 4M pages, 4-way, 4 entries\n");
			break;
		case 0xB2:
			printf("Instruction TLB: 4KByte pages, 4-way set associative, 64 entries\n");
			break;
		case 0xB3:
			printf("Data TLB: 4 KByte pages, 4-way set associative, 128 entries\n");
			break;
		case 0xB4:
			printf("Data TLB1: 4 KByte pages, 4-way associative, 256 entries\n");
			break;
		case 0xB5:
			printf("Instruction TLB: 4KByte pages, 8-way set associative, 64 entries\n");
			break;
		case 0xB6:
			printf("Instruction TLB: 4KByte pages, 8-way set associative, 128 entries\n");
			break;
		case 0xBA:
			printf("Data TLB1: 4 KByte pages, 4-way associative, 64 entries\n");
			break;
		case 0xC0:
			printf("Data TLB: 4 KByte and 4 MByte pages, 4-way associative, 8 entries\n");
			break;
		case 0xC1:
			printf("Shared 2nd-Level TLB: 4 KByte/2MByte pages, 8-way associative, 1024 entries\n");
			break;
		case 0xC2:
			printf("DTLB: 4 KByte/2 MByte pages, 4-way associative, 16 entries\n");
			break;
		case 0xC3:
			printf("Shared 2nd-Level TLB: 4 KByte /2 MByte pages, 6-way associative, 1536 entries. Also 1GBbyte pages, 4-way, 16 entries\n");
			break;
		case 0xC4:
			printf("DTLB: 2M/4M Byte pages, 4-way associative, 32 entries\n");
			break;
		case 0xCA:
			printf("Shared 2nd-Level TLB: 4 KByte pages, 4-way associative, 512 entries\n");
			break;
		case 0xD0:
			printf("3rd-level cache: 512 KByte, 4-way set associative, 64 byte line size\n");
			break;
		case 0xD1:
			printf("3rd-level cache: 1 MByte, 4-way set associative, 64 byte line size\n");
			break;
		case 0xD2:
			printf("3rd-level cache: 2 MByte, 4-way set associative, 64 byte line size\n");
			break;
		case 0xD6:
			printf("3rd-level cache: 1 MByte, 8-way set associative, 64 byte line size\n");
			break;
		case 0xD7:
			printf("3rd-level cache: 2 MByte, 8-way set associative, 64 byte line size\n");
			break;
		case 0xD8:
			printf("3rd-level cache: 4 MByte, 8-way set associative, 64 byte line size\n");
			break;
		case 0xDC:
			printf("3rd-level cache: 1.5 MByte, 12-way set associative, 64 byte line size\n");
			break;
		case 0xDD:
			printf("3rd-level cache: 3 MByte, 12-way set associative, 64 byte line size\n");
			break;
		case 0xDE:
			printf("3rd-level cache: 6 MByte, 12-way set associative, 64 byte line size\n");
			break;
		case 0xE2:
			printf("3rd-level cache: 2 MByte, 16-way set associative, 64 byte line size\n");
			break;
		case 0xE3:
			printf("3rd-level cache: 4 MByte, 16-way set associative, 64 byte line size\n");
			break;
		case 0xE4:
			printf("3rd-level cache: 8 MByte, 16-way set associative, 64 byte line size\n");
			break;
		case 0xEA:
			printf("3rd-level cache: 12MByte, 24-way set associative, 64 byte line size\n");
			break;
		case 0xEB:
			printf("3rd-level cache: 18MByte, 24-way set associative, 64 byte line size\n");
			break;
		case 0xEC:
			printf("3rd-level cache: 24MByte, 24-way set associative, 64 byte line size\n");
			break;
		case 0xF0:
			printf("64-Byte prefetching\n");
			break;
		case 0xF1:
			printf("128-Byte prefetching\n");
			break;
		case 0xFF:
			printf("CPUID leaf 2 does not report cache descriptor information, use CPUID leaf 4 to query cache parameters\n");
			break;
		default:
			break;
	}
}

void func_tlb_info()
{
	unsigned int eax, ebx, ecx, edx;
	
	eax = 0x02;
	
	__asm__ __volatile__(
		"cpuid;"
		: "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
		: "a"(eax)
	);
	
	func_check_tlb((eax & 0xFF000000) >> 24);
	func_check_tlb((eax & 0xFF0000) >> 16);
	func_check_tlb((eax & 0xFF00) >> 8);
	func_check_tlb(eax & 0xFF);	

	func_check_tlb((ebx & 0xFF000000) >> 24);
	func_check_tlb((ebx & 0xFF0000) >> 16);
	func_check_tlb((ebx & 0xFF00) >> 8);
	func_check_tlb(ebx & 0xFF);	

	func_check_tlb((ecx & 0xFF000000) >> 24);
	func_check_tlb((ecx & 0xFF0000) >> 16);
	func_check_tlb((ecx & 0xFF00) >> 8);
	func_check_tlb(ecx & 0xFF);	

	func_check_tlb((edx & 0xFF000000) >> 24);
	func_check_tlb((edx & 0xFF0000) >> 16);
	func_check_tlb((edx & 0xFF00) >> 8);
	func_check_tlb(edx & 0xFF);
}

void func_mem_info()
{
	unsigned int eax, ebx, ecx, edx;
	unsigned int way, partition, set, line, size, ksize, msize;
	unsigned int array[] = {0x01, 0x02, 0x03}, i;
	
	for(i = 0; i < sizeof(array) / sizeof(int); i ++)
	{
		eax = 0x04;
		ecx = array[i];
			
		__asm__ __volatile__(
			"cpuid;"
			: "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
			: "a"(eax), "c"(ecx)
		);
		
		way = (ebx & 0xFFF00000) >> 22;
		partition = (ebx & 0x3FF000) >> 12;
		line = ebx & 0xFFF;
		set = ecx;	
		size = (way + 1) * (partition + 1) * (line + 1) * (set + 1);
		ksize = size / 1024;
		msize = size / (1024 * 1024);

		printf("L%d Cache Size: %d(Bytes)/%d(%s)\n", i + 1, size, (size >= 10000 && size <= 999999) ? ksize : msize, (size >= 10000 && size <= 999999) ? "KB" : "MB");
	}
}

void func_addr_info()
{
	unsigned int eax, ebx, ecx, edx;
	
	eax = 0x80000008;
	
	__asm__ __volatile__(
		"cpuid;"
		: "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
		: "a"(eax)
	);
	
	printf("Physical Address Width: %d\n", eax & 0xFF);
	printf("Logical Address Width: %d\n", (eax & 0xFF00) >> 8);
}

void func_number_info()
{
	unsigned int eax, ebx, ecx, edx;
	unsigned int num, type, i;

	for(i = 0; ; i ++) 
	{
		eax = 0x0B;
		ecx = i;
		
		__asm__ __volatile__(
			"cpuid;"
			: "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
			: "a"(eax), "c"(ecx)
		);
		
		type = (ecx & 0xFF00) >> 8;
		
		if(type == 0) 
		{
			break;
		}
		
		num = ebx & 0xFFFF;
	}
	
	printf("Number of Core: %d\n", num);
	printf("Number of Logical Processor: %d\n", num * 2);
}

void func_family_info()
{
	unsigned int eax, ebx, ecx, edx;
	unsigned int id, eid;
	
	eax = 0x01;

	__asm__ __volatile__(
		"cpuid;"
		: "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
		: "a"(eax)
	);
	
	id = (eax & 0xF00) >> 8;
	eid = (eax & 0xFF00000) >> 20;
	
	printf("Family: %d\n", (id != 0x0F) ? id : id + eid);
}

void func_model_info()
{
	unsigned int eax, ebx, ecx, edx;
	unsigned int family, id, eid;
	
	eax = 0x01;

	__asm__ __volatile__(
		"cpuid;"
		: "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
		: "a"(eax)
	);
	
	family = (eax & 0xF00) >> 8;
	id = (eax & 0xF0) >> 4;
	eid = ((0xF0000 & eax) >> 16) << 4;
	
	printf("Model ID: %d\n", (family == 0x06 || family == 0x0F) ? id + eid : id);
}

void func_name_info() 
{
	unsigned int eax, ebx, ecx, edx;

	char model[64];
	memset(model, 0, 64);
	
	eax = 0x80000002;
	
	__asm__ __volatile__(
		"cpuid;"
		: "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
		: "a"(eax)
	);
	
	memcpy(model, (char *)&eax, 4);
	memcpy(model + 4, (char *)&ebx, 4);
	memcpy(model + 8, (char *)&ecx, 4);
	memcpy(model + 12, (char *)&edx, 4);
	
	eax = 0x80000003;
	
	__asm__ __volatile__(
		"cpuid;"
		: "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
		: "a"(eax)
	);
	
	memcpy(model + 16, (char *)&eax, 4);
	memcpy(model + 20, (char *)&ebx, 4);
	memcpy(model + 24, (char *)&ecx, 4);
	memcpy(model + 28, (char *)&edx, 4);
	
	eax = 0x80000004;
	
	__asm__ __volatile__(
		"cpuid;"
		: "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
		: "a"(eax)
	);
	
	memcpy(model + 32, (char *)&eax, 4);
	memcpy(model + 36, (char *)&ebx, 4);
	memcpy(model + 40, (char *)&ecx, 4);
	memcpy(model + 44, (char *)&edx, 4);
	model[45] = 0;

	printf("Model Name: %s\n", model);
}

void func_frequency_info()
{
	unsigned long int eax, ebx, ecx, edx;
	float proc_base_freq, max_freq, bus_freq;
	
	eax = 0x16;
	
	__asm__ __volatile__(
		"cpuid;"
		: "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
		: "a"(eax)
	);
	
	proc_base_freq = (double)(eax & 0xFFFF);
	max_freq = (double)(ebx & 0xFFFF); 
	bus_freq = (double)(ecx & 0xFFFF);

	if(proc_base_freq == 0)
	{
		printf("Processor Base Frequency: Not Supported\n");
	}
	else
	{
		printf("Processor Base Frequency: %.2f(MHz)\n", proc_base_freq);
	}

	if(max_freq == 0)
	{
		printf("Maximum Frequency: Not Supported\n");
	}
	else
	{
		printf("Maximum Frequency: %.2f(MHz)\n", max_freq);
	}

	if(bus_freq == 0)
	{
		printf("Bus Frequency: Not Supported\n");
	}
	else
	{
		printf("Bus Frequency: %.2f(MHz)\n", bus_freq);
	}
}

void func_feature_info()
{
	unsigned int eax, ebx, ecx, edx;
	
	eax = 0x01;
	
	__asm__ __volatile__(
		"cpuid;"
		: "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx)
		: "a"(eax)
	);
	
	printf("SSE3: %s\n", ((ecx & 0x01) == 1) ? "true" : "false");
	printf("PCLMULQDQ: %s\n", (((ecx & 0x02) >> 1) == 1) ? "true" : "false");
	printf("DTES64: %s\n", (((ecx & 0x04) >> 2) == 1) ? "true" : "false");
	printf("MONITOR: %s\n", (((ecx & 0x08) >> 3) == 1) ? "true" : "false");

	printf("DS-CPL: %s\n", (((ecx & 0x10) >> 4) == 1) ? "true" : "false");
	printf("VMX: %s\n", (((ecx & 0x20) >> 5) == 1) ? "true" : "false");
	printf("SMX: %s\n", (((ecx & 0x40) >> 6) == 1) ? "true" : "false");
	printf("EIST: %s\n", (((ecx & 0x80) >> 7) == 1) ? "true" : "false");

	printf("TM2: %s\n", (((ecx & 0x100) >> 8) == 1) ? "true" : "false");
	printf("SSSE3: %s\n", (((ecx & 0x200) >> 9) == 1) ? "true" : "false");
	printf("CNXT-ID: %s\n", (((ecx & 0x400) >> 10) == 1) ? "true" : "false");
	printf("SDBG: %s\n", (((ecx & 0x800) >> 11) == 1) ? "true" : "false");

	printf("FMA: %s\n", (((ecx & 0x1000) >> 12) == 1) ? "true" : "false");
	printf("CMPXCHG16B: %s\n", (((ecx & 0x2000) >> 13) == 1) ? "true" : "false");
	printf("xTPR Update Control: %s\n", (((ecx & 0x4000) >> 14) == 1) ? "true" : "false");
	printf("PDCM: %s\n", (((ecx & 0x8000) >> 15) == 1) ? "true" : "false");

	printf("PCID: %s\n", (((ecx & 0x20000) >> 17) == 1) ? "true" : "false");
	printf("DCA: %s\n", (((ecx & 0x40000) >> 18) == 1) ? "true" : "false");
	printf("SSE 4.1: %s\n", (((ecx & 0x80000) >> 19) == 1) ? "true" : "false");
	
	printf("SSE 4.2: %s\n", (((ecx & 0x100000) >> 20) == 1) ? "true" : "false");
	printf("x2APIC: %s\n", (((ecx & 0x200000) >> 21) == 1) ? "true" : "false");
	printf("MOVBE: %s\n", (((ecx & 0x400000) >> 22) == 1) ? "true" : "false");
	printf("POPCNT: %s\n", (((ecx & 0x800000) >> 23) == 1) ? "true" : "false");
	
	printf("TSC-Deadline: %s\n", (((ecx & 0x1000000) >> 24) == 1) ? "true" : "false");
	printf("AESNI: %s\n", (((ecx & 0x2000000) >> 25) == 1) ? "true" : "false");
	printf("XSAVE: %s\n", (((ecx & 0x4000000) >> 26) == 1) ? "true" : "false");
	printf("OSXSAVE: %s\n", (((ecx & 0x8000000) >> 27) == 1) ? "true" : "false");
	
	printf("AVX: %s\n", (((ecx & 0x10000000) >> 28) == 1) ? "true" : "false");
	printf("F16C: %s\n", (((ecx & 0x20000000) >> 29) == 1) ? "true" : "false");
	printf("RDRAND: %s\n", (((ecx & 0x40000000) >> 30) == 1) ? "true" : "false");
	/************************************************************************/
	printf("FPU: %s\n", ((edx & 0x01) == 1) ? "true" : "false");
	printf("VME: %s\n", (((edx & 0x02) >> 1) == 1) ? "true" : "false");
	printf("DE: %s\n", (((edx & 0x04) >> 2) == 1) ? " true" : "false");
	printf("PSE: %s\n", (((edx & 0x08) >> 3) == 1) ? "true" : "false");
	
	printf("TSC: %s\n", (((edx & 0x10) >> 4) == 1) ? "true" : "false");
	printf("MSR: %s\n", (((edx & 0x20) >> 5) == 1) ? "true" : "false");
	printf("PAE: %s\n", (((edx & 0x40) >> 6) == 1) ? "true" : "false");
	printf("MCE: %s\n", (((edx & 0x80) >> 7) == 1) ? "true" : "false");
	
	printf("CX8: %s\n", (((edx & 0x100) >> 8) == 1) ? "true" : "false");
	printf("APIC: %s\n", (((edx & 0x200) >> 9) == 1) ? "true" : "false");
	printf("SEP: %s\n", (((edx & 0x800) >> 11) == 1) ? "true" : "false");
	
	printf("MTRR: %s\n", (((edx & 0x1000) >> 12) == 1) ? "true" : "false");
	printf("PGE: %s\n", (((edx & 0x2000) >> 13) == 1) ? "true" : "false");
	printf("MCA: %s\n", (((edx & 0x4000) >> 14) == 1) ? "true" : "false");
	printf("CMOV: %s\n", (((edx & 0x8000) >> 15) == 1) ? "true" : "false");
	
	printf("PAT: %s\n", (((edx & 0x10000) >> 16) == 1) ? "true" : "false");
	printf("PSE-36: %s\n", (((edx & 0x20000) >> 17) == 1) ? "true" : "false");
	printf("PSN: %s\n", (((edx & 0x40000) >> 18) == 1) ? "true" : "false");
	printf("CLFLUSH: %s\n", (((edx & 0x80000) >> 19) == 1) ? "true" : "false");
	
	printf("DS: %s\n", (((edx & 0x100000) >> 21) == 1) ? "true" : "false");
	printf("ACPI: %s\n", (((edx & 0x200000) >> 22) == 1) ? "true" : "false");
	printf("MMX: %s\n", (((edx & 0x400000) >> 23) == 1) ? "true" : "false");
	
	printf("FXSR: %s\n", (((edx & 0x1000000) >> 24) == 1) ? "true" : "false");
	printf("SSE %s\n", (((edx & 0x2000000) >> 25) == 1) ? "true" : "false");
	printf("SSE 2: %s\n", (((edx & 0x4000000) >> 26) == 1) ? "true" : "false");
	printf("SS: %s\n", (((edx & 0x8000000) >> 27) == 1) ? "true" : "false");
	
	printf("HTT: %s\n", (((edx & 0x10000000) >> 28) == 1) ? "true" : "false");
	printf("TM: %s\n", (((edx & 0x20000000) >> 29) == 1) ? "true" : "false");
	printf("PBE: %s\n", (((edx & 0x80000000) >> 31) == 1) ? "true" : "false");
}
