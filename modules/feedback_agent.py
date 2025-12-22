from modules.persistence import SessionLocal, CampaignStrategy

# É necessário atualizações para ser utilizado com dados reais!
class FeedbackAgent:
    """
    Feedback Agent (fase de teste).
    Simula resultados reais para fechar o learning loop.
    """

    @staticmethod
    def gerar_feedback_simulado(strategy_id: int) -> dict:
        db = SessionLocal()

        try:
            strategy = db.query(CampaignStrategy).filter(
                CampaignStrategy.id == strategy_id
            ).first()

            if not strategy:
                raise ValueError("Strategy não encontrada.")

            comportamento = strategy.icp_comportamento or {}

            expected_roas = comportamento.get("expected_roas", 1)
            conversion_rate = comportamento.get("conversion_rate", 1)
            click_volume = comportamento.get("click_volume", 10)

            # --- Simulação controlada ---
            total_leads = max(int(click_volume * (conversion_rate / 100)), 1)
            total_conversoes = int(total_leads * 0.3)

            custo_total = round(
                total_leads * (10 / max(expected_roas, 0.1)),
                2
            )

            taxa_resposta = (
                total_conversoes / total_leads
                if total_leads > 0 else 0
            )

            custo_medio_lead = (
                custo_total / total_leads
                if total_leads > 0 else 0
            )

            # --- Atualização da Strategy ---
            strategy.total_leads = total_leads
            strategy.taxa_resposta = round(taxa_resposta, 4)
            strategy.taxa_conversao = round(taxa_resposta * 100, 2)
            strategy.custo_medio_lead = round(custo_medio_lead, 2)
            strategy.status = "SIMULATED_FEEDBACK"

            db.commit()
            db.refresh(strategy)

            return {
                "status": "success",
                "strategy_id": strategy.id,
                "feedback_simulado": {
                    "total_leads": total_leads,
                    "total_conversoes": total_conversoes,
                    "custo_total": custo_total,
                    "taxa_conversao": strategy.taxa_conversao,
                    "custo_medio_lead": strategy.custo_medio_lead
                }
            }

        except Exception as e:
            db.rollback()
            return {
                "status": "error",
                "reason": str(e)
            }

        finally:
            db.close()
