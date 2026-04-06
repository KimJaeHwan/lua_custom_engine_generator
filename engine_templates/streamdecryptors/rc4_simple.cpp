
/* Stream Decryptor Level 3: RC4-like */
uint8_t stream_rc4_S[256];
for (int i = 0; i < 256; i++) stream_rc4_S[i] = i;
uint8_t stream_rc4_j = 0;
uint8_t stream_rc4_key[8] = {0x12,0x34,0x56,0x78,0x9A,0xBC,0xDE,0xF0};
for (int i = 0; i < 256; i++) {
    stream_rc4_j = (stream_rc4_j + stream_rc4_S[i] + stream_rc4_key[i%8]) & 255;
    uint8_t t = stream_rc4_S[i]; stream_rc4_S[i] = stream_rc4_S[stream_rc4_j]; stream_rc4_S[stream_rc4_j] = t;
}
uint8_t stream_rc4_i = 0; stream_rc4_j = 0;
for (size_t k = 0; k < size; k++) {
    stream_rc4_i = (stream_rc4_i + 1) & 255;
    stream_rc4_j = (stream_rc4_j + stream_rc4_S[stream_rc4_i]) & 255;
    uint8_t t = stream_rc4_S[stream_rc4_i]; stream_rc4_S[stream_rc4_i] = stream_rc4_S[stream_rc4_j]; stream_rc4_S[stream_rc4_j] = t;
    data[k] ^= stream_rc4_S[(stream_rc4_S[stream_rc4_i] + stream_rc4_S[stream_rc4_j]) & 255];
}