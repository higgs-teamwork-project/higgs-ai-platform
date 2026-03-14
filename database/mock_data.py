from . import dataset_db


def seed_mock_data() -> None:
    """
    Insert a small set of mock donors and NGOs into the dataset database.
    Safe to call multiple times: it will not duplicate entries.
    """
    existing_donors = dataset_db.list_donors()
    existing_ngos = dataset_db.list_ngos()
    if existing_donors or existing_ngos:
        return

    # 4 donors
    dataset_db.insert_donor(
        name="European Green Fund",
        legal_form="Foundation",
        strategy="Environment and climate action funder",
        sectors=["Environment", "Climate Action"],
        regions=["Europe", "Mediterranean"],
        description="Philanthropic fund supporting grassroots environmental initiatives and climate resilience projects.",
        keywords=["sustainability", "climate", "biodiversity"],
    )
    dataset_db.insert_donor(
        name="Social Innovation Trust",
        legal_form="Foundation",
        strategy="Education and social inclusion programs",
        sectors=["Education", "Social Inclusion"],
        regions=["Greece", "Balkans"],
        description="Foundation backing innovative NGOs working on youth employability and inclusive education.",
        keywords=["youth", "education", "inclusion"],
    )
    dataset_db.insert_donor(
        name="Health Futures Foundation",
        legal_form="Foundation",
        strategy="Health and mental health initiatives",
        sectors=["Health", "Mental Health", "Wellbeing"],
        regions=["Greece", "Southeast Europe"],
        description="Funds NGOs that improve access to healthcare and mental health support in underserved communities.",
        keywords=["health", "mental health", "wellbeing", "access"],
    )
    dataset_db.insert_donor(
        name="Culture & Heritage Fund",
        legal_form="Charitable Trust",
        strategy="Culture, arts and heritage preservation",
        sectors=["Culture", "Arts", "Heritage"],
        regions=["Greece", "Mediterranean"],
        description="Supports preservation of cultural heritage, traditional arts, and community-based cultural projects.",
        keywords=["culture", "heritage", "arts", "tradition"],
    )

    # 10 NGOs
    dataset_db.insert_ngo(
        name="Green Cities Network",
        legal_form="Association",
        strategy="Urban sustainability projects",
        focus="Urban green spaces and sustainable mobility",
        sectors=["Environment", "Urban Development"],
        regions=["Athens", "Thessaloniki"],
        description="Network of local NGOs promoting urban green spaces, sustainable mobility, and community gardens.",
        keywords=["urban", "parks", "sustainability"],
    )
    dataset_db.insert_ngo(
        name="NextGen Learning Hub",
        legal_form="Non-profit",
        strategy="Youth digital skills and employability",
        focus="Digital skills training for young job seekers",
        sectors=["Education", "Youth"],
        regions=["Greece"],
        description="Non-profit providing digital skills training and mentoring for young job seekers.",
        keywords=["digital skills", "youth", "training"],
    )
    dataset_db.insert_ngo(
        name="Climate Action Greece",
        legal_form="Association",
        strategy="Climate advocacy and awareness",
        focus="Climate awareness and biodiversity protection",
        sectors=["Environment", "Climate Action"],
        regions=["Greece"],
        description="Grassroots campaigns for climate awareness, renewable energy adoption, and biodiversity protection.",
        keywords=["climate", "renewable", "biodiversity", "awareness"],
    )
    dataset_db.insert_ngo(
        name="Rural Education Initiative",
        legal_form="Non-profit",
        strategy="Rural education programs",
        focus="Education and after-school programs in rural areas",
        sectors=["Education", "Rural Development"],
        regions=["Northern Greece", "Balkans"],
        description="Brings quality education and after-school programs to remote and rural communities.",
        keywords=["education", "rural", "schools", "literacy"],
    )
    dataset_db.insert_ngo(
        name="Community Health Partners",
        legal_form="NGO",
        strategy="Community health outreach",
        focus="Mobile clinics and outreach for vulnerable groups",
        sectors=["Health", "Community"],
        regions=["Athens", "Piraeus"],
        description="Mobile clinics and health outreach for vulnerable and low-income populations.",
        keywords=["health", "clinics", "vulnerable", "access"],
    )
    dataset_db.insert_ngo(
        name="Youth Voice Collective",
        legal_form="Youth NGO",
        strategy="Youth leadership and advocacy",
        focus="Youth-led advocacy and leadership programmes",
        sectors=["Youth", "Social Inclusion", "Advocacy"],
        regions=["Greece"],
        description="Youth-led advocacy and leadership programs for marginalised young people.",
        keywords=["youth", "advocacy", "inclusion", "leadership"],
    )
    dataset_db.insert_ngo(
        name="Mediterranean Heritage Society",
        legal_form="Association",
        strategy="Cultural heritage preservation",
        focus="Traditional crafts, museums and oral history",
        sectors=["Culture", "Heritage"],
        regions=["Greece", "Crete", "Cyclades"],
        description="Preservation of traditional crafts, local museums, and oral history projects.",
        keywords=["heritage", "crafts", "museums", "tradition"],
    )
    dataset_db.insert_ngo(
        name="Mental Health First",
        legal_form="NGO",
        strategy="Community mental health support",
        focus="Crisis support and school-based mental health",
        sectors=["Mental Health", "Health"],
        regions=["Greece"],
        description="Crisis support, counselling, and stigma reduction for mental health in communities and schools.",
        keywords=["mental health", "counselling", "crisis", "stigma"],
    )
    dataset_db.insert_ngo(
        name="Reforest Greece",
        legal_form="NGO",
        strategy="Reforestation and environmental education",
        focus="Forest restoration and environmental education",
        sectors=["Environment", "Reforestation"],
        regions=["Central Greece", "Peloponnese"],
        description="Tree planting, forest restoration, and environmental education in fire-affected areas.",
        keywords=["reforestation", "forest", "environment", "education"],
    )
    dataset_db.insert_ngo(
        name="Arts for All",
        legal_form="Non-profit",
        strategy="Inclusive arts programmes",
        focus="Free arts workshops and performances",
        sectors=["Arts", "Culture", "Social Inclusion"],
        regions=["Athens", "Thessaloniki"],
        description="Free workshops and performances in theatre, music, and visual arts for underserved communities.",
        keywords=["arts", "theatre", "music", "inclusion"],
    )

