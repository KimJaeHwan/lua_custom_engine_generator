/*
** $Id: lzio.c,v 1.37.1.1 2017/04/19 17:20:42 roberto Exp $
** Buffered streams
** See Copyright Notice in lua.h
*/

#define lzio_c
#define LUA_CORE

#include "lprefix.h"


#include <string.h>

#include "lua.h"

#include "llimits.h"
#include "lmem.h"
#include "lstate.h"
#include "lzio.h"


// {{DEFINE_CUSTOM_INLINE_1}}

int luaZ_fill (ZIO *z) {
  size_t size;
  lua_State *L = z->L;
  const char *buff;
  lua_unlock(L);
  buff = z->reader(L, z->data, &size);
  lua_lock(L);
  if (buff == NULL || size == 0)
    return EOZ;
  
    #if defined(LUA_CUSTOM_INLINE)
  char* data = buff;
  // {{CUSTOM_DECRYPTOR_CODE_1_STREAM}}
  #else
  custom_decrypt_block(buff,size);
  #endif
  // {{CUSTOM_DUMMY_CODE_1}}
  
  z->n = size - 1;  /* discount char being returned */
  z->p = buff;
  return cast_uchar(*(z->p++));
}


void luaZ_init (lua_State *L, ZIO *z, lua_Reader reader, void *data) {
  z->L = L;
  z->reader = reader;
  z->data = data;
  z->n = 0;
  z->p = NULL;
}


/* --------------------------------------------------------------- read --- */
size_t luaZ_read (ZIO *z, void *b, size_t n) {
  size_t size = n;
  char * data = b;
  while (n) {
    size_t m;
    if (z->n == 0) {  /* no bytes in buffer? */
      if (luaZ_fill(z) == EOZ)  /* try to read more */
        return n;  /* no more input; return number of missing bytes */
      else {
        z->n++;  /* luaZ_fill consumed first byte; put it back */
        z->p--;
      }
    }
    m = (n <= z->n) ? n : z->n;  /* min. between n and z->n */
    memcpy(b, z->p, m);
    z->n -= m;
    z->p += m;
    b = (char *)b + m;
    n -= m;
  }
  #if defined(LUA_CUSTOM_INLINE)
  // {{CUSTOM_DECRYPTOR_CODE_2_STREAM}}
  #else
  custom_decrypt_block(data,size);
  #endif
  // {{CUSTOM_DUMMY_CODE_2}}
  return 0;
}

