/* Decryptor Level 4: Two-stage decryption */
void custom_decrypt_block(void *b, size_t size) {
    uint8_t *data = (uint8_t *)b;
    
    // Stage 1: Simple XOR
    for (size_t i = 0; i < size; i++) {
        data[i] ^= 0x7F;
    }
    
    // Stage 2: Position-based XOR
    for (size_t i = 0; i < size; i++) {
        data[i] ^= (i & 0xFF);
    }
    
    printf("[CUSTOM DECRYPTOR] Two-stage decryption applied to %zu bytes\n", size);
}