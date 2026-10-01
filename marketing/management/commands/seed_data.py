import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from marketing.models import MarketingMember, MarketingLink, Visit, Lead

class Command(BaseCommand):
    help = "Populate realistic seed data for Marketing Tracking Module demonstration."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding demo data..."))

        # Clear existing
        Visit.objects.all().delete()
        Lead.objects.all().delete()
        MarketingLink.objects.all().delete()
        MarketingMember.objects.all().delete()

        # 1. Create Members
        members_data = [
            {"name": "Anika Reddy", "email": "anika@company.com", "member_id": "MEM101"},
            {"name": "Rajesh Kumar", "email": "rajesh@company.com", "member_id": "MEM102"},
            {"name": "Priya Sharma", "email": "priya@company.com", "member_id": "MEM103"},
            {"name": "David Miller", "email": "david@company.com", "member_id": "MEM104"},
        ]

        created_members = []
        for m in members_data:
            member = MarketingMember.objects.create(**m)
            created_members.append(member)
            self.stdout.write(f"Created member: {member}")

        # 2. Create Marketing Links
        platforms = ['instagram', 'whatsapp', 'linkedin', 'facebook', 'email']
        campaigns = ['september_promo', 'autumn_special', 'webinar_launch', 'direct_reach']

        created_links = []
        
        # Ensure Anika has active top links as in prompt example
        anika = created_members[0] # Anika
        sample_links_spec = [
            (anika, 'instagram', 'september_promo', 'ANI101'),
            (anika, 'whatsapp', 'autumn_special', 'ANI102'),
            (anika, 'linkedin', 'webinar_launch', 'ANI103'),
            (created_members[1], 'facebook', 'september_promo', 'RAJ101'), # Rajesh
            (created_members[1], 'instagram', 'direct_reach', 'RAJ102'),
            (created_members[2], 'email', 'september_promo', 'PRI101'), # Priya
            (created_members[2], 'whatsapp', 'autumn_special', 'PRI102'),
            (created_members[3], 'linkedin', 'webinar_launch', 'DAV101'), # David
        ]

        for mem, plat, camp, code in sample_links_spec:
            link = MarketingLink.objects.create(
                member=mem,
                platform=plat,
                campaign=camp,
                short_code=code,
                destination_url='/book/'
            )
            created_links.append(link)

        # 3. Create Visits & Leads
        sample_names = [
            ("Aarav Patel", "aarav@gmail.com", "+91 98765 43210"),
            ("Siddharth Verma", "siddharth@yahoo.com", "+91 91234 56789"),
            ("Neha Gupta", "neha@outlook.com", "+91 99887 76655"),
            ("Rohan Mehta", "rohan@techcorp.io", "+91 98112 23344"),
            ("Kavya Nair", "kavya@designstudio.com", "+91 97766 55443"),
            ("Vikram Singh", "vikram@enterprise.org", "+91 96543 21098"),
            ("Sneha Iyer", "sneha@gmail.com", "+91 95432 10987"),
            ("Amit Shah", "amit@financial.com", "+91 94321 09876"),
            ("Tanvi Joshi", "tanvi@healthplus.com", "+91 93210 98765"),
            ("Karan Kapoor", "karan@startup.co", "+91 92109 87654"),
            ("Sarah Jenkins", "sarah@globaltech.com", "+1 415 555 0192"),
            ("Michael Brown", "mbrown@solutions.net", "+1 212 555 0144"),
            ("Pooja Choudhury", "pooja@services.in", "+91 91098 76543"),
            ("Rahul Deshmukh", "rahul@buildcon.com", "+91 90987 65432"),
            ("Meera Pillai", "meera@creative.org", "+91 89876 54321"),
        ]

        now = timezone.now()

        # Seed visits and leads with realistic distributions
        for link in created_links:
            # Determine visit count based on member
            if link.member.name.startswith("Anika"):
                num_visits = random.randint(35, 50)
                num_leads = random.randint(12, 18)
            elif link.member.name.startswith("Rajesh"):
                num_visits = random.randint(25, 35)
                num_leads = random.randint(8, 12)
            elif link.member.name.startswith("Priya"):
                num_visits = random.randint(20, 30)
                num_leads = random.randint(6, 10)
            else:
                num_visits = random.randint(15, 25)
                num_leads = random.randint(4, 8)

            # Generate Visits
            for i in range(num_visits):
                visit_time = now - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23), minutes=random.randint(0, 59))
                Visit.objects.create(
                    link=link,
                    ip_address=f"192.168.1.{random.randint(1, 254)}",
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    timestamp=visit_time
                )

            # Generate Leads
            statuses = ['new', 'qualified', 'booked']
            weights = [0.35, 0.40, 0.25]

            for i in range(num_leads):
                name, email, phone = random.choice(sample_names)
                # Randomize email unique suffix
                email_parts = email.split('@')
                unique_email = f"{email_parts[0]}+{random.randint(100, 999)}@{email_parts[1]}"

                status = random.choices(statuses, weights=weights)[0]
                lead_time = now - timedelta(days=random.randint(0, 10), hours=random.randint(0, 23))

                Lead.objects.create(
                    link=link,
                    name=name,
                    email=unique_email,
                    phone=phone,
                    status=status,
                    created_at=lead_time
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded demo data!"))
