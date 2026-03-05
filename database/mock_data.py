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

    # Example donors
    dataset_db.insert_donor(
        name="European Green Fund",
        sectors=["Environment", "Climate Action"],
        regions=["Europe", "Mediterranean"],
        description="Philanthropic fund supporting grassroots environmental initiatives and climate resilience projects.",
        keywords=["sustainability", "climate", "biodiversity"],
    )
    dataset_db.insert_donor(
        name="Social Innovation Trust",
        sectors=["Education", "Social Inclusion"],
        regions=["Greece", "Balkans"],
        description="Foundation backing innovative NGOs working on youth employability and inclusive education.",
        keywords=["youth", "education", "inclusion"],
    )

    # Example NGOs
    dataset_db.insert_ngo(
        name="Green Cities Network",
        sectors=["Environment", "Urban Development"],
        regions=["Athens", "Thessaloniki"],
        description="Network of local NGOs promoting urban green spaces, sustainable mobility, and community gardens.",
        keywords=["urban", "parks", "sustainability"],
    )
    dataset_db.insert_ngo(
        name="NextGen Learning Hub",
        sectors=["Education", "Youth"],
        regions=["Greece"],
        description="Non-profit providing digital skills training and mentoring for young job seekers.",
        keywords=["digital skills", "youth", "training"],
    )

