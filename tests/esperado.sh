# shellcheck shell=bash
# O que os testes esperam desta imagem (lido por tests/teste.sh).
# shellcheck disable=SC2034
NOME_PADRAO="TF2 MGE Server"
PLUGINS=(
    "Admin File Reader"
    "Basic Commands"
    "MGE"
)
COMANDOS=(
    "mge:add"
    "mge:remove"
    "mge:top5"
    "mge:rank"
    "mge:mgehelp"
)
# cvars que a imagem tem que ligar com estes valores
CVARS=(
    "tf_weapon_criticals:0"
    "sv_maxupdaterate:100"
    "mp_timelimit:0"
)
ARENAS=18
TICK=100
