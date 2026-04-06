// Dummy Level 2: 반복문 + 간단 연산
volatile int dummy_var1 = 123;
volatile int dummy_var2 = 456;
for (int i = 0; i < 30; i++) {
    dummy_var1 += i * 7;
    dummy_var2 ^= dummy_var1;
}