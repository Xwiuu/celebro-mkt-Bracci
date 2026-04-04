from decimal import Decimal, ROUND_HALF_UP

class DataNormalizer:
    @staticmethod
    def to_brl(value, platform: str) -> Decimal:
        """ Converte valores brutos das APIs para Decimal BRL padrão. """
        if value is None: return Decimal("0.00")
        
        val = Decimal(str(value))
        
        # Google manda em Micros (1.000.000)
        if platform.lower() == "google":
            normalized = val / Decimal("1000000")
        # Meta costuma mandar em centavos ou direto (depende da config da conta)
        # Vamos padronizar para garantir 2 casas decimais
        else:
            normalized = val
            
        return normalized.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def clean_campaign_name(name: str) -> str:
        """ Padroniza nomes para facilitar a atribuição Omnichannel (Lá embaixo). """
        return name.strip().upper()