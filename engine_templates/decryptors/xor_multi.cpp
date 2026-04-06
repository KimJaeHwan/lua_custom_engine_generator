// decryptors/xor_multi.cpp
void custom_decrypt_block(void *b, size_t size) {
    uint8_t *data = (uint8_t *)b;
    const uint8_t decrypt_key[8] = {0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0};
    for (size_t i = 0; i < size; i++) {
        data[i] ^= decrypt_key[i % 8];
    }
}