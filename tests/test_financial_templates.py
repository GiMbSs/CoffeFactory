"""
Testes automatizados para validar os templates financeiros corrigidos
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.template import Context, Template
import re


class FinancialTemplatesTestCase(TestCase):
    def setUp(self):
        """Configuração inicial dos testes"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_dashboard_template_structure(self):
        """Testa se o dashboard financeiro segue o padrão correto"""
        try:
            # Carrega o template do dashboard
            template = get_template('financial/dashboard.html')
            
            # Renderiza o template
            rendered = template.render({})
            
            # Verifica se contém elementos essenciais do padrão
            self.assertIn('Coffee Factory', rendered)
            self.assertIn('coffee-600', rendered)  # Cor do tema coffee
            self.assertIn('fas fa-chart-line', rendered)  # Font Awesome icons
            self.assertIn('gradient-card', rendered)  # Cartões com gradiente
            self.assertIn('dark:', rendered)  # Suporte ao modo escuro
            self.assertIn('x-data', rendered)  # Alpine.js
            
            # Verifica se não há loops infinitos do Alpine.js
            self.assertNotIn('x-data="{', rendered)  # Evita objetos vazios que causam loops
            
        except Exception as e:
            self.fail(f"Erro ao carregar template dashboard: {e}")

    def test_accounts_receivable_template_structure(self):
        """Testa se o template de contas a receber segue o padrão"""
        try:
            template = get_template('financial/accounts_receivable.html')
            rendered = template.render({})
            
            # Verifica padrões do projeto
            self.assertIn('Contas a Receber', rendered)
            self.assertIn('coffee-600', rendered)
            self.assertIn('fas fa-hand-holding-usd', rendered)
            self.assertIn('financial-card', rendered)
            self.assertIn('gradient-card', rendered)
            
            # Verifica Alpine.js correto
            self.assertIn('x-data="{', rendered)
            self.assertIn('showFilters:', rendered)
            self.assertIn('showCreateModal:', rendered)
            
        except Exception as e:
            self.fail(f"Erro ao carregar template accounts_receivable: {e}")

    def test_accounts_payable_template_structure(self):
        """Testa se o template de contas a pagar segue o padrão"""
        try:
            template = get_template('financial/accounts_payable.html')
            rendered = template.render({})
            
            # Verifica padrões do projeto
            self.assertIn('Contas a Pagar', rendered)
            self.assertIn('coffee-600', rendered)
            self.assertIn('fas fa-credit-card', rendered)
            self.assertIn('financial-card', rendered)
            
        except Exception as e:
            self.fail(f"Erro ao carregar template accounts_payable: {e}")

    def test_payroll_template_structure(self):
        """Testa se o template de folha de pagamento segue o padrão"""
        try:
            template = get_template('financial/payroll.html')
            rendered = template.render({})
            
            # Verifica padrões do projeto
            self.assertIn('Folha de Pagamento', rendered)
            self.assertIn('coffee-600', rendered)
            self.assertIn('fas fa-users', rendered)
            self.assertIn('financial-card', rendered)
            
        except Exception as e:
            self.fail(f"Erro ao carregar template payroll: {e}")

    def test_coffee_theme_consistency(self):
        """Verifica se todos os templates usam o tema coffee consistentemente"""
        templates = [
            'financial/dashboard.html',
            'financial/accounts_receivable.html', 
            'financial/accounts_payable.html',
            'financial/payroll.html'
        ]
        
        for template_path in templates:
            with self.subTest(template=template_path):
                try:
                    template = get_template(template_path)
                    rendered = template.render({})
                    
                    # Verifica cores do tema coffee
                    self.assertIn('coffee-600', rendered)
                    self.assertIn('coffee-400', rendered)
                    
                    # Verifica gradientes
                    self.assertIn('gradient-card', rendered)
                    
                    # Verifica suporte ao modo escuro
                    self.assertIn('dark:', rendered)
                    
                except Exception as e:
                    self.fail(f"Erro ao verificar tema coffee em {template_path}: {e}")

    def test_alpine_js_no_infinite_loops(self):
        """Verifica se não há loops infinitos do Alpine.js nos templates"""
        templates = [
            'financial/dashboard.html',
            'financial/accounts_receivable.html',
            'financial/accounts_payable.html', 
            'financial/payroll.html'
        ]
        
        for template_path in templates:
            with self.subTest(template=template_path):
                try:
                    template = get_template(template_path)
                    rendered = template.render({})
                    
                    # Verifica se não há estruturas que causam loops
                    # Procura por objetos Alpine.js mal formados
                    problematic_patterns = [
                        r'x-data="\s*{\s*}\s*"',  # Objetos vazios
                        r'x-data="\s*\{\s*\$data\s*\}\s*"',  # Referencias circulares
                        r'x-init="\s*\$watch\s*\(\s*\$data',  # Watchers em $data
                    ]
                    
                    for pattern in problematic_patterns:
                        matches = re.findall(pattern, rendered, re.IGNORECASE)
                        self.assertEqual(len(matches), 0, 
                            f"Encontrado padrão problemático em {template_path}: {pattern}")
                    
                except Exception as e:
                    self.fail(f"Erro ao verificar Alpine.js em {template_path}: {e}")

    def test_font_awesome_icons_presence(self):
        """Verifica se todos os templates têm ícones Font Awesome consistentes"""
        templates_icons = {
            'financial/dashboard.html': ['fas fa-chart-line', 'fas fa-dollar-sign'],
            'financial/accounts_receivable.html': ['fas fa-hand-holding-usd', 'fas fa-plus'],
            'financial/accounts_payable.html': ['fas fa-credit-card', 'fas fa-plus'],
            'financial/payroll.html': ['fas fa-users', 'fas fa-play']
        }
        
        for template_path, expected_icons in templates_icons.items():
            with self.subTest(template=template_path):
                try:
                    template = get_template(template_path)
                    rendered = template.render({})
                    
                    for icon in expected_icons:
                        self.assertIn(icon, rendered, 
                            f"Ícone {icon} não encontrado em {template_path}")
                        
                except Exception as e:
                    self.fail(f"Erro ao verificar ícones em {template_path}: {e}")

    def test_responsive_design_classes(self):
        """Verifica se todos os templates têm classes responsivas do TailwindCSS"""
        templates = [
            'financial/dashboard.html',
            'financial/accounts_receivable.html',
            'financial/accounts_payable.html',
            'financial/payroll.html'
        ]
        
        responsive_classes = [
            'md:grid-cols-2',
            'lg:grid-cols-4', 
            'lg:flex-row',
            'sm:flex-row',
            'md:col-span-2'
        ]
        
        for template_path in templates:
            with self.subTest(template=template_path):
                try:
                    template = get_template(template_path)
                    rendered = template.render({})
                    
                    # Verifica se pelo menos algumas classes responsivas estão presentes
                    found_responsive = False
                    for responsive_class in responsive_classes:
                        if responsive_class in rendered:
                            found_responsive = True
                            break
                    
                    self.assertTrue(found_responsive, 
                        f"Nenhuma classe responsiva encontrada em {template_path}")
                        
                except Exception as e:
                    self.fail(f"Erro ao verificar classes responsivas em {template_path}: {e}")

    def test_modal_functionality(self):
        """Verifica se os modais estão implementados corretamente com Alpine.js"""
        templates_modals = {
            'financial/accounts_receivable.html': ['showCreateModal', 'showPaymentModal'],
            'financial/accounts_payable.html': ['showCreateModal', 'showPaymentModal'],
            'financial/payroll.html': ['showProcessModal', 'showPaymentModal']
        }
        
        for template_path, expected_modals in templates_modals.items():
            with self.subTest(template=template_path):
                try:
                    template = get_template(template_path)
                    rendered = template.render({})
                    
                    for modal in expected_modals:
                        # Verifica se o modal está definido no x-data
                        self.assertIn(f'{modal}:', rendered, 
                            f"Modal {modal} não encontrado em {template_path}")
                        
                        # Verifica se há botão para abrir o modal
                        self.assertIn(f'@click="{modal} = true"', rendered,
                            f"Botão para abrir {modal} não encontrado em {template_path}")
                        
                        # Verifica se há estrutura do modal
                        self.assertIn(f'x-show="{modal}"', rendered,
                            f"Estrutura do modal {modal} não encontrada em {template_path}")
                        
                except Exception as e:
                    self.fail(f"Erro ao verificar modais em {template_path}: {e}")


