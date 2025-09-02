#!/usr/bin/env python3
"""
Script para testar a API do Sistema de Gestão da Fábrica de Coadores de Café
"""

import urllib.request
import urllib.error
import json


def test_api_endpoint(url, description):
    """Testa um endpoint da API"""
    print(f"\n=== Testando: {description} ===")
    print(f"URL: {url}")
    
    try:
        with urllib.request.urlopen(url) as response:
            status_code = response.getcode()
            content = response.read().decode('utf-8')
            
            print(f"Status: {status_code}")
            print(f"Content-Type: {response.getheader('Content-Type')}")
            
            try:
                data = json.loads(content)
                print(f"JSON Data: {json.dumps(data, indent=2)[:500]}...")
            except json.JSONDecodeError:
                print(f"Raw Content: {content[:200]}...")
                
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        error_content = e.read().decode('utf-8')
        print(f"Error Content: {error_content}")
        
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        
    except Exception as e:
        print(f"Unexpected Error: {e}")


def main():
    """Função principal para testar vários endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    # Lista de endpoints para testar
    endpoints = [
        (f"{base_url}/api/v1/suppliers/", "Lista de Fornecedores"),
        (f"{base_url}/api/v1/categories/", "Lista de Categorias"),
        (f"{base_url}/api/v1/materials/", "Lista de Materiais"),
        (f"{base_url}/api/v1/products/", "Lista de Produtos"),
        (f"{base_url}/api/v1/employees/", "Lista de Funcionários"),
        (f"{base_url}/api/v1/customers/", "Lista de Clientes"),
        (f"{base_url}/api/v1/recipes/", "Lista de Receitas"),
        (f"{base_url}/api/v1/production-orders/", "Lista de Ordens de Produção"),
        (f"{base_url}/api/v1/sales-orders/", "Lista de Pedidos de Venda"),
        (f"{base_url}/api/v1/accounts-payable/", "Lista de Contas a Pagar"),
        (f"{base_url}/api/v1/accounts-receivable/", "Lista de Contas a Receber"),
        (f"{base_url}/api/v1/payroll/", "Lista de Folha de Pagamento"),
        (f"{base_url}/api/v1/stock-movements/", "Lista de Movimentações de Estoque"),
    ]
    
    # Endpoints de estatísticas
    stats_endpoints = [
        (f"{base_url}/api/v1/suppliers/statistics/", "Estatísticas de Fornecedores"),
        (f"{base_url}/api/v1/categories/statistics/", "Estatísticas de Categorias"),
        (f"{base_url}/api/v1/products/statistics/", "Estatísticas de Produtos"),
        (f"{base_url}/api/v1/employees/statistics/", "Estatísticas de Funcionários"),
    ]
    
    print("🧪 TESTE DA API - Sistema de Gestão da Fábrica de Coadores")
    print("=" * 60)
    
    # Testa endpoints principais
    for url, description in endpoints:
        test_api_endpoint(url, description)
    
    # Testa endpoints de estatísticas
    print("\n" + "=" * 60)
    print("📊 TESTANDO ENDPOINTS DE ESTATÍSTICAS")
    print("=" * 60)
    
    for url, description in stats_endpoints:
        test_api_endpoint(url, description)
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 60)


if __name__ == "__main__":
    main()
