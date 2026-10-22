import re
import sys
# SKYNET: MGEMod em portugues e sem as mensagens de resultado de duelo, de boas-vindas e de vida restante.
#   uso: python3 mge_pt.py <mge.sp> <mgemod.phrases.txt original> <saida.phrases.txt>
sp, frases_orig, frases_saida = sys.argv[1:4]

# ---------------------------------------------------------------- 1. mensagens que saem do chat
s = open(sp, encoding="utf-8").read()
tirar = re.compile(r'MC_PrintToChat(All)?\((client, |victim, )?"%t", "(XdefeatsY|XdefeatsYearly|HPLeft|Welcome1|Welcome2|Welcome3)"[^;]*\);')
s, n = tirar.subn("{} // SKYNET: mensagem removida", s)
if n != 13:
    sys.exit("ERRO: esperava 13 mensagens para remover, achei %d" % n)

# ---------------------------------------------------------------- 2. textos fixos do plugin em portugues
TEXTOS = [
    ('"[MGEMod] Plugin reloaded. Slaying all players to avoid bugs."', '"[MGE] Plugin recarregado. Todos os jogadores foram mortos para evitar bugs."', 1),
    ('"You have the intel!"', '"Você está com a bola!"', 2),
    ('"Arena %s. Capture Limit(%d)"', '"Arena %s. Limite de capturas: %d"', 1),
    ('"Arena %s. No Capture Limit"', '"Arena %s. Sem limite de capturas"', 1),
    ('"Arena %s. Frag Limit(%d)"', '"Arena %s. Limite de frags: %d"', 2),
    ('"Arena %s. No Frag Limit"', '"Arena %s. Sem limite de frags"', 2),
    ('"Your team already has that class!"', '"Seu time já tem essa classe!"', 3),
    ('"Would you like to swap classes with your teammate?"', '"Quer trocar de classe com o seu parceiro?"', 1),
    ('menu.AddItem("yes", "Yes");', 'menu.AddItem("yes", "Sim");', 1),
    ('menu.AddItem("no", "No");', 'menu.AddItem("no", "Não");', 1),
    ('menu.AddItem("1", "Next");', 'menu.AddItem("1", "Próxima");', 1),
    ('menu.AddItem("2", "back");', 'menu.AddItem("2", "Voltar");', 1),
    ('"You must wait 60 seconds between swap attempts!"', '"Espere 60 segundos entre um pedido de troca e outro!"', 1),
    ('"No Stats is true"', '"As estatísticas estão desligadas."', 1),
    ('"You are not in an arena!"', '"Você não está em uma arena!"', 4),
    ('"This arena is already in 1v1 mode!"', '"Esta arena já está no modo 1x1!"', 1),
    ('"Cannot change to 1v1 in this arena!"', '"Esta arena não pode virar 1x1!"', 1),
    ('"Cannot switch to 1v1 now!"', '"Não dá para mudar para 1x1 agora!"', 1),
    ('"There are more then 2 players in this arena"', '"Há mais de 2 jogadores nesta arena"', 1),
    ('"Changed current arena to 1v1 arena!"', '"A arena mudou para 1x1!"', 2),
    ('"This arena is already in 2v2 mode!"', '"Esta arena já está no modo 2x2!"', 1),
    ('"Cannot change to 2v2 in this arena!"', '"Esta arena não pode virar 2x2!"', 1),
    ('"Cannot switch to 2v2 now!"', '"Não dá para mudar para 2x2 agora!"', 1),
    ('"Changed current arena to 2v2 arena!"', '"A arena mudou para 2x2!"', 2),
    ('"This doesn\'t do anything and hasn\'t for a long time. Have a hitsound instead!"', '"Este comando não faz mais nada. Use o som de acerto no lugar!"', 1),
    ('"\\x01HUD is \\x04%sabled\\x01.", g_bShowHud[client] ? "en":"dis"', '"\\x01Placar na tela \\x04%s\\x01.", g_bShowHud[client] ? "ligado":"desligado"', 1),
    ('"\\x03%N\\x01 has \\x04%i\\x01 wins and \\x04%i\\x01 losses. You have a \\x04%i%%\\x01 chance of beating him."',
     '"\\x03%N\\x01 tem \\x04%i\\x01 vitórias e \\x04%i\\x01 derrotas. Você tem \\x04%i%%\\x01 de chance de vencer."', 1),
    ('"\\x03%N\\x01\'s rating is \\x04%i\\x01. You have a \\x04%i%%\\x01 chance of beating him."',
     '"O ELO de \\x03%N\\x01 é \\x04%i\\x01. Você tem \\x04%i%%\\x01 de chance de vencer."', 1),
    ('"\\x01Database is \\x04Up\\x01."', '"\\x01Banco de dados \\x04no ar\\x01."', 1),
    ('"\\x01Database is \\x04Down\\x01."', '"\\x01Banco de dados \\x04fora do ar\\x01."', 1),
    ('"[MGE] Arena = EndIf and you have the Manntreads. Automatically removing you from the queue."',
     '"[MGE] A arena Endif não aceita as Mantreads. Você foi tirado da fila."', 1),
    ('"This arena is already in KOTH mode!"', '"Esta arena já está no modo KOTH!"', 1),
    ('"Cannot change to KOTH mode in this arena!"', '"Esta arena não pode virar KOTH!"', 1),
    ('"Cannot switch to KOTH now!"', '"Não dá para mudar para KOTH agora!"', 1),
    ('"Changed current arena to KOTH mode!"', '"A arena mudou para o modo KOTH!"', 1),
    ('"Changed current arena to KOTH mode"', '"A arena mudou para o modo KOTH!"', 1),
    ('"This arena is already in MGE mode!"', '"Esta arena já está no modo MGE!"', 1),
    ('"Changed current arena to MGE mode!"', '"A arena mudou para o modo MGE!"', 1),
    ('"Changed current arena to MGE mode"', '"A arena mudou para o modo MGE!"', 1),
]
for a, b, qtd in TEXTOS:
    if s.count(a) != qtd:
        sys.exit("ERRO: texto %r achado %d vez(es), esperava %d" % (a[:50], s.count(a), qtd))
    s = s.replace(a, b)
