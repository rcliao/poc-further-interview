import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from openai import OpenAI
from sales_agent.models import CommunityKnowledge


class Command(BaseCommand):
    help = 'Seed the knowledge base with ACME Senior Living facts and embeddings'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting knowledge base seeding...'))

        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.stdout.write(self.style.ERROR('OPENAI_API_KEY not set in environment'))
            return

        client = OpenAI(api_key=api_key)

        # Load knowledge data
        data_file = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'acme_knowledge.json'
        self.stdout.write(f'Loading data from: {data_file}')

        with open(data_file, 'r') as f:
            knowledge_items = json.load(f)

        self.stdout.write(f'Found {len(knowledge_items)} knowledge items')

        # Clear existing knowledge
        deleted_count = CommunityKnowledge.objects.all().count()
        CommunityKnowledge.objects.all().delete()
        self.stdout.write(f'Deleted {deleted_count} existing knowledge items')

        # Create embeddings and save
        created_count = 0
        for item in knowledge_items:
            try:
                # Generate embedding using OpenAI
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=item['content'],
                    dimensions=1536
                )
                embedding = response.data[0].embedding

                # Create knowledge entry
                CommunityKnowledge.objects.create(
                    category=item['category'],
                    content=item['content'],
                    metadata=item['metadata'],
                    embedding=embedding
                )
                created_count += 1
                self.stdout.write(f'  ✓ Created: {item["category"]} - {item["content"][:50]}...')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error creating {item["category"]}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSeeding complete! Created {created_count}/{len(knowledge_items)} knowledge items')
        )
