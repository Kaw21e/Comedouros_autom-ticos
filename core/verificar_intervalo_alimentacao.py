import pandas as pd
from datetime import datetime
import os
import logging

from config import TAG_INFO

INTERVALO_HORAS = 24

def verificar_intervalo_alimentacao(tag_id, caminho_csv, intervalo_horas=INTERVALO_HORAS):
    """
    Verifica se a tag atual já realizou alimentação nas últimas `intervalo_horas` horas.
    A regra é individual por tag, com exceção da tag mestra, que sempre é liberada.

    Args:
        tag_id: ID da tag do animal lido atualmente
        caminho_csv: Caminho do arquivo CSV de relatório
        intervalo_horas: Intervalo em horas (padrão: 24)

    Retorna:
        True se BLOQUEADO (tag já alimentou dentro do intervalo)
        False se LIBERADO (tag sem registro recente, sem registros, ou tag mestra)
    """
    try:
        tag_info = TAG_INFO.get(str(tag_id).strip(), {})
        if tag_info.get("mestra", False):
            logging.debug(f"Tag mestra '{tag_id}' liberada sem restrição de intervalo.")
            return False

        # Se o arquivo não existe ou está vazio, libera o sistema (primeiro acesso)
        if not os.path.exists(caminho_csv) or os.path.getsize(caminho_csv) == 0:
            return False

        # Lê o CSV
        df = pd.read_csv(caminho_csv)

        # Se não há registros no CSV, libera
        if df.empty:
            return False

        # Normaliza a tag e filtra apenas os registros dela
        df['tag_id'] = df['tag_id'].astype(str).str.strip()
        tag_procurada = str(tag_id).strip()
        df_tag = df[df['tag_id'] == tag_procurada]

        if df_tag.empty:
            return False

        # Converter hora_entrada para datetime logo após ler
        try:
            df_tag['hora_entrada'] = pd.to_datetime(df_tag['hora_entrada'], errors='coerce')
        except Exception as e:
            logging.warning(f"Erro ao converter hora_entrada para datetime: {e}")
            return False

        df_tag = df_tag.dropna(subset=['hora_entrada'])
        if df_tag.empty:
            return False

        # Ordenar por hora_entrada e pegar o último registro da tag
        df_tag = df_tag.sort_values(by='hora_entrada')
        ultimo_registro = df_tag.iloc[-1]
        ultima_entrada = ultimo_registro['hora_entrada']

        # Remover timezone info se presente para evitar comparações mistas
        if hasattr(ultima_entrada, 'tz') and ultima_entrada.tz is not None:
            try:
                ultima_entrada = ultima_entrada.tz_localize(None)
            except Exception:
                # Em alguns casos, a série pode já estar sem tz; ignorar
                pass

        agora = datetime.now()

        # Calcular diferença em horas desde o último acesso da mesma tag
        diferenca_horas = (agora - ultima_entrada).total_seconds() / 3600

        # Log para debug — informar qual tag solicitou e o último acesso dela
        logging.debug(
            f"Tag solicitante: '{tag_id}' | Último acesso da tag: {ultima_entrada} | "
            f"Diferença: {diferenca_horas:.2f}h | Bloqueada: {diferenca_horas < intervalo_horas}"
        )

        # Aplicar bloqueio individual: se diferença < intervalo_horas, BLOQUEIA
        if diferenca_horas < intervalo_horas:
            return True

        return False

    except Exception as e:
        logging.error(f"Erro ao verificar intervalo de alimentação para tag {tag_id}: {e}")
        return False  # Em caso de erro, libera o sistema
