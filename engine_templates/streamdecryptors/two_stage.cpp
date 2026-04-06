/* Decryptor Level 4: Two-stage decryption */
   
// Stage 1: Simple XOR
for (size_t i = 0; i < size; i++) {
    data[i] ^= 0x7F;
}

// Stage 2: Position-based XOR
for (size_t i = 0; i < size; i++) {
    data[i] ^= (i & 0xFF);
}

printf("[CUSTOM DECRYPTOR] Two-stage decryption applied to %zu bytes\n", size);
