#define __NV_MODULE_ID _13_MainC_cpp1_ii_debugFN
#define __NV_CUBIN_HANDLE_STORAGE__ extern
#include "crt/host_runtime.h"
#include "MainC.fatbin.c"
static void __nv_cudaEntityRegisterCallback(void **);
static void __sti____cudaRegisterAll_13_MainC_cpp1_ii_debugFN(void);
#pragma section(".CRT$XCU",read,write)
__declspec(allocate(".CRT$XCU"))static void (*__dummy_static_init__sti____cudaRegisterAll_13_MainC_cpp1_ii_debugFN[])(void) = {__sti____cudaRegisterAll_13_MainC_cpp1_ii_debugFN};
static void __nv_cudaEntityRegisterCallback(void **__T20){__nv_dummy_param_ref(__T20);__nv_save_fatbinhandle_for_managed_rt(__T20);}
static void __sti____cudaRegisterAll_13_MainC_cpp1_ii_debugFN(void){____cudaRegisterLinkedBinary(__nv_cudaEntityRegisterCallback);}