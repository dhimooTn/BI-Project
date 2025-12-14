import time
import random
import pandas as pd
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


class HelloWorkScraper:

    def __init__(self, driver, base_url, wait_time=10):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, wait_time)

        self.data = {
            "titre": [],
            "entreprise": [],
            "localisation": [],
            "salaire": [],
            "date_publication": [],
            "description": []
        }

    # -------------------------------------------------
    # MAIN SCRAPING
    # -------------------------------------------------
    def scrape_page(self, page):
        url = self.base_url.format(page)

        try:
            self.driver.get(url)

            # attendre la liste des offres
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'ul[aria-label="liste des offres"]')
                )
            )

            self._human_behavior()

            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            offers_list = soup.find(
                "ul",
                attrs={"aria-label": "liste des offres"}
            )

            if not offers_list:
                print(f"⚠️ Page {page} : liste des offres introuvable")
                return

            offres = offers_list.find_all("li", recursive=False)

            if not offres:
                print(f"⚠️ Page {page} : aucune offre trouvée")

            for offre_li in offres:
                self._extract_offer(offre_li)

        except TimeoutException:
            print(f"⏱️ Timeout page {page}")
        except WebDriverException as e:
            print(f"🚨 Selenium error page {page} → {e}")
        except Exception as e:
            print(f"❌ Unknown error page {page} → {e}")

    def scrape_all_pages(self, start_page=1, end_page=50):
        for page in range(start_page, end_page + 1):
            print(f"\n📄 Scraping page {page}")
            self.scrape_page(page)
            time.sleep(random.uniform(1.5, 3.5))

    # -------------------------------------------------
    # OFFER EXTRACTION (1 <li> = 1 offre)
    # -------------------------------------------------
    def _extract_offer(self, offre_li):
        # Extract from the <li> element
        titre, entreprise = self._safe_title_company(offre_li)
        localisation = self._safe_localisation(offre_li)
        date_publication = self._safe_date_publication(offre_li)

        # Extract from the <a> element inside the <li>
        offre_a = offre_li.select_one("a.tw-no-underline.tw-outline-none.tw-inline")
        description = self._safe_description(offre_a) if offre_a else None
        salaire = self._safe_salary(offre_a) if offre_a else None

        self.data["titre"].append(titre)
        self.data["entreprise"].append(entreprise)
        self.data["localisation"].append(localisation)
        self.data["salaire"].append(salaire)
        self.data["date_publication"].append(date_publication)
        self.data["description"].append(description)

    # -------------------------------------------------
    # SAFE METHODS
    # -------------------------------------------------
    def _safe_title_company(self, offre_li):
        try:
            a = offre_li.select_one("a[data-cy='offerTitle']")
            h3 = a.find("h3")
            p = h3.find_all("p")

            titre = p[0].get_text(strip=True)
            entreprise = p[1].get_text(strip=True)

            return titre, entreprise
        except Exception:
            return None, None

    def _safe_localisation(self, offre_li):
        try:
            loc = offre_li.find("div", attrs={"data-cy": "localisationCard"})
            return loc.get_text(strip=True) if loc else None
        except Exception:
            return None

    def _safe_description(self, offre_a):
        """Extract description from the <a> tag using aria-label"""
        try:
            # L'aria-label contient un résumé de l'offre
            aria_label = offre_a.get("aria-label", "")

            if aria_label:
                # Nettoyer le texte: enlever "Voir offre de" du début
                if aria_label.startswith("Voir offre de"):
                    aria_label = aria_label.replace("Voir offre de", "").strip()
                return aria_label

            # Alternative: récupérer tout le texte visible de la carte
            all_text = offre_a.get_text(separator=" ", strip=True)
            return all_text if all_text else None

        except Exception:
            return None

    def _safe_salary(self, offre_a):
        """Extract salary from aria-label attribute"""
        try:
            aria = offre_a.get("aria-label", "")

            if "€" in aria:
                # Extract text between "avec un salaire de" and next comma
                salaire = aria.split("avec un salaire de")[1].split(",")[0].strip()
                return salaire

            return None
        except Exception:
            return None

    def _safe_date_publication(self, offre_li):
        try:
            date_div = offre_li.find(
                "div",
                class_="tw-typo-s tw-text-grey-500 tw-pl-1 tw-pt-1"
            )

            raw_date = date_div.get_text(strip=True) if date_div else None
            return self._normalize_date(raw_date)
        except Exception:
            return None

    # -------------------------------------------------
    # DATE NORMALIZATION
    # -------------------------------------------------
    def _normalize_date(self, text):
        if not text:
            return None

        now = datetime.now()
        text = text.lower()

        try:
            n = int("".join(filter(str.isdigit, text)))

            if "heure" in text:
                return now - timedelta(hours=n)
            if "jour" in text:
                return now - timedelta(days=n)
            if "minute" in text:
                return now - timedelta(minutes=n)

            return None
        except Exception:
            return None

    # -------------------------------------------------
    # ANTI-BAN
    # -------------------------------------------------
    def _human_behavior(self):
        scroll_height = random.randint(300, 800)
        self.driver.execute_script(
            f"window.scrollBy(0, {scroll_height});"
        )
        time.sleep(random.uniform(0.3, 0.8))

    # -------------------------------------------------
    # DATAFRAME
    # -------------------------------------------------
    def to_dataframe(self):
        return pd.DataFrame(self.data)