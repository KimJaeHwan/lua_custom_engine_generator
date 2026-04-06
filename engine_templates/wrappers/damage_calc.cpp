static int custom_function(lua_State *L) {
    /* Damage Calculation Wrapper - 간단한 데미지 계산 */
    double atk = luaL_checknumber(L, 1);
    double def = luaL_checknumber(L, 2);
    double skill_factor = luaL_optnumber(L, 3, 1.0);

    double damage = (atk * 1.5 - def * 0.8) * skill_factor;
    if (damage < 1.0) damage = 1.0;

    lua_pushnumber(L, damage);
    printf("[CUSTOM WRAPPER] damage_calc executed (atk=%.1f, def=%.1f) -> damage=%.1f\n", 
           atk, def, damage);
    return 1;   // 반환값 1개
}
