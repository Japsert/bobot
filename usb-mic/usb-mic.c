#include "pico/stdlib.h"
#include <hardware/gpio.h>
#include <hardware/pio.h>
#include <hardware/timer.h>
#include <hardware/uart.h>
#include <math.h>
#include <pico/stdio.h>
#include <pico/time.h>
#include <pico/types.h>
#include <stdint.h>
#include <stdio.h>

// Assembled PIO program
#include "usb-mic.pio.h"

#define USBMIC_SD_PIN 27
#define USBMIC_WS_PIN 28
#define USBMIC_SCK_PIN 29

int32_t sign_extend(uint32_t value) {
   uint32_t sign = UINT32_C(1) << (24 - 1);
   return (int32_t)((value & 0x00ffffff) ^ sign) - (int32_t)sign;
}

int main() {
   // Output to Mac over UART
   stdio_init_all();

   PIO pio;
   uint sm;
   uint offset;

   setup_default_uart();

   // Find free PIO & state machine, and load program
   bool ok = pio_claim_free_sm_and_add_program(&usbmic_program, &pio, &sm, &offset);
   hard_assert(ok);

   usbmic_program_init(pio, sm, offset, USBMIC_SD_PIN, USBMIC_WS_PIN, USBMIC_SCK_PIN);

   // State machine now running
   printf("State machine running!\n");

   for (int i = 5; i >= 0; i--) {
      sleep_ms(1000);
   }

   uint32_t words[16000];
   for (int sec = 0; sec < 3; sec++) {
      for (int i = 0; i < 16000; i++)
         words[i] = pio_sm_get_blocking(pio, sm);
      for (int i = 0; i < 16000; i++) {
         printf("%d\n", sign_extend(words[i]));
         sleep_us(100);
      }
   }

   while (true)
      ;

   // Free and unload
   pio_remove_program_and_unclaim_sm(&usbmic_program, pio, sm, offset);
}