class TemplateRenderingTestCase(TestCase):
    """Testes específicos para renderização dos templates"""
    
    def setUp(self):
        """Configuração inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_dashboard_renders_without_errors(self):
        """Testa se o dashboard renderiza sem erros"""
        template = Template("""
            {% extends 'base.html' %}
            {% block content %}
                <div x-data="{ chartInitialized: false }">
                    <h1 class="text-coffee-600">Dashboard Financeiro</h1>
                </div>
            {% endblock %}
        """)
        
        try:
            rendered = template.render(Context({}))
            self.assertIn('Dashboard Financeiro', rendered)
        except Exception as e:
            self.fail(f"Erro na renderização: {e}")

    def test_no_template_syntax_errors(self):
        """Verifica se não há erros de sintaxe nos templates"""
        templates = [
            'financial/dashboard.html',
            'financial/accounts_receivable.html',
            'financial/accounts_payable.html',
            'financial/payroll.html'
        ]
        
        for template_path in templates:
            with self.subTest(template=template_path):
                try:
                    template = get_template(template_path)
                    # Tenta renderizar com contexto mínimo
                    rendered = template.render({})
                    # Se chegou até aqui, não há erros de sintaxe
                    self.assertIsNotNone(rendered)
                except Exception as e:
                    self.fail(f"Erro de sintaxe em {template_path}: {e}")
