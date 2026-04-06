// Dummy Level 3: 상당히 무거운 dummy 코드 (변수 충돌 방지 버전)
volatile int dummy_junk_a = 1;
volatile int dummy_junk_b = 2;
volatile int dummy_junk_c = 3;
volatile int dummy_junk_d = 0xDEADBEEF;
volatile float dummy_junk_f = 123.456f;

for (int dummy_junk_i = 0; dummy_junk_i < 120; dummy_junk_i++) {
    dummy_junk_a = (dummy_junk_a * dummy_junk_b + dummy_junk_c) ^ dummy_junk_d;
    dummy_junk_b = dummy_junk_b * 3 + dummy_junk_i;
    dummy_junk_c = (dummy_junk_c << 2) | (dummy_junk_a & 0xFF);
    if ((dummy_junk_i % 17) == 0) {
        dummy_junk_d = ~dummy_junk_d;
    }
}

for (int dummy_junk_i = 0; dummy_junk_i < 40; dummy_junk_i++) {
    dummy_junk_f = dummy_junk_f * 1.17f - 4.2f;
}