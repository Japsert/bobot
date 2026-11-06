#include "pico/stdlib.h"
#include <stdio.h>

int main() {
   stdio_init_all();

   int i = 0;
   while (true) {
      printf("Hi! This is message %d.\n", i++);
      sleep_ms(500);
   }
}
