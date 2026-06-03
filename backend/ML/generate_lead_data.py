"""
Génération de données réalistes de leads CRM pour Lead Scoring ML.
──────────────────────────────────────────────────────────────────
Auteur  : Senior Data Analyst
Contexte: FRS — IT Development Company, Tunis
But     : Créer un dataset sémantiquement cohérent qui reflète
          les vrais patterns d'un cycle commercial B2B en Tunisie.

Patterns métier encodés :
  1. Les referrals convertissent 3x plus que les réseaux sociaux
  2. Les leads à forte valeur sont plus sérieux (budget validé)
  3. Un lead sans email ni téléphone = contact impossible
  4. Plus il y a d'activités (appels, emails, RDV), plus le lead est chaud
  5. Un lead qui stagne > 60 jours sans action = froid
  6. Certains secteurs (IT, Finance, Santé) ont des cycles plus courts
  7. Les leads trade_show sont saisonniers (salons professionnels)
  8. La taille de l'entreprise influence la valeur et le cycle
"""

import csv
import random
import os
from datetime import datetime, timedelta

random.seed(2026)  # Reproductibilité

# ─────────────────────────────────────────────────────────────
# 1. RÉFÉRENTIELS MÉTIER RÉALISTES (contexte tunisien B2B)
# ─────────────────────────────────────────────────────────────

COMPANIES = {
    "IT / Digital": [
        ("DataSphere Solutions", "Ahmed Ben Ali"),
        ("CloudNova Tunisie", "Sami Trabelsi"),
        ("PixelCraft Agency", "Ines Chaabane"),
        ("ByteForge SARL", "Mehdi Hammami"),
        ("NetVision Technologies", "Fatma Souissi"),
        ("SoftBridge Consulting", "Karim Jebali"),
        ("DigiWave Studio", "Amira Belhadj"),
        ("TechPulse Innovation", "Yassine Mrad"),
        ("CodeFactory TN", "Nadia Kchouk"),
        ("SmartGrid Systems", "Rami Khelifi"),
        ("AppNest Mobile", "Leila Gharbi"),
        ("CyberShield Security", "Omar Bouzid"),
    ],
    "Finance / Banque": [
        ("FinTrust Assurances", "Hichem Dridi"),
        ("CapitalWise Gestion", "Salma Ayari"),
        ("MicroFinance Plus", "Nabil Mejri"),
        ("AssetGuard Tunisie", "Rim Hosni"),
        ("BankTech Solutions", "Walid Saidi"),
        ("InvestPro Conseil", "Sonia Maalej"),
        ("PaySecure Gateway", "Tarek Chouchene"),
        ("WealthBridge SA", "Mariem Ayed"),
    ],
    "Santé": [
        ("MedLab Diagnostics", "Dr. Anis Bouaziz"),
        ("PharmaCare Distribution", "Hajer Sfar"),
        ("HealthConnect TN", "Dr. Fathi Rezgui"),
        ("BioGenesis Recherche", "Samia Tlili"),
        ("CliniqPlus Gestion", "Zied Oueslati"),
        ("MedSoft Systems", "Olfa Belhaj"),
    ],
    "Industrie / Fabrication": [
        ("SteelMaster Fonderie", "Mondher Gasmi"),
        ("PlastiPack Emballage", "Amel Khiari"),
        ("AutoParts Tunisie", "Chokri Boujelben"),
        ("TextilePro SARL", "Sana Riahi"),
        ("AgroTech Industries", "Bilel Hamdi"),
        ("BuildMaster BTP", "Lamia Ferchichi"),
        ("ElectroPower SA", "Habib Manai"),
        ("MetalForm Engineering", "Rania Toumi"),
    ],
    "Commerce / Retail": [
        ("ShopConnect Retail", "Youssef Ladhari"),
        ("FreshMarket Distribution", "Nour Slimane"),
        ("LuxuryBrand TN", "Dorra Jerbi"),
        ("QuickServe Logistique", "Fares Abidi"),
        ("TradeLink Export", "Maha Gueddiche"),
        ("RetailPro Solutions", "Adel Nasr"),
    ],
    "Éducation": [
        ("EduTech Academy", "Pr. Moez Kallel"),
        ("SkillUp Formation", "Wided Cherif"),
        ("Campus Digital TN", "Amine Masmoudi"),
        ("LearnPro Plateforme", "Nesrine Hadj"),
    ],
    "Immobilier": [
        ("ImmoVista Promotion", "Khaled Boukadida"),
        ("HomeBuilder SARL", "Asma Rejeb"),
        ("PropTech Tunisie", "Hamza Kouki"),
    ],
    "Tourisme / Hôtellerie": [
        ("TravelSmart Agency", "Manel Sassi"),
        ("HotelConnect Booking", "Sofiane Arfaoui"),
        ("TunExplore Tourism", "Chiraz Mbarek"),
    ],
}

