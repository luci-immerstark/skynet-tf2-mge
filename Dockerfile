# syntax=docker/dockerfile:1.10
# SKYNET TF2 MGE: servidor de MGE (duelos 1x1 e 2x2) pronto, em cima da imagem tf2-sourcemod do melkor.tf (64 bits).
# MGEMod e o mapa mge_training_v8_beta4b vem do repositorio oficial do MGEMod, em versao fixa e conferidos por sha256.
# Nada aqui tem senha, token ou IP: tudo isso entra pelas variaveis de ambiente quando o container liga.

# Imagem base. A montagem automatica (GitHub) troca "latest" pelo digest exato que foi testado.
ARG BASE=ghcr.io/melkortf/tf2-sourcemod/amd64:latest

# ---------- 1. MGEMod e o mapa, versao fixa (commit) e conferidos por sha256 ----------
FROM ubuntu:24.04 AS fontes
ARG MGE_COMMIT=da8cefde880b76fb466e543786b9f94972aaa676
ARG RAW=https://raw.githubusercontent.com/sapphonie/MGEMod/${MGE_COMMIT}
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 \
 && rm -rf /var/lib/apt/lists/*
ADD --checksum=sha256:d359c1b7b928417637c687064801e01c7c8f61d1c13edbf591ba301a3bdd30f5 \
    ${RAW}/addons/sourcemod/scripting/mge.sp /fontes/mge.sp
ADD --checksum=sha256:e95dfa5f52ebeb81972151b997d3b887b869c02f91e63051a07e1e33deb30d74 \
    ${RAW}/addons/sourcemod/scripting/include/morecolors.inc /fontes/include/morecolors.inc
ADD --checksum=sha256:392fb5ccf70566aea1663eb0378afc167f6ff54846f7f7d44825519028ed5d00 \
    ${RAW}/addons/sourcemod/configs/mgemod_spawns.cfg /fontes/mgemod_spawns.cfg
ADD --checksum=sha256:3d6f126c34f37e16e9b69d0a5c9a7ae2144f174cf45f2fab1023fe8beeb9b5f7 \
    ${RAW}/addons/sourcemod/translations/mgemod.phrases.txt /fontes/mgemod.phrases.original.txt
ADD --checksum=sha256:3c00fbc6c63c972834f9824e8d5d5e394a66b915f62a6308883b152dd8d64cb2 \
    ${RAW}/maps/mge_training_v8_beta4b.bsp /fontes/mge_training_v8_beta4b.bsp
COPY build/ /build/
# Duas mudancas no MGEMod (veja build/): cada vitoria e derrota de duelo vai para o log do jogo (para rankings como
# o HLstatsX/HLstatsZ) e as mensagens ficam em portugues, sem as de resultado de duelo, boas-vindas e vida restante.
RUN set -eu; \
    python3 -I /build/duelos_no_log.py /fontes/mge.sp; \
    python3 -I /build/portugues.py /fontes/mge.sp /fontes/mgemod.phrases.original.txt /fontes/mgemod.phrases.txt; \
    test "$(head -c 4 /fontes/mge_training_v8_beta4b.bsp)" = "VBSP"; \
    chmod -R u=rwX,go=rX /fontes   # o ADD de um link grava os arquivos so para o root (600)

# ---------- 2. compila o MGEMod com o compilador do proprio SourceMod da imagem base ----------
FROM ${BASE} AS compilar
ARG SC=/home/tf2/server/tf/addons/sourcemod/scripting
COPY --from=fontes --chown=tf2:tf2 /fontes/mge.sp /tmp/mge/mge.sp
COPY --from=fontes --chown=tf2:tf2 /fontes/include/ /tmp/mge/include/
RUN set -eu; \
    "${SC}/spcomp64" /tmp/mge/mge.sp -i/tmp/mge/include -o/tmp/mge.smx; \
    test -s /tmp/mge.smx

# ---------- 3. imagem final ----------
FROM ${BASE}
ARG SM=/home/tf2/server/tf/addons/sourcemod

LABEL org.opencontainers.image.title="SKYNET TF2 MGE" \
      org.opencontainers.image.description="Servidor de TF2 MGE pronto (MGEMod + mge_training_v8_beta4b, 100 tick, 64 bits), sem senhas embutidas" \
      org.opencontainers.image.source="https://github.com/luci-immerstark/skynet-tf2-mge" \
      org.opencontainers.image.licenses="GPL-3.0-only"

COPY --from=compilar --chown=tf2:tf2 /tmp/mge.smx ${SM}/plugins/mge.smx
COPY --from=fontes --chown=tf2:tf2 /fontes/mgemod_spawns.cfg ${SM}/configs/mgemod_spawns.cfg
COPY --from=fontes --chown=tf2:tf2 /fontes/mgemod.phrases.txt ${SM}/translations/mgemod.phrases.txt
COPY --from=fontes --chown=tf2:tf2 /fontes/mge_training_v8_beta4b.bsp /home/tf2/server/tf/maps/mge_training_v8_beta4b.bsp
COPY --chown=tf2:tf2 config/cfg/ /home/tf2/server/tf/cfg/
COPY --chown=tf2:tf2 LICENSE /home/tf2/server/LICENSES/skynet-tf2-mge-GPL-3.0.txt
COPY --chown=tf2:tf2 --chmod=755 skynet-entrypoint.sh /home/tf2/server/skynet-entrypoint.sh

# Sem valores perigosos de fabrica: a base vem com a senha de RCON 123456 e FastDL de terceiros; aqui ficam vazios
# e o servidor so liga com uma senha forte (veja skynet-entrypoint.sh).
ENV RCON_PASSWORD="" \
    SERVER_HOSTNAME="TF2 MGE Server" \
    SERVER_PASSWORD="" \
    SERVER_TAGS="mge,1v1,duel,training,100tick" \
    SERVER_REGION="255" \
    DOWNLOAD_URL="" \
    TICKRATE="100" \
    SM_ADMINS=""

# O atualizador automatico do SourceMod (update.sourcemod.net) passou a responder 404 e registra erro a cada mapa.
# Numa imagem Docker a atualizacao ja vem pela montagem diaria com a base nova, entao ele fica desligado.
# O MGEMod guarda o ELO num banco SQLite proprio (mgemod.sq3, na pasta data/sqlite: monte um volume nela).
RUN set -eu; \
    sed -i -E 's/^([[:space:]]*"DisableAutoUpdate"[[:space:]]+)"no"/\1"yes"/' ${SM}/configs/core.cfg; \
    grep -qE '^[[:space:]]*"DisableAutoUpdate"[[:space:]]+"yes"' ${SM}/configs/core.cfg; \
    db=${SM}/configs/databases.cfg; \
    if ! grep -q '"mgemod"' "$db"; then \
        awk '{ l[NR] = $0 } /^}/ { fim = NR } END { for (i = 1; i <= NR; i++) { if (i == fim) printf "\t\"mgemod\"\n\t{\n\t\t\"driver\"\t\t\"sqlite\"\n\t\t\"database\"\t\"mgemod\"\n\t}\n"; print l[i] } }' "$db" > /tmp/db.cfg; \
        cat /tmp/db.cfg > "$db"; rm -f /tmp/db.cfg; \
    fi; \
    grep -q '"mgemod"' "$db"; \
    mkdir -p ${SM}/data/sqlite

USER tf2
ENTRYPOINT ["/home/tf2/server/skynet-entrypoint.sh"]
CMD ["+sv_pure", "1", "+map", "mge_training_v8_beta4b", "+maxplayers", "12"]
