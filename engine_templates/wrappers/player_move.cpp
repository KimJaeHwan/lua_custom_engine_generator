static int custom_function(lua_State *L) {
    /* Player Move Wrapper - 간단한 위치 계산 로직 */
    double x = luaL_checknumber(L, 1);
    double y = luaL_checknumber(L, 2);
    double speed = luaL_optnumber(L, 3, 1.0);

    double new_x = x + speed * 0.7;
    double new_y = y + speed * 1.3;

    lua_pushnumber(L, new_x);
    lua_pushnumber(L, new_y);
    printf("[CUSTOM WRAPPER] player_move executed (%.2f, %.2f) -> (%.2f, %.2f)\n", 
           x, y, new_x, new_y);
    return 2;   // 반환값 2개 (new_x, new_y)
}