open(sp, "w", encoding="utf-8").write(s)
print("MGEMod: %d mensagens removidas e %d textos fixos em portugues" % (n, sum(q for _, _, q in TEXTOS)))

# ---------------------------------------------------------------- 3. frases (translations) em portugues
PT = {
    "MenuTitle": "Entrar numa arena...",
    "MenuRemove": "Sair da fila",
    "HPLeft": "{green}[MGE]{default} Seu adversário ficou com {green}{1}{default} de vida.",
    "Adv": "{olive}Para entrar numa arena, digite {default}!add\\n{olive}Para ver todos os comandos, digite {default}!mgehelp",
    "JoinsArena": "{lightgreen}{1} ({2}) {default}entrou na arena {green}{3}.",
    "JoinsArenaNoStats": "{lightgreen}{1} {default}entrou na arena {green}{2}.",
    "ChoseArena": "Você escolheu a arena {green}{1}.",
    "NextInLine": "Você é o {green}próximo{default} da fila.",
    "InLine": "Você é o {green}{1}º{default} da fila.",
    "GainedPoints": "Você ganhou {green}{1}{default} pontos de ELO.",
    "LostPoints": "Você perdeu {green}{1}{default} pontos de ELO.",
    "MyRank": "Seu ELO é {green}{1}{default}. Vitórias: {green}{2}{default}, derrotas: {green}{3}{default}",
    "MyRankNoRating": "Você tem {green}{1}{default} vitórias e {green}{2}{default} derrotas.",
    "ClassIsNotAllowed": "{olive}Esta classe não é permitida nesta arena!",
    "LowRating": "Seu ELO {green}{1}{default} é baixo demais para esta arena. O mínimo é {green}{2}",
    "HighRating": "Seu ELO {green}{1}{default} é alto demais para esta arena. O máximo é {green}{2}",
    "XdefeatsY": "{lightgreen}{1}{default} ({2}) venceu {lightgreen}{3}{default} ({4}) num duelo até {green}{5}{default} em {green}{6}",
    "XdefeatsYearly": "{lightgreen}{1}{default} ({2}) venceu {lightgreen}{3}{default} ({4}) num duelo em {green}{5}",
    "SpecRemove": "{olive}Não dá para ir de espectador no meio da luta: você saiu da fila.",
    "ClassChangePoint": "{olive}Você trocou de classe no meio da luta e deu um ponto ao adversário.",
    "ClassChangePointOpponent": "{olive}Seu adversário trocou de classe no meio da luta e você ganhou um ponto.",
    "Welcome1": "{olive}Bem-vindo ao MGE versão {lightgreen}{1}",
    "Welcome2": "{olive}Mapa de{default}: {lightgreen}Swaty {default}e {lightgreen}CB",
    "Welcome3": "{olive}Plugin de{default}: {lightgreen}Lange & Cprice{default}, baseado no {lightgreen}kAmmomod",
    "top5error": "[MGE] Ainda não há jogadores suficientes no ranking.",
    "bballdunk": "{lightgreen}Você {default}ENTERROU em cima de {lightgreen}{1}{default}!",
    "Cmd_MGECmds": "[MGE] Ajuda: comandos do MGE",
    "Cmd_SeeConsole": "[MGE] Veja a lista completa no console.",
    "Cmd_MGEMod": "[MGE] mgemod\\t - Menu",
    "Cmd_Add": "[MGE] add\\t - Uso: add <número ou nome da arena>. Entra numa arena.",
    "Cmd_Remove": "[MGE] remove\\t - Sai da arena atual.",
    "Cmd_First": "[MGE] first\\t - Entra na primeira arena livre.",
    "Cmd_Top5": "[MGE] top5\\t - Mostra os 5 melhores jogadores.",
    "Cmd_Rank": "[MGE] rank\\t - Uso: rank <nome do jogador>. Mostra o ELO do jogador.",
    "Cmd_HitBlip": "[MGE] hitblip - Liga e desliga o som de acerto.",
    "Cmd_Hud": "[MGE] hud\\t - Liga e desliga o placar na tela.",
    "Cmd_Handicap": "[MGE] handicap - Diminui a sua vida máxima. Digite '!handicap off' para desligar.",
    "NoClassChange": "{olive}Você não pode trocar de classe agora.",
    "DatabaseDown": "Falha na conexão com o banco de dados: estatísticas desligadas.\\nNova tentativa em {1} minutos.",
    "StatsRestored": "Conexão com o banco de dados restaurada, atualizando as estatísticas...\\nEstatísticas restauradas.",
    "StatsRestoredDown": "O banco de dados está no ar, mas as estatísticas foram desligadas pela administração.",
    "MustJoinArena": "{olive}Você precisa entrar numa arena para fazer isso.",
    "NoCurrentHandicap": "{olive}Você não está usando handicap.",
    "CurrentHandicap": "{olive}Seu handicap atual é de {lightgreen}{1} {olive}de vida máxima.",
    "InvalidHandicap": "{olive}Handicap inválido. O handicap foi desligado.",
    "HandicapDisabled": "{olive}Handicap desligado.",
}
linhas = open(frases_orig, encoding="utf-8").read().split("\n")
atual, feitos, saida = None, set(), []
for l in linhas:
    m = re.match(r'^\t"([^"]+)"', l)
    if m:
        atual = m.group(1)
    m = re.match(r'^(\t\t"en"\s+)"(.*)"\s*$', l)
    if m and atual in PT:
        orig = m.group(2)
        novo = PT[atual]
        if sorted(re.findall(r"\{\d\}", orig)) != sorted(re.findall(r"\{\d\}", novo)):
            sys.exit("ERRO: %s ficou com marcadores diferentes do original" % atual)
        l = '%s"%s"' % (m.group(1), novo)
        feitos.add(atual)
    saida.append(l)
falta = set(PT) - feitos
if falta:
    sys.exit("ERRO: frases nao achadas no arquivo: %s" % ", ".join(sorted(falta)))
open(frases_saida, "w", encoding="utf-8").write("\n".join(saida))
print("frases do MGE em portugues: %d" % len(feitos))
