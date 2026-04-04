import random
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth
from app.services.groq_service import ai_service
from typing import List, Dict, Any
import logging
import asyncio

# Lista de User-Agents para Rotação
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76"
]

class RadarService:
    def scrape_meta_ads(self, page_id: str = "418295661555191") -> List[str]:
        """
        Scraping SÍNCRONO da Meta Ads Library para evitar NotImplementedError no Windows.
        """
        ads_texts = []
        user_agent = random.choice(USER_AGENTS)
        
        with sync_playwright() as p:
            # Modo visual (Headed) e bypass de automação
            browser = p.chromium.launch(
                headless=False, 
                args=['--disable-blink-features=AutomationControlled']
            )
            context = browser.new_context(
                user_agent=user_agent,
                viewport={'width': 1280, 'height': 800}
            )
            page = context.new_page()
            
            # Aplica Stealth (versão síncrona compatível)
            stealth(page)
            
            url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=BR&view_all_page_id={page_id}&search_type=page&media_type=all"
            
            try:
                # Navegação síncrona
                page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Delay para renderização React
                time.sleep(5)
                
                # Mimic Humano: Movimento e Scroll
                page.mouse.move(random.randint(100, 500), random.randint(100, 500))
                
                for _ in range(2):
                    page.mouse.wheel(0, random.randint(400, 800))
                    time.sleep(random.uniform(1, 3))
                
                page.wait_for_selector('div[role="main"]', timeout=30000)
                ad_elements = page.query_selector_all('div.xh8yej3')
                
                for el in ad_elements[:3]:
                    text = el.inner_text()
                    if text:
                        ads_texts.append(text.strip())
                
            except Exception as e:
                logging.error(f"FALHA NO RADAR (MODO SÍNCRONO): {str(e)}")
            finally:
                browser.close()
        
        return ads_texts

    async def analyze_competitor(self, ads: List[str]) -> str:
        """
        Analisa as copies via Groq (Mantido async para integração com AI Service).
        """
        if not ads:
            return "ALERTA: PERÍMETRO BLOQUEADO OU NENHUM ANÚNCIO NO RADAR."

        system_prompt = (
            "Você é um espião de inteligência competitiva de alto escalão. Analise estas copies de luxo.\n"
            "FOCO: Eles usam Preço, Status (Luxo), Tecnologia ou Urgência?\n"
            "MISSÃO: Gere um alerta tático curto sugerindo como a Bracci pode desposicioná-los "
            "usando autoridade e exclusividade superior."
        )
        
        user_prompt = "DADOS DE INTELIGÊNCIA:\n" + "\n---\n".join(ads)

        client = await ai_service._get_client()
        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=ai_service.model,
            temperature=0.4,
        )
        return chat_completion.choices[0].message.content

radar_service = RadarService()
