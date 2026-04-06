// 원본 OpCode 값 백업 (기존 코드 호환성 유지)
#define OP_ORIG_MOVE        OP_MOVE
#define OP_ORIG_LOADK       OP_LOADK
#define OP_ORIG_GETUPVAL    OP_GETUPVAL
#define OP_ORIG_CLOSURE     OP_CLOSURE
#define OP_ORIG_SETLIST     OP_SETLIST
#define OP_ORIG_VARARG      OP_VARARG
#define OP_ORIG_VARARGPREP  OP_VARARGPREP
#define OP_ORIG_EXTRAARG    OP_EXTRAARG


// Level 3: 테이블 기반 완전 재정의
    static const uint8_t remap_custom_lua_table[32] = {
        7, 12, 3, 27, 8, 19, 31, 0, 15, 22, 9, 4, 25, 11, 6, 28,
        14, 21, 2, 17, 10, 5, 30, 13, 20, 1, 26, 16, 29, 24, 18, 23
    };

#undef OP_MOVE
#undef OP_LOADK
#undef OP_GETUPVAL
#undef OP_CLOSURE
#undef OP_SETLIST
#undef OP_VARARG
#undef OP_VARARGPREP
#undef OP_EXTRAARG

#define OP_MOVE         ((OpCode)remap_custom_lua_table[OP_ORIG_MOVE])
#define OP_LOADK        ((OpCode)remap_custom_lua_table[OP_ORIG_LOADK])
#define OP_GETUPVAL     ((OpCode)remap_custom_lua_table[OP_ORIG_GETUPVAL])
#define OP_CLOSURE      ((OpCode)remap_custom_lua_table[OP_ORIG_CLOSURE])
#define OP_SETLIST      ((OpCode)remap_custom_lua_table[OP_ORIG_SETLIST])
#define OP_VARARG       ((OpCode)remap_custom_lua_table[OP_ORIG_VARARG])
#define OP_VARARGPREP   ((OpCode)remap_custom_lua_table[OP_ORIG_VARARGPREP])
#define OP_EXTRAARG     ((OpCode)remap_custom_lua_table[OP_ORIG_EXTRAARG])