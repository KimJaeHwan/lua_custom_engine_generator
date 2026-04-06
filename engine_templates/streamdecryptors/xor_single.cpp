/* Stream Decryptor Level 1: Single XOR */
uint8_t stream_xor_key = 0xA5;
for (size_t i = 0; i < size; i++) data[i] ^= stream_xor_key;