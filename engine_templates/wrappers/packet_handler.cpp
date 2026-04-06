static int custom_function(lua_State *L) {
    /* Packet Handler Wrapper - opcode 처리 시뮬레이션 */
    int opcode = luaL_checkinteger(L, 1);
    int data_len = luaL_optinteger(L, 2, 0);

    printf("[CUSTOM WRAPPER] packet_handler executed (opcode=0x%X, data_len=%d)\n", 
           opcode, data_len);

    lua_pushboolean(L, (opcode > 0 && opcode < 0x100));  // 간단한 유효성 체크
    return 1;
}