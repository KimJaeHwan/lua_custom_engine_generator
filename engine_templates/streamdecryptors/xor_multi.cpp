/* Stream Decryptor Level 2: Multi XOR */
const uint8_t stream_multi_key[8] = {0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0};
for (size_t i = 0; i < size; i++) data[i] ^= stream_multi_key[i % 8];