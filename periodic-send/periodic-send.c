#include "pico/stdlib.h"
#include "hardware/gpio.h"

#define LED_PIN 25

int main() {
   gpio_init(LED_PIN);
   gpio_set_dir(LED_PIN, GPIO_OUT);

   while (true) {
      gpio_xor_mask(1u << LED_PIN); // toggle
      sleep_ms(500);
   }
}
