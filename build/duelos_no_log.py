import sys
# SKYNET: o MGEMod passa a escrever no log do jogo cada vitoria e derrota de duelo (o ranking HLstatsZ le daqui)
f = sys.argv[1]
s = open(f, encoding="utf-8").read()
FUNC = '''// SKYNET: registra vitoria/derrota do duelo no log do jogo para o ranking HLstatsZ (mge_win +5, mge_loss -2)
void SkynetLogDuel(int client, const char[] acao)
{
    if (!IsValidClient(client) || IsFakeClient(client))
        return;
    char auth[32], team[16];
    if (!GetClientAuthId(client, AuthId_Steam3, auth, sizeof(auth)))
        return;
    GetTeamName(GetClientTeam(client), team, sizeof(team));
    LogToGame("\\"%N<%d><%s><%s>\\" triggered \\"%s\\"", client, GetClientUserId(client), auth, team, acao);
}

'''
A1 = ("void CalcELO(int winner, int loser)\n{\n"
      "    if (IsFakeClient(winner) || IsFakeClient(loser) || g_bNoStats)\n        return;\n")
A2 = ("void CalcELO2(int winner, int winner2, int loser, int loser2)\n{\n"
      "    if (IsFakeClient(winner) || IsFakeClient(loser) || g_bNoStats || IsFakeClient(loser2) || IsFakeClient(winner2))\n"
      "        return;\n")
A3 = "// ====[ STATS ]====================================================\n"
for a in (A1, A2, A3):
    if s.count(a) != 1:
        sys.exit("ERRO: ponto de encaixe do MGEMod nao encontrado (%r)" % a[:40])
s = s.replace(A3, FUNC + A3)
s = s.replace(A1, A1 + '\n    SkynetLogDuel(winner, "mge_win");\n    SkynetLogDuel(loser, "mge_loss");\n')
s = s.replace(A2, A2 + '\n    SkynetLogDuel(winner, "mge_win");\n    SkynetLogDuel(winner2, "mge_win");\n'
                       '    SkynetLogDuel(loser, "mge_loss");\n    SkynetLogDuel(loser2, "mge_loss");\n')
open(f, "w", encoding="utf-8").write(s)
print("MGEMod: vitorias e derrotas vao para o log do ranking")
