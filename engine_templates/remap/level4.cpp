// 원본 OpCode 값 백업 (기존 코드 호환성 유지)
#define OP_ORIG_MOVE        OP_MOVE
#define OP_ORIG_LOADK       OP_LOADK
#define OP_ORIG_GETUPVAL    OP_GETUPVAL
#define OP_ORIG_CLOSURE     OP_CLOSURE
#define OP_ORIG_SETLIST     OP_SETLIST
#define OP_ORIG_VARARG      OP_VARARG
#define OP_ORIG_VARARGPREP  OP_VARARGPREP
#define OP_ORIG_EXTRAARG    OP_EXTRAARG

// Level 2: XOR 기반 값 재정의
#undef OP_MOVE
#undef OP_LOADK
#undef OP_GETUPVAL
#undef OP_CLOSURE
#undef OP_SETLIST
#undef OP_VARARG
#undef OP_VARARGPREP
#undef OP_EXTRAARG

#define OP_MOVE         (OP_ORIG_MOVE ^ 0x55)
#define OP_LOADK        (OP_ORIG_LOADK ^ 0x55)
#define OP_GETUPVAL     (OP_ORIG_GETUPVAL ^ 0x55)
#define OP_CLOSURE      (OP_ORIG_CLOSURE ^ 0x55)
#define OP_SETLIST      (OP_ORIG_SETLIST ^ 0x55)
#define OP_VARARG       (OP_ORIG_VARARG ^ 0x55)
#define OP_VARARGPREP   (OP_ORIG_VARARGPREP ^ 0x55)
#define OP_EXTRAARG     (OP_ORIG_EXTRAARG ^ 0x55)