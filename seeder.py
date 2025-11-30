"""
Seeder for resources/course catalog. Generates a configurable number of realistic
course/resource entries and inserts them into MongoDB. Supports dry-run mode.

Usage:
  python seeder.py --count 500 --commit
  python seeder.py --count 100 --dry-run
"""

from database import get_db_instance, ResourceDAO, init_db, close_db
from config import settings
from datetime import datetime, timedelta
import random
import argparse
import uuid

PROVIDERS = [
    "Coursera",
    "edX",
    "Udemy",
    "Pluralsight",
    "LinkedIn Learning",
    "Khan Academy",
    "MIT OpenCourseWare",
    "Harvard Extension",
    "Fast.ai",
    "Codecademy",
]

TOPICS = [
    "Python",
    "Machine Learning",
    "Data Science",
    "Deep Learning",
    "NLP",
    "Computer Vision",
    "Statistics",
    "SQL",
    "Cloud Computing",
    "DevOps",
    "Frontend Development",
    "Backend Development",
    "MLOps",
    "Reinforcement Learning",
    "Data Engineering",
]

LEVELS = ["Beginner", "Intermediate", "Advanced"]
COURSE_TYPES = ["Course", "Specialization", "Nanodegree", "Bootcamp", "Tutorial"]

SAMPLE_TAGS = ["career-ready", "project-based", "hands-on", "certificate", "free", "paid"]


def generate_resource(i: int) -> dict:
    provider = random.choice(PROVIDERS)
    topic = random.choice(TOPICS)
    level = random.choice(LEVELS)
    ctype = random.choice(COURSE_TYPES)

    duration_weeks = random.choice([2, 4, 6, 8, 10, 12])
    hours = random.choice([5, 10, 20, 40, 60])

    title = f"{topic} for {level} Learners - {provider} ({i})"

    url_slug = f"{topic.lower().replace(' ', '-')}-{provider.lower().replace(' ', '-')}-{i}"
    url = f"https://{provider.lower().replace(' ', '')}.example/{url_slug}"

    description = (
        f"{title}: A {ctype.lower()} focusing on {topic} skills. "
        f"Covers core concepts, practical projects and assessments. "
        f"Estimated {hours} hours over {duration_weeks} weeks."
    )

    resource = {
        "resource_id": str(uuid.uuid4()),
        "title": title,
        "provider": provider,
        "topic": topic,
        "level": level,
        "type": ctype,
        "duration_weeks": duration_weeks,
        "estimated_hours": hours,
        "url": url,
        "tags": random.sample(SAMPLE_TAGS, k=random.randint(1, 3)),
        "rating": round(random.uniform(3.5, 5.0), 2),
        "created_at": datetime.utcnow(),
        "metadata": {
            "popularity_score": random.randint(10, 10000),
            "last_checked": (datetime.utcnow() - timedelta(days=random.randint(0, 90))).isoformat()
        }
    }

    return resource


def seed(count: int = 500, commit: bool = False):
    resources = [generate_resource(i + 1) for i in range(count)]

    if not commit:
        print(f"Dry-run: generated {len(resources)} resources. No DB writes performed.")
        for r in resources[:3]:
            print(r)
        return len(resources)

    # commit mode: connect to DB and insert
    init_db()
    db = get_db_instance()
    resource_dao = ResourceDAO(db)
    inserted = resource_dao.create_many(resources)
    print(f"Inserted {inserted} resources into MongoDB")
    close_db()
    return inserted


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Seed MongoDB with course resources")
    parser.add_argument("--count", type=int, default=int(settings.__dict__.get('SEEDER_COUNT', 500)), help="Number of resources to generate")
    parser.add_argument("--commit", action="store_true", help="Actually insert into DB (default is dry-run)")
    args = parser.parse_args()

    seed(count=args.count, commit=args.commit)
