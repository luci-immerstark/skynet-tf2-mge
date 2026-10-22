# SKYNET TF2 MGE (Docker)

Servidor de **TF2 MGE** (duelos 1x1 e 2x2 para treinar) pronto para usar: [MGEMod](https://github.com/sapphonie/MGEMod) 3.0.9 com o mapa **mge_training_v8_beta4b** (18 arenas), 100 tick, sem crítico aleatório e com o ELO de cada jogador salvo num banco próprio. Montado em cima da imagem [`tf2-sourcemod`](https://github.com/melkortf/tf2-servers) do melkor.tf.

```
ghcr.io/luci-immerstark/skynet-tf2-mge:latest
```

[English below](#english)

## O que vem dentro

| Item | Versão |
|---|---|
| Servidor do TF2 | **64 bits** (`srcds_linux64`), da imagem base `ghcr.io/melkortf/tf2-sourcemod/amd64`. A imagem é só para **x86-64 (amd64)**: não roda em ARM (Raspberry Pi, Oracle Ampere, Mac M1+ sem emulação). |
| SourceMod e Metamod:Source | os da imagem base (64 bits), com os plugins padrão. |
| MGEMod | **3.0.9**, commit [`da8cefd`](https://github.com/sapphonie/MGEMod/tree/da8cefde880b76fb466e543786b9f94972aaa676) (7 fev. 2025), compilado na montagem com o compilador do próprio SourceMod da imagem. |
| Mapa | **mge_training_v8_beta4b** (41 MB), do repositório do MGEMod, com as 18 arenas do `mgemod_spawns.cfg` oficial. |
| Tick | **100** (`TICKRATE=100`), com rates de até 100. |

Todos os arquivos do MGEMod e o mapa são baixados em versão fixa e **conferidos por sha256** na montagem. Se qualquer um mudar, a montagem falha.

**Arenas do mapa:** Viaduct Middle, Granary Middle, Granary Last, Badlands Middle, Badlands Spire, Gullywash Middle, Waste Middle, Snakewater Middle, Gravelpit C, Process Middle, Trainyard, Turris 1, Turris 2, Ammomod, Ammomod [MGE], No Splash, Endif e BBall 2v2.

**Configuração do servidor:** sem crítico aleatório (`tf_weapon_criticals 0`), sem limite de tempo nem troca de mapa, sem SourceTV (todas as vagas são de jogadores) e 12 vagas.

### Mudanças no MGEMod

O código original é baixado e recebe duas mudanças antes de compilar (veja a pasta [`build/`](build/)):

1. **Mensagens em português.** O chat, os menus e a ajuda (`!mgehelp`) ficam em português do Brasil. Saem do chat as mensagens de resultado de cada duelo ("X venceu Y"), de boas-vindas e de vida restante do adversário, que poluem o chat com o servidor cheio. O lembrete "digite !add", para quem está fora das arenas, aparece a cada 3 minutos e meio (no original, a cada 15 segundos).
2. **Duelos no log do jogo.** Cada vitória e derrota vira uma linha `"Jogador<id><[U:1:...]><time>" triggered "mge_win"` (ou `"mge_loss"`) no log do servidor. Rankings como o HLstatsX:CE ou HLstatsZ podem pontuar os duelos a partir delas (veja [Ranking externo](#ranking-externo-opcional)).

## Requisitos

- Linux x86-64 com Docker (ou Docker Desktop no Windows com WSL 2).
- **Disco:** cerca de 10 GB (a imagem base tem cerca de 7 GB, e o TF2 confere atualizações ao ligar).
- **Memória:** 1,5 GB por servidor com 12 jogadores.
- **CPU:** um núcleo livre. Num servidor com outros jogos, reserve um núcleo para ele (`--cpuset-cpus`).
- **Token GSLT** (opcional, mas sem ele o servidor não aparece na lista da Steam): crie em <https://steamcommunity.com/dev/managegameservers> com o App ID **440**. Um token por servidor.
- **Porta UDP liberada** no firewall e no roteador (padrão 27015).

## Instalação

### 1. Arquivo de configuração

Crie um arquivo `mge.env` e deixe só você lendo (`chmod 600 mge.env`):

```
RCON_PASSWORD=<gere com: openssl rand -hex 16>
SERVER_HOSTNAME=Meu Servidor de MGE
SERVER_TOKEN=<seu token GSLT>
SM_ADMINS=<seu SteamID, ex.: STEAM_0:1:1234567>
SERVER_REGION=2
```

### 2. Ligar com `docker run`

```bash
docker volume create mge-dados
docker run -d --name tf2-mge --restart unless-stopped \
  --env-file mge.env \
  -p 27015:27015/udp \
  --memory 1536m \
  -v mge-dados:/home/tf2/server/tf/addons/sourcemod/data/sqlite \
  ghcr.io/luci-immerstark/skynet-tf2-mge:latest
```

O volume `mge-dados` guarda o ELO, as vitórias e as derrotas dos jogadores. Sem ele, o ranking do MGE zera toda vez que o container é recriado.

Na primeira vez o servidor confere atualizações do TF2 e pode levar alguns minutos para aparecer. Acompanhe com `docker logs -f tf2-mge`. Quando aparecer `Loaded 18 arenas. MGEMod enabled.` nos logs do SourceMod, está pronto.

### 3. Ou com `docker compose`

```yaml
services:
  mge:
    image: ghcr.io/luci-immerstark/skynet-tf2-mge:latest
    container_name: tf2-mge
    restart: unless-stopped
    env_file: mge.env
    ports:
      - "27015:27015/udp"
    mem_limit: 1536m
    volumes:
      - mge-dados:/home/tf2/server/tf/addons/sourcemod/data/sqlite

volumes:
  mge-dados:
```

```bash
docker compose up -d
```

### 4. Entrar

No console do TF2: `connect SEU_IP:27015`. Para trocar de porta, mude `PORT` no `mge.env` e o `-p` (por exemplo, `PORT=27055` e `-p 27055:27055/udp`).

## Variáveis

| Variável | Padrão | Para que serve |
|---|---|---|
| `RCON_PASSWORD` | (vazia) | **Obrigatória.** Senha do RCON: no mínimo 12 caracteres, só letras, números e `. _ - @ % + =`. Sem ela, ou com senha fraca, o servidor não liga. |
| `SERVER_HOSTNAME` | `TF2 MGE Server` | Nome do servidor na lista. |
| `SERVER_PASSWORD` | (vazia) | Senha para entrar no servidor (vazia = aberto). |
| `SERVER_TOKEN` | (vazio) | Token GSLT (32 caracteres hexadecimais), para o servidor aparecer na lista da Steam. |
| `SM_ADMINS` | (vazio) | SteamIDs dos admins, separados por vírgula (`STEAM_0:1:123` ou `[U:1:123]`). Recebem acesso total (`z`). |
| `SERVER_TAGS` | `mge,1v1,duel,training,100tick` | Tags do servidor. |
| `SERVER_REGION` | `255` | Região (`0` a `7`, `255` = mundo; `2` = América do Sul). |
| `PORT` | `27015` | Porta do jogo (publique a mesma no `-p`). |
| `TICKRATE` | `100` | `100`, `133` ou `200`. Vazio = 66,7, o padrão do TF2. |
| `DOWNLOAD_URL` | (vazio) | Endereço do seu FastDL (veja abaixo). |

Para mudar o número de vagas, troque o `+maxplayers 12` no fim do `docker run` (ou em `command:` no compose): `... skynet-tf2-mge:latest +sv_pure 1 +map mge_training_v8_beta4b +maxplayers 16`.

Nomes, senhas e links não podem ter aspas, ponto e vírgula ou quebra de linha (é assim que se injetaria comando no `server.cfg`); a imagem recusa e diz o que corrigir.

## FastDL (recomendado)

O mapa tem 41 MB e não vem com o jogo. Sem FastDL, cada jogador novo baixa o mapa direto do servidor do jogo, que é lento. Com FastDL ele baixa de um site comum, em segundos:

1. Pegue o mapa de dentro da imagem e compacte:

   ```bash
   docker cp tf2-mge:/home/tf2/server/tf/maps/mge_training_v8_beta4b.bsp .
   bzip2 -k mge_training_v8_beta4b.bsp
   ```

2. Publique `mge_training_v8_beta4b.bsp.bz2` num servidor web, dentro de uma pasta `maps/` (ex.: `https://seu-site/tf/maps/mge_training_v8_beta4b.bsp.bz2`).
3. No `mge.env`, coloque `DOWNLOAD_URL=https://seu-site/tf/` e recrie o container.

## Comandos no jogo

Digite no chat. Os comandos com `!` também funcionam com `/`, e aí a mensagem não aparece para os outros.

| Comando | O que faz |
|---|---|
| `!add` | Abre o menu das arenas. `!add 3` entra direto na arena 3. |
| `!remove` | Sai da arena ou da fila. |
| `!first` | Entra na primeira arena livre. |
| `!rank` | Mostra o seu ELO. `!rank nome` mostra o de outro jogador. |
| `!top5` | Mostra os 5 melhores. |
| `!hud` / `!hitblip` | Liga e desliga o placar na tela / o som de acerto. |
| `!handicap 150` | Diminui a sua vida máxima (`!handicap off` desliga). |
| `!1v1` / `!2v2` | Troca a arena entre duelo e dupla. |
| `!mgehelp` | Lista todos os comandos. |

O ELO começa em 1600 para todos.

## Administração

- **Admins:** coloque os SteamIDs em `SM_ADMINS` e recrie o container. Eles usam os comandos do SourceMod no jogo (`!admin`, `sm_kick`, `sm_ban`...).
- **RCON sem abrir porta:**

  ```bash
  docker exec tf2-mge sh -c './rcon -H 127.0.0.1 -p "$PORT" -P "$RCON_PASSWORD" status'
  ```

- **Atualizar:** a imagem é montada de novo todo dia com o TF2 mais novo e só é publicada se passar nos testes. Para atualizar:

  ```bash
  docker pull ghcr.io/luci-immerstark/skynet-tf2-mge:latest
  docker rm -f tf2-mge   # o ELO continua no volume mge-dados
  # e rode o docker run de novo (ou: docker compose up -d)
  ```

- **Backup do ranking:** `docker run --rm -v mge-dados:/d -v "$PWD":/b alpine tar czf /b/mge-dados.tgz -C /d .`

## Ranking externo (opcional)

Para mandar o log do servidor a um HLstatsX:CE ou HLstatsZ, monte o seu próprio `server.cfg.template` (copie o [`config/cfg/server.cfg.template`](config/cfg/server.cfg.template) deste repositório e acrescente no fim uma linha `logaddress_add` com o endereço e a porta do daemon do ranking):

```bash
-v ./server.cfg.template:/home/tf2/server/tf/cfg/server.cfg.template:ro
```

No ranking, crie as ações `mge_win` e `mge_loss` com os pontos que quiser (por exemplo, +5 e -2). Para que só os duelos contem, zere os pontos de kill do jogo do MGE no seu ranking.

## Segurança

O que a imagem faz:

- **Nenhuma senha, token, IP, e-mail ou admin embutido.** Tudo entra pelas variáveis quando o container liga.
- **Recusa senha de RCON fraca.** A imagem base vem com a senha `123456`; aqui o padrão é vazio e o servidor não liga sem uma senha forte.
- **Recusa valores que injetariam comandos** no `server.cfg` ou na linha de comando do servidor.
- **FastDL vazio por padrão** (a base vem com o FastDL de um site de terceiros).
- **Só mapas oficiais podem mandar comandos para o console do servidor** (`sv_allow_point_servercommand "official"`) e os jogadores não sobem arquivos ao servidor (`sv_allowupload 0`).
- **Código e mapa conferidos por sha256** na montagem; o MGEMod é compilado aqui, a partir do código-fonte, e não vem como binário pronto.
- **Testes automáticos** antes de cada publicação ([`tests/teste.sh`](tests/teste.sh)): recusa de configurações inseguras, plugins carregados, 100 tick, 18 arenas, banco do MGEMod, crítico desligado, nenhum erro registrado, nenhum dado sensível nos arquivos da imagem e desligamento limpo.
- **Varredura de dados sensíveis** no repositório a cada montagem ([`tools/varredura.sh`](tools/varredura.sh)).
- Roda como usuário comum (`tf2`), não como root.

O que recomendamos:

- **Publique só a porta UDP** (`-p 27015:27015/udp`). O RCON usa TCP na mesma porta: sem publicar o TCP, ninguém de fora tenta adivinhar a senha.
- Se usar `--network host`, bloqueie o TCP da porta do jogo no firewall (ex.: `ufw allow 27015/udp` e nada para TCP).
- Guarde o `mge.env` fora de repositórios git e com `chmod 600`.

Achou um problema de segurança? Não abra issue pública: use **Report a vulnerability**, na aba **Security** deste repositório, que só os mantenedores veem.

## Testar na sua máquina

```bash
docker build -t mge:teste .
bash tests/teste.sh mge:teste
bash tools/varredura.sh .
```

## Créditos

- [MGEMod](https://github.com/sapphonie/MGEMod): Lange e Cprice (autores originais, a partir do kAmmomod), mantido por sapphonie e colaboradores (GPLv3);
- mapa mge_training: Swaty e CB;
- [melkor.tf](https://github.com/melkortf/tf2-servers) pela imagem base (MIT);
- [AlliedModders](https://www.sourcemod.net/) pelo SourceMod e Metamod:Source;
- Valve pelo Team Fortress 2.

## Licença

GPLv3 (veja [LICENSE](LICENSE)), a mesma do MGEMod. Dentro da imagem, a licença fica em `/home/tf2/server/LICENSES`.

---

## English

A ready-to-run **TF2 MGE** (1v1/2v2 training) server image: [MGEMod](https://github.com/sapphonie/MGEMod) 3.0.9 (commit `da8cefd`) with the **mge_training_v8_beta4b** map (18 arenas), 100 tick, random crits off, and per-player ELO stored in its own SQLite database. Built on melkor.tf's [`tf2-sourcemod`](https://github.com/melkortf/tf2-servers) image.

- **64-bit** TF2 server (`srcds_linux64`); the image is **x86-64 (amd64) only**.
- MGEMod and the map are pinned and **verified by sha256** at build time, and MGEMod is compiled from source with the base image's SourceMod compiler.
- Chat messages are in **Brazilian Portuguese**, without per-duel result, welcome and remaining-HP messages, and the "type !add" reminder shows every 3.5 minutes instead of every 15 seconds. Each duel win/loss is logged as `triggered "mge_win"` / `"mge_loss"`, for HLstatsX:CE/HLstatsZ rankings.

```bash
docker volume create mge-dados
docker run -d --name tf2-mge --restart unless-stopped \
  --env-file mge.env -p 27015:27015/udp --memory 1536m \
  -v mge-dados:/home/tf2/server/tf/addons/sourcemod/data/sqlite \
  ghcr.io/luci-immerstark/skynet-tf2-mge:latest
```

- `RCON_PASSWORD` is **required** (at least 12 characters: letters, digits and `. _ - @ % + =`). The server refuses to start without it or with a weak one (the base image defaults to `123456`).
- Other variables: `SERVER_HOSTNAME`, `SERVER_PASSWORD`, `SERVER_TOKEN` (GSLT, App ID 440), `SM_ADMINS` (comma-separated SteamIDs, full access), `SERVER_TAGS`, `SERVER_REGION`, `PORT`, `TICKRATE` (default `100`), `DOWNLOAD_URL` (FastDL; recommended, the map is 41 MB).
- Keep the `mge-dados` volume: it holds everyone's ELO.
- No passwords, tokens, IPs or admins are baked in, only official maps may run server commands, and every release passes automated tests.
- Publish only the UDP port; RCON uses TCP on the same port, so leaving TCP closed keeps it off the internet.
- Licensed under GPLv3, like MGEMod.