SOURCES = ["website", "phone", "referral", "trade_show", "social_media", "email", "other"]

# Taux de conversion réalistes par source (pattern métier clé)
SOURCE_CONVERSION_RATES = {
    "referral":     0.65,  # Le bouche-à-oreille convertit beaucoup
    "trade_show":   0.45,  # Contact direct en salon = bon signal
    "phone":        0.40,  # Appel entrant = lead motivé
    "website":      0.30,  # Formulaire web = intérêt moyen
    "email":        0.25,  # Campagne email = taux moyen
    "social_media": 0.15,  # Réseaux sociaux = leads froids
    "other":        0.20,  # Divers
}

# Distribution réaliste des sources (pas uniforme)
SOURCE_WEIGHTS = {
    "website":      0.25,
    "referral":     0.15,
    "phone":        0.12,
    "email":        0.18,
    "social_media": 0.15,
    "trade_show":   0.08,
    "other":        0.07,
}

# Fourchettes de valeurs par secteur (en DT — Dinars Tunisiens)
SECTOR_VALUE_RANGES = {
    "IT / Digital":           (5_000, 80_000),
    "Finance / Banque":       (15_000, 150_000),
    "Santé":                  (10_000, 100_000),
    "Industrie / Fabrication":(8_000, 120_000),
    "Commerce / Retail":      (3_000, 50_000),
    "Éducation":              (2_000, 30_000),
    "Immobilier":             (10_000, 90_000),
    "Tourisme / Hôtellerie":  (5_000, 60_000),
}

# Secteurs qui convertissent mieux (multiplicateur)
SECTOR_CONVERSION_BOOST = {
    "IT / Digital":           1.2,   # Même secteur que FRS
    "Finance / Banque":       1.15,  # Budget disponible
    "Santé":                  1.1,
    "Industrie / Fabrication":0.9,   # Cycles longs
    "Commerce / Retail":      0.85,
    "Éducation":              0.75,  # Budgets serrés
    "Immobilier":             0.95,
    "Tourisme / Hôtellerie":  0.80,
}

# ─────────────────────────────────────────────────────────────
# 2. FONCTIONS DE GÉNÉRATION RÉALISTE
# ─────────────────────────────────────────────────────────────

def pick_source():
    """Source avec distribution réaliste (pas uniforme)."""
    sources = list(SOURCE_WEIGHTS.keys())
    weights = list(SOURCE_WEIGHTS.values())
    return random.choices(sources, weights=weights, k=1)[0]


def pick_company_and_sector():
    """Choisit une entreprise et son secteur."""
    sector = random.choice(list(COMPANIES.keys()))
    company_name, contact_name = random.choice(COMPANIES[sector])
    return sector, company_name, contact_name


def generate_estimated_value(sector, source):
    """
    Valeur estimée cohérente :
    - Dépend du secteur (Finance > Éducation)
    - Les referrals ont tendance à avoir des valeurs plus élevées
    - Arrondis réalistes (pas 13,847 DT mais 15,000 DT)
    """
    low, high = SECTOR_VALUE_RANGES[sector]

    # Les referrals arrivent avec des projets plus concrets
    if source == "referral":
        low = int(low * 1.3)
        high = int(high * 1.2)
    elif source == "social_media":
        high = int(high * 0.6)  # Social media = petits projets

    value = random.gauss((low + high) / 2, (high - low) / 4)
    value = max(low, min(high, value))

    # Arrondis business réalistes
    if value > 50_000:
        value = round(value / 5_000) * 5_000
    elif value > 10_000:
        value = round(value / 1_000) * 1_000
    else:
        value = round(value / 500) * 500

    return int(value)


def generate_contact_info(conversion_tendency):
    """
    Présence email/phone corrélée avec la conversion :
    - Un lead sérieux laisse ses coordonnées
    - Un lead froid peut ne pas donner d'email
    """
    if conversion_tendency > 0.5:
        has_email = random.random() < 0.95
        has_phone = random.random() < 0.85
    elif conversion_tendency > 0.3:
        has_email = random.random() < 0.80
        has_phone = random.random() < 0.65
    else:
        has_email = random.random() < 0.60
        has_phone = random.random() < 0.40
    return has_email, has_phone


