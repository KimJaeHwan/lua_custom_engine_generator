// decryptors/rc4_simple.cpp
void custom_decrypt_block(void *b, size_t size) {
    uint8_t *data = (uint8_t *)b;
    uint8_t S[256];
    for (int i = 0; i < 256; i++) S[i] = i;
    uint8_t j = 0;
    uint8_t k[8] = {0x12,0x34,0x56,0x78,0x9A,0xBC,0xDE,0xF0};
    for (int i = 0; i < 256; i++) {
        j = (j + S[i] + k[i%8]) & 255;
        uint8_t t = S[i]; S[i] = S[j]; S[j] = t;
    }
    uint8_t i = 0; j = 0;
    for (size_t k = 0; k < size; k++) {
        i = (i+1)&255; j = (j + S[i])&255;
        uint8_t t = S[i]; S[i] = S[j]; S[j] = t;
        data[k] ^= S[(S[i]+S[j])&255];
    }
}