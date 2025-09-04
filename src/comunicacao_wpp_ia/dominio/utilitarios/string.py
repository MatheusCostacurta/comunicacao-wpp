import re
from datetime import date, timedelta

class StringUtilidade:
    @staticmethod
    def para_data(texto_data: str) -> date:
        """
        Converte uma string de data (parcial, completa ou relativa como 'ontem') em um objeto de data.
        Preenche as partes faltantes (mês, ano) com a data atual.
        Retorna a data de hoje se a string for inválida ou vazia.
        """
        hoje = date.today()

        if not texto_data or not isinstance(texto_data, str):
            return hoje

        texto_lower = texto_data.lower()
        if "hoje" in texto_lower:
            return hoje
        if "ontem" in texto_lower:
            return hoje - timedelta(days=1)

        # Tenta padrão "24 de julho"
        match = re.search(r"(\d{1,2})\s+de\s+([a-zA-Z]+)", texto_lower)
        if match:
            dia_str, mes_nome = match.groups()
            dia = int(dia_str)
            meses = {
                "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
                "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
            }
            mes = meses.get(mes_nome)
            if mes:
                try:
                    return date(hoje.year, mes, dia)
                except ValueError:
                    pass

        # Tenta padrões como dd/mm/yyyy, dd-mm-yyyy, dd/mm, dd-mm
        padroes = [
            (r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", lambda d, m, a: date(a if a > 100 else a + 2000, m, d)),
            (r"(\d{1,2})[/-](\d{1,2})", lambda d, m: date(hoje.year, m, d))
        ]
        for padrao, construtor in padroes:
            match = re.search(padrao, texto_data)
            if match:
                try:
                    return construtor(*map(int, match.groups()))
                except (ValueError, TypeError):
                    continue

        # Tenta padrão para apenas o dia (ex: "dia 20")
        numeros = re.findall(r"\d+", texto_data)
        if numeros:
            dia = int(numeros[0])
            if 1 <= dia <= 31:
                try:
                    # Assume o mês e ano correntes
                    return date(hoje.year, hoje.month, dia)
                except ValueError:
                    pass

        # Se nenhum padrão funcionar, retorna a data de hoje como fallback
        return hoje