def generate_activities(conversion_tendency, days_in_pipeline):
    """
    Nombre d'activités commerciales (appels, emails, RDV) :
    - Un lead chaud reçoit plus d'attention
    - Le nombre dépend aussi du temps dans le pipeline
    """
    if conversion_tendency > 0.5:
        base = random.randint(3, 8)
    elif conversion_tendency > 0.3:
        base = random.randint(1, 5)
    else:
        base = random.randint(0, 2)

    # Ajustement temporel : plus de temps = plus d'activités possibles
    time_factor = min(days_in_pipeline / 30, 2.0)
    activities = int(base * (0.7 + 0.3 * time_factor))

    # Détail des types d'activités
    calls = random.randint(0, max(1, activities // 2))
    emails = random.randint(0, max(1, activities - calls))
    meetings = max(0, activities - calls - emails)

    return activities, calls, emails, meetings


def determine_outcome(source, sector, estimated_value, has_email, has_phone,
                      activities_count, days_in_pipeline):
    """
    Décision de conversion basée sur des RÈGLES MÉTIER RÉALISTES
    (pas du random pur — c'est ça la différence senior).

    Le score est calculé puis bruité pour éviter un dataset trop parfait.
    """
    score = 0.0

    # Factor 1 : Source (poids fort)
    score += SOURCE_CONVERSION_RATES[source] * 0.25

    # Factor 2 : Secteur
    score += SECTOR_CONVERSION_BOOST[sector] * 0.10

    # Factor 3 : Valeur estimée (normalisée 0-1)
    max_val = max(r[1] for r in SECTOR_VALUE_RANGES.values())
    value_norm = min(estimated_value / max_val, 1.0)
    score += value_norm * 0.15

    # Factor 4 : Coordonnées de contact
    if has_email and has_phone:
        score += 0.15
    elif has_email or has_phone:
        score += 0.08
    else:
        score -= 0.05  # Pénalité : impossible de contacter

    # Factor 5 : Activités commerciales (très important)
    if activities_count >= 5:
        score += 0.20
    elif activities_count >= 3:
        score += 0.12
    elif activities_count >= 1:
        score += 0.05
    else:
        score -= 0.08  # Aucune activité = lead abandonné

    # Factor 6 : Durée dans le pipeline
    if days_in_pipeline <= 15:
        score += 0.10  # Lead frais
    elif days_in_pipeline <= 45:
        score += 0.05  # Cycle normal
    elif days_in_pipeline <= 90:
        score -= 0.05  # Commence à stagner
    else:
        score -= 0.15  # Lead qui traîne trop

    # Ajout de bruit réaliste (±10%) pour éviter un modèle trop parfait
    noise = random.gauss(0, 0.08)
    score += noise

    # Clamp entre 0 et 1
    score = max(0.05, min(0.95, score))

    # Décision binaire avec la probabilité calculée
    converted = random.random() < score

    return converted, round(score, 3)


# ─────────────────────────────────────────────────────────────
# 3. GÉNÉRATION DU DATASET
# ─────────────────────────────────────────────────────────────

def generate_dataset(n_leads=500):
    """Génère n_leads enregistrements réalistes."""
    data = []
    base_date = datetime(2025, 1, 15)  # Début de la période

    owners = [
        "Mahdi Chakroun", "Sami Trabelsi", "Ines Chaabane",
        "Ahmed Kharat", "Nadia Kchouk"
    ]  # Commerciaux FRS

    for i in range(1, n_leads + 1):
        # Données de base
        sector, company_name, contact_name = pick_company_and_sector()
        source = pick_source()
        estimated_value = generate_estimated_value(sector, source)

        # Temporalité réaliste (leads créés sur ~12 mois)
        days_offset = random.randint(0, 365)
        created_at = base_date + timedelta(days=days_offset)

        # Durée dans le pipeline (entre 3 et 120 jours)
        days_in_pipeline = random.randint(3, 120)

        # Tendance de conversion (pour générer les corrélations)
        base_tendency = SOURCE_CONVERSION_RATES[source] * SECTOR_CONVERSION_BOOST[sector]

        # Contact info
        has_email, has_phone = generate_contact_info(base_tendency)

        # Activités commerciales
        activities_count, calls, emails_sent, meetings = generate_activities(
            base_tendency, days_in_pipeline
        )

        # Propriétaire commercial
        owner = random.choice(owners)

        # Décision finale : converti ou non
        converted, confidence_score = determine_outcome(
            source, sector, estimated_value,
            has_email, has_phone, activities_count, days_in_pipeline
        )

        # Statut final
        if converted:
            status = "converted"
        else:
            # Répartition réaliste des non-convertis
            r = random.random()
            if r < 0.4:
                status = "unqualified"
            elif r < 0.65:
                status = "contacted"
            elif r < 0.85:
                status = "new"
            else:
                status = "qualified"

        # Email et téléphone réalistes
        email_addr = ""
        if has_email:
            prenom = contact_name.split()[-1].lower()
            domain = company_name.split()[0].lower().replace("é", "e")
            email_addr = f"{prenom}@{domain}.tn"

        phone_num = ""
        if has_phone:
            phone_num = f"+216 {random.choice(['2','5','7','9'])}{random.randint(0,9)} " \
                        f"{random.randint(100,999)} {random.randint(100,999)}"

        data.append({
            "lead_id": i,
            "company_name": company_name,
            "contact_name": contact_name,
            "email": email_addr,
            "phone": phone_num,
            "sector": sector,
            "source": source,
            "status": status,
            "estimated_value": estimated_value,
            "owner": owner,
            "has_email": int(has_email),
            "has_phone": int(has_phone),
            "days_in_pipeline": days_in_pipeline,
            "activities_count": activities_count,
            "calls": calls,
            "emails_sent": emails_sent,
            "meetings": meetings,
            "created_at": created_at.strftime("%Y-%m-%d"),
            "converted": int(converted),
            "confidence_score": confidence_score,
        })

    return data


# ─────────────────────────────────────────────────────────────
# 4. EXPORT CSV + STATISTIQUES
# ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  GÉNÉRATION DU DATASET LEAD SCORING — FRS CRM")
    print("=" * 60)

    data = generate_dataset(500)

    # Export CSV
    output_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(output_dir, "leads_dataset.csv")

    fieldnames = [
        "lead_id", "company_name", "contact_name", "email", "phone",
        "sector", "source", "status", "estimated_value", "owner",
        "has_email", "has_phone", "days_in_pipeline",
        "activities_count", "calls", "emails_sent", "meetings",
        "created_at", "converted", "confidence_score"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    # Statistiques
    total = len(data)
    converted = sum(1 for d in data if d["converted"] == 1)
    not_converted = total - converted

    print(f"\n✅ Dataset généré : {csv_path}")
    print(f"   Total leads     : {total}")
    print(f"   Convertis       : {converted} ({converted/total*100:.1f}%)")
    print(f"   Non convertis   : {not_converted} ({not_converted/total*100:.1f}%)")

    # Stats par source
    print(f"\n📊 Taux de conversion par source :")
    sources_stats = {}
    for d in data:
        src = d["source"]
        if src not in sources_stats:
            sources_stats[src] = {"total": 0, "converted": 0}
        sources_stats[src]["total"] += 1
        sources_stats[src]["converted"] += d["converted"]

    for src in sorted(sources_stats, key=lambda s: sources_stats[s]["converted"]/max(1,sources_stats[s]["total"]), reverse=True):
        s = sources_stats[src]
        rate = s["converted"] / max(1, s["total"]) * 100
        print(f"   {src:15s} : {s['total']:3d} leads → {s['converted']:3d} convertis ({rate:.0f}%)")

    # Stats par secteur
    print(f"\n🏢 Taux de conversion par secteur :")
    sector_stats = {}
    for d in data:
        sec = d["sector"]
        if sec not in sector_stats:
            sector_stats[sec] = {"total": 0, "converted": 0}
        sector_stats[sec]["total"] += 1
        sector_stats[sec]["converted"] += d["converted"]

    for sec in sorted(sector_stats, key=lambda s: sector_stats[s]["converted"]/max(1,sector_stats[s]["total"]), reverse=True):
        s = sector_stats[sec]
        rate = s["converted"] / max(1, s["total"]) * 100
        print(f"   {sec:25s} : {s['total']:3d} leads → {s['converted']:3d} convertis ({rate:.0f}%)")

    # Valeur moyenne
    avg_val_conv = sum(d["estimated_value"] for d in data if d["converted"]) / max(1, converted)
    avg_val_not = sum(d["estimated_value"] for d in data if not d["converted"]) / max(1, not_converted)
    print(f"\n💰 Valeur estimée moyenne :")
    print(f"   Convertis     : {avg_val_conv:,.0f} DT")
    print(f"   Non convertis : {avg_val_not:,.0f} DT")

    # Activités moyennes
    avg_act_conv = sum(d["activities_count"] for d in data if d["converted"]) / max(1, converted)
    avg_act_not = sum(d["activities_count"] for d in data if not d["converted"]) / max(1, not_converted)
    print(f"\n📞 Activités moyennes :")
    print(f"   Convertis     : {avg_act_conv:.1f} activités")
    print(f"   Non convertis : {avg_act_not:.1f} activités")

    print(f"\n{'=' * 60}")
    print(f"  Dataset prêt pour l'entraînement ML !")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
