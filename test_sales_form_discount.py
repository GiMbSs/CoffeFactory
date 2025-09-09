"""
Test script to verify sales form discount field validation.
"""
import time
from playwright.sync_api import sync_playwright, expect


def test_sales_form_discount():
    """Test that sales form allows empty discount field."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Navigate to the sales order creation form
            page.goto("http://127.0.0.1:8000/sales/orders/new/")
            
            # Wait for the page to load
            page.wait_for_load_state("networkidle")
            print("✓ Página carregada com sucesso")

            # Fill in only required fields, leaving discount empty
            # First, need to create/select a customer if required
            customer_select = page.query_selector("select[name='customer']")
            if customer_select:
                options = customer_select.query_selector_all("option[value]:not([value=''])")
                if options:
                    customer_value = options[0].get_attribute("value")
                    page.select_option(customer_select, customer_value)
                    print(f"✓ Cliente selecionado: {customer_value}")

            # Fill order date
            order_date_input = page.query_selector("input[name='order_date']")
            if order_date_input:
                page.fill("input[name='order_date']", "2025-09-04")
                print("✓ Data do pedido preenchida")

            # Leave discount field empty (default behavior)
            discount_field = page.query_selector("input[name='discount_percentage']")
            if discount_field:
                # Clear the field to ensure it's empty
                page.fill("input[name='discount_percentage']", "")
                print("✓ Campo desconto deixado vazio")

            # Fill other required fields if they exist
            delivery_date_input = page.query_selector("input[name='delivery_date']")
            if delivery_date_input:
                page.fill("input[name='delivery_date']", "2025-09-10")
                print("✓ Data de entrega preenchida")

            # Leave order number empty to test auto-generation
            order_number_field = page.query_selector("input[name='order_number']")
            if order_number_field:
                page.fill("input[name='order_number']", "")
                print("✓ Número do pedido deixado vazio para geração automática")

            # Try to submit the form
            submit_button = page.query_selector("button[type='submit'], input[type='submit']")
            if submit_button:
                print("Tentando enviar formulário...")
                submit_button.click()
                
                # Wait a moment to see if there are validation errors
                time.sleep(2)
                
                # Check for validation errors
                error_messages = page.query_selector_all(".text-red-600, .text-red-400, .alert-danger, .error")
                
                discount_errors = []
                order_number_errors = []
                other_errors = []
                
                for error in error_messages:
                    error_text = error.text_content().lower()
                    if "desconto" in error_text or "discount" in error_text:
                        discount_errors.append(error_text)
                    elif "número" in error_text or "pedido" in error_text or "order" in error_text:
                        order_number_errors.append(error_text)
                    else:
                        other_errors.append(error_text)
                
                if discount_errors:
                    print(f"✗ Ainda há erros de desconto: {discount_errors}")
                    return False
                else:
                    print("✓ Nenhum erro de validação no campo desconto")
                
                if order_number_errors:
                    print(f"! Erros no número do pedido (pode ser esperado se ainda for obrigatório): {order_number_errors}")
                else:
                    print("✓ Nenhum erro no número do pedido")
                
                if other_errors:
                    print(f"! Outros erros encontrados: {other_errors}")
                
                # Check if form was submitted successfully or if it's still on the form page
                current_url = page.url
                if "/new/" in current_url and error_messages:
                    print("Formulário ainda na página de criação devido a erros de validação")
                else:
                    print("✓ Formulário pode ter sido enviado com sucesso")
                
                return len(discount_errors) == 0

        except Exception as e:
            print(f"Erro durante o teste: {e}")
            # Take a screenshot for debugging
            page.screenshot(path="sales_form_test_error.png")
            return False
            
        finally:
            browser.close()


if __name__ == "__main__":
    print("Iniciando teste de validação do campo desconto no formulário de vendas...")
    success = test_sales_form_discount()
    if success:
        print("✓ Teste passou: Campo desconto não está mais obrigatório")
    else:
        print("✗ Teste falhou: Ainda há problemas com o campo desconto")
    print("Teste concluído.")
