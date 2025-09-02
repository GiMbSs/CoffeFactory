"""
Management command para popular dados de demonstração.
Execute com: python manage.py populate_demo
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import os
import sys

# Adicionar o diretório scripts ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

try:
    from populate_demo_data import DemoDataPopulator
except ImportError:
    DemoDataPopulator = None

User = get_user_model()


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de demonstração'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force populate even if data already exists',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING('🚀 Iniciando populate de dados de demonstração...')
        )

        if DemoDataPopulator:
            populator = DemoDataPopulator()
            populator.run()
        else:
            self.stdout.write(
                self.style.ERROR('❌ Erro: Não foi possível importar DemoDataPopulator')
            )
            return

        self.stdout.write(
            self.style.SUCCESS('✅ Populate concluído com sucesso!')
        )
