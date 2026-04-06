// decryptors/xor_single.cpp
void custom_decrypt_block(void *b, size_t size) {
    uint8_t *data = (uint8_t *)b;
    uint8_t decrypt_key = 0xA5;
    for (size_t i = 0; i < size; i++) {
        data[i] ^= decrypt_key;
    }
}