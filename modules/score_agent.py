from datetime import datetime

class ScoreAgent:
    @staticmethod
    def avaliar(strategy: dict) -> dict:
        score = 1.0
        flags = []

        # ---------- 1. ICP DEMOGRÁFICO ----------
        icp_demo = strategy.get("icp_demografia", {})
        if not all([
            icp_demo.get("age_range"),
            icp_demo.get("gender"),
            icp_demo.get("location")
        ]):
            score -= 0.2
            flags.append("icp_incompleto")

        # ---------- 2. MÉTRICAS COMPORTAMENTAIS ----------
        icp_comp = strategy.get("icp_comportamento", {})
        roas = icp_comp.get("expected_roas", 0)
        cvr = icp_comp.get("conversion_rate", 0)
        clicks = icp_comp.get("click_volume", 0)

        # ROAS irrealista
        if roas > 15:
            score -= 0.15
            flags.append("roas_irrealista")

        # Conversão irrealista
        if cvr > 25:
            score -= 0.15
            flags.append("conversao_irrealista")

        # Baixo volume
        if clicks < 100:
            score -= 0.1
            flags.append("baixo_volume_cliques")

        # ---------- 3. CLAREZA DA MENSAGEM ----------
        mensagem = strategy.get("mensagem_template", "").lower()
        mensagens_genericas = [
            "aproveite agora",
            "não perca",
            "o melhor para você",
            "solução ideal"
        ]

        if any(m in mensagem for m in mensagens_genericas):
            score -= 0.1
            flags.append("mensagem_generica")

        # ---------- 4. ALINHAMENTO COM PLATAFORMA ----------
        plataforma = strategy.get("plataforma")
        criativo = strategy.get("criativo_tipo", "").lower()

        if plataforma == "google_ads" and "video" in criativo:
            score -= 0.1
            flags.append("criativo_incompativel_plataforma")

        if plataforma == "meta_ads" and "search" in criativo:
            score -= 0.1
            flags.append("criativo_incompativel_plataforma")

        # ---------- NORMALIZAÇÃO ----------
        score = max(round(score, 2), 0.0)

        # ---------- RISCO ----------
        if score >= 0.8:
            risk = "low"
        elif score >= 0.6:
            risk = "medium"
        else:
            risk = "high"

        return {
            "confidence_score": score,
            "risk_level": risk,
            "flags": flags,
            "avaliado_em": datetime.utcnow().isoformat()
        }
