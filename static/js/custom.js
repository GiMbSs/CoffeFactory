/**
 * Coffee Factory Management System - Custom JavaScript
 * Enhanced functionality and user experience improvements
 */

(function() {
    'use strict';

    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeComponents();
        initializeDataTables();
        initializeFormValidation();
        initializeTooltips();
        initializeModals();
        initializeKeyboardShortcuts();
    });

    /**
     * Initialize all components
     */
    function initializeComponents() {
        // Auto-focus first form input
        const firstInput = document.querySelector('form input:not([type="hidden"]):not([readonly]):not([disabled])');
        if (firstInput) {
            firstInput.focus();
        }

        // Initialize loading states
        initializeLoadingStates();
        
        // Initialize confirmation dialogs
        initializeConfirmationDialogs();
        
        // Initialize auto-save functionality
        initializeAutoSave();
        
        // Initialize search functionality
        initializeSearch();
        
        // Initialize quick actions
        initializeQuickActions();
    }

    /**
     * Initialize loading states for forms and buttons
     */
    function initializeLoadingStates() {
        // Add loading state to form submissions
        const forms = document.querySelectorAll('form[data-loading="true"]');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
                if (submitButton && !form.dataset.skipLoading) {
                    const originalText = submitButton.textContent || submitButton.value;
                    const loadingText = submitButton.dataset.loadingText || 'Processando...';
                    
                    submitButton.disabled = true;
                    if (submitButton.tagName === 'BUTTON') {
                        submitButton.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i>${loadingText}`;
                    } else {
                        submitButton.value = loadingText;
                    }
                    
                    // Store original text for potential restoration
                    submitButton.dataset.originalText = originalText;
                }
            });
        });

        // Add loading state to async action buttons
        const actionButtons = document.querySelectorAll('[data-async-action]');
        actionButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                if (!button.disabled) {
                    const originalHtml = button.innerHTML;
                    const loadingText = button.dataset.loadingText || 'Carregando...';
                    
                    button.disabled = true;
                    button.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i>${loadingText}`;
                    button.dataset.originalHtml = originalHtml;
                }
            });
        });
    }

    /**
     * Initialize confirmation dialogs
     */
    function initializeConfirmationDialogs() {
        const confirmButtons = document.querySelectorAll('[data-confirm]');
        confirmButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                const message = button.dataset.confirm || 'Tem certeza que deseja continuar?';
                const title = button.dataset.confirmTitle || 'Confirmar ação';
                
                e.preventDefault();
                showConfirmDialog(title, message, () => {
                    // If it's a link, navigate to href
                    if (button.tagName === 'A' && button.href) {
                        window.location.href = button.href;
                    }
                    // If it's a form button, submit the form
                    else if (button.form) {
                        button.form.submit();
                    }
                    // If it has a data-action, execute it
                    else if (button.dataset.action) {
                        executeAction(button.dataset.action, button);
                    }
                });
            });
        });
    }

    /**
     * Show confirmation dialog
     */
    function showConfirmDialog(title, message, onConfirm, onCancel) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50';
        modal.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">${title}</h3>
                <p class="text-gray-600 dark:text-gray-400 mb-6">${message}</p>
                <div class="flex justify-end space-x-3">
                    <button class="btn btn-secondary cancel-btn">Cancelar</button>
                    <button class="btn btn-danger confirm-btn">Confirmar</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Handle confirm
        modal.querySelector('.confirm-btn').addEventListener('click', () => {
            document.body.removeChild(modal);
            if (onConfirm) onConfirm();
        });

        // Handle cancel
        modal.querySelector('.cancel-btn').addEventListener('click', () => {
            document.body.removeChild(modal);
            if (onCancel) onCancel();
        });

        // Handle backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
                if (onCancel) onCancel();
            }
        });

        // Handle escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                document.body.removeChild(modal);
                if (onCancel) onCancel();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    }

    /**
     * Initialize auto-save functionality
     */
    function initializeAutoSave() {
        const autoSaveForms = document.querySelectorAll('[data-auto-save]');
        autoSaveForms.forEach(form => {
            const interval = parseInt(form.dataset.autoSaveInterval) || 30000; // 30 seconds default
            let timeoutId;

            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('input', () => {
                    clearTimeout(timeoutId);
                    timeoutId = setTimeout(() => {
                        autoSaveForm(form);
                    }, interval);
                });
            });
        });
    }

    /**
     * Auto-save form data
     */
    function autoSaveForm(form) {
        const formData = new FormData(form);
        const saveUrl = form.dataset.autoSaveUrl || form.action;
        
        // Add auto-save indicator
        formData.append('auto_save', 'true');
        
        fetch(saveUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': CoffeeFactory.getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAutoSaveIndicator('Rascunho salvo automaticamente');
            }
        })
        .catch(error => {
            console.error('Auto-save failed:', error);
        });
    }

    /**
     * Show auto-save indicator
     */
    function showAutoSaveIndicator(message) {
        const indicator = document.createElement('div');
        indicator.className = 'fixed bottom-4 left-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 animate-fade-in';
        indicator.textContent = message;
        
        document.body.appendChild(indicator);
        
        setTimeout(() => {
            indicator.style.opacity = '0';
            setTimeout(() => {
                if (indicator.parentNode) {
                    document.body.removeChild(indicator);
                }
            }, 300);
        }, 2000);
    }

    /**
     * Initialize search functionality
     */
    function initializeSearch() {
        const searchInputs = document.querySelectorAll('[data-search]');
        searchInputs.forEach(input => {
            let timeoutId;
            input.addEventListener('input', function() {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => {
                    performSearch(input);
                }, 300);
            });
        });
    }

    /**
     * Perform search
     */
    function performSearch(input) {
        const query = input.value.trim();
        const target = input.dataset.searchTarget;
        const minLength = parseInt(input.dataset.searchMinLength) || 2;
        
        if (query.length < minLength && query.length > 0) {
            return;
        }
        
        if (target) {
            const targetElement = document.querySelector(target);
            if (targetElement) {
                filterContent(targetElement, query);
            }
        }
    }

    /**
     * Filter content based on search query
     */
    function filterContent(container, query) {
        const items = container.querySelectorAll('[data-searchable]');
        
        items.forEach(item => {
            const searchText = item.textContent.toLowerCase();
            const matches = query === '' || searchText.includes(query.toLowerCase());
            
            if (matches) {
                item.style.display = '';
                item.classList.remove('hidden');
            } else {
                item.style.display = 'none';
                item.classList.add('hidden');
            }
        });
        
        // Show "no results" message if needed
        updateNoResultsMessage(container, items, query);
    }

    /**
     * Update no results message
     */
    function updateNoResultsMessage(container, items, query) {
        const visibleItems = Array.from(items).filter(item => !item.classList.contains('hidden'));
        let noResultsEl = container.querySelector('.no-results-message');
        
        if (visibleItems.length === 0 && query !== '') {
            if (!noResultsEl) {
                noResultsEl = document.createElement('div');
                noResultsEl.className = 'no-results-message text-center py-8 text-gray-500 dark:text-gray-400';
                noResultsEl.innerHTML = `
                    <i class="fas fa-search text-4xl mb-4"></i>
                    <p class="text-lg font-medium">Nenhum resultado encontrado</p>
                    <p class="text-sm">Tente ajustar sua pesquisa</p>
                `;
                container.appendChild(noResultsEl);
            }
            noResultsEl.classList.remove('hidden');
        } else if (noResultsEl) {
            noResultsEl.classList.add('hidden');
        }
    }

    /**
     * Initialize quick actions
     */
    function initializeQuickActions() {
        // Quick edit functionality
        const quickEditButtons = document.querySelectorAll('[data-quick-edit]');
        quickEditButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = button.dataset.quickEdit;
                const targetElement = document.querySelector(`[data-quick-edit-target="${targetId}"]`);
                
                if (targetElement) {
                    toggleQuickEdit(targetElement);
                }
            });
        });
    }

    /**
     * Toggle quick edit mode
     */
    function toggleQuickEdit(element) {
        const isEditing = element.dataset.editing === 'true';
        
        if (isEditing) {
            // Save changes
            saveQuickEdit(element);
        } else {
            // Enter edit mode
            enterQuickEditMode(element);
        }
    }

    /**
     * Enter quick edit mode
     */
    function enterQuickEditMode(element) {
        const originalText = element.textContent.trim();
        const inputType = element.dataset.editType || 'text';
        
        let input;
        if (inputType === 'textarea') {
            input = document.createElement('textarea');
            input.className = 'form-textarea w-full';
        } else {
            input = document.createElement('input');
            input.type = inputType;
            input.className = 'form-input w-full';
        }
        
        input.value = originalText;
        element.dataset.originalText = originalText;
        element.innerHTML = '';
        element.appendChild(input);
        element.dataset.editing = 'true';
        
        input.focus();
        input.select();
        
        // Handle save on Enter (for input) or Ctrl+Enter (for textarea)
        input.addEventListener('keydown', (e) => {
            if ((inputType !== 'textarea' && e.key === 'Enter') || 
                (inputType === 'textarea' && e.key === 'Enter' && e.ctrlKey)) {
                e.preventDefault();
                saveQuickEdit(element);
            } else if (e.key === 'Escape') {
                cancelQuickEdit(element);
            }
        });
        
        // Handle save on blur
        input.addEventListener('blur', () => {
            setTimeout(() => saveQuickEdit(element), 100);
        });
    }

    /**
     * Save quick edit
     */
    function saveQuickEdit(element) {
        const input = element.querySelector('input, textarea');
        if (!input) return;
        
        const newValue = input.value.trim();
        const originalText = element.dataset.originalText;
        
        if (newValue !== originalText) {
            // Perform save operation
            const saveUrl = element.dataset.saveUrl;
            const fieldName = element.dataset.fieldName;
            
            if (saveUrl && fieldName) {
                const formData = new FormData();
                formData.append(fieldName, newValue);
                formData.append('csrfmiddlewaretoken', CoffeeFactory.getCsrfToken());
                
                fetch(saveUrl, {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        element.textContent = newValue;
                        CoffeeFactory.showToast('Alteração salva com sucesso', 'success', 3000);
                    } else {
                        element.textContent = originalText;
                        CoffeeFactory.showToast('Erro ao salvar alteração', 'error');
                    }
                })
                .catch(error => {
                    element.textContent = originalText;
                    CoffeeFactory.showToast('Erro de conexão', 'error');
                    console.error('Quick edit save failed:', error);
                });
            } else {
                element.textContent = newValue;
            }
        } else {
            element.textContent = originalText;
        }
        
        element.dataset.editing = 'false';
        delete element.dataset.originalText;
    }

    /**
     * Cancel quick edit
     */
    function cancelQuickEdit(element) {
        const originalText = element.dataset.originalText;
        element.textContent = originalText;
        element.dataset.editing = 'false';
        delete element.dataset.originalText;
    }

    /**
     * Initialize data tables
     */
    function initializeDataTables() {
        const tables = document.querySelectorAll('[data-table="sortable"]');
        tables.forEach(table => {
            makeTableSortable(table);
        });
    }

    /**
     * Make table sortable
     */
    function makeTableSortable(table) {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.classList.add('select-none');
            
            // Add sort icon
            const icon = document.createElement('i');
            icon.className = 'fas fa-sort ml-2 text-gray-400';
            header.appendChild(icon);
            
            header.addEventListener('click', () => {
                sortTable(table, header);
            });
        });
    }

    /**
     * Sort table
     */
    function sortTable(table, header) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const columnIndex = Array.from(header.parentNode.children).indexOf(header);
        const sortType = header.dataset.sort || 'string';
        const currentSort = header.dataset.sortDirection || 'none';
        
        let newSort;
        if (currentSort === 'none' || currentSort === 'desc') {
            newSort = 'asc';
        } else {
            newSort = 'desc';
        }
        
        // Reset all other headers
        table.querySelectorAll('th[data-sort]').forEach(th => {
            const icon = th.querySelector('i');
            if (th !== header) {
                th.dataset.sortDirection = 'none';
                icon.className = 'fas fa-sort ml-2 text-gray-400';
            }
        });
        
        // Update current header
        header.dataset.sortDirection = newSort;
        const icon = header.querySelector('i');
        icon.className = `fas fa-sort-${newSort === 'asc' ? 'up' : 'down'} ml-2 text-gray-600 dark:text-gray-300`;
        
        // Sort rows
        rows.sort((a, b) => {
            const aVal = a.cells[columnIndex].textContent.trim();
            const bVal = b.cells[columnIndex].textContent.trim();
            
            let comparison = 0;
            if (sortType === 'number') {
                comparison = parseFloat(aVal) - parseFloat(bVal);
            } else if (sortType === 'date') {
                comparison = new Date(aVal) - new Date(bVal);
            } else {
                comparison = aVal.localeCompare(bVal);
            }
            
            return newSort === 'asc' ? comparison : -comparison;
        });
        
        // Reorder DOM
        rows.forEach(row => tbody.appendChild(row));
    }

    /**
     * Initialize form validation
     */
    function initializeFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!validateForm(form)) {
                    e.preventDefault();
                }
            });
            
            // Real-time validation
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    validateField(input);
                });
                input.addEventListener('input', () => {
                    clearFieldError(input);
                });
            });
        });
    }

    /**
     * Validate form
     */
    function validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            if (!validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    /**
     * Validate field
     */
    function validateField(field) {
        const rules = field.dataset.validate ? field.dataset.validate.split('|') : [];
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';
        
        for (let rule of rules) {
            const [ruleName, ruleValue] = rule.split(':');
            
            switch (ruleName) {
                case 'required':
                    if (!value) {
                        isValid = false;
                        errorMessage = 'Este campo é obrigatório';
                    }
                    break;
                case 'min':
                    if (value.length < parseInt(ruleValue)) {
                        isValid = false;
                        errorMessage = `Mínimo de ${ruleValue} caracteres`;
                    }
                    break;
                case 'max':
                    if (value.length > parseInt(ruleValue)) {
                        isValid = false;
                        errorMessage = `Máximo de ${ruleValue} caracteres`;
                    }
                    break;
                case 'email':
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (value && !emailRegex.test(value)) {
                        isValid = false;
                        errorMessage = 'Email inválido';
                    }
                    break;
                case 'numeric':
                    if (value && !/^\d+$/.test(value)) {
                        isValid = false;
                        errorMessage = 'Apenas números são permitidos';
                    }
                    break;
            }
            
            if (!isValid) break;
        }
        
        if (isValid) {
            clearFieldError(field);
        } else {
            showFieldError(field, errorMessage);
        }
        
        return isValid;
    }

    /**
     * Show field error
     */
    function showFieldError(field, message) {
        clearFieldError(field);
        
        field.classList.add('border-red-500', 'focus:ring-red-500');
        
        const error = document.createElement('div');
        error.className = 'field-error text-red-500 text-sm mt-1';
        error.textContent = message;
        
        field.parentNode.insertBefore(error, field.nextSibling);
    }

    /**
     * Clear field error
     */
    function clearFieldError(field) {
        field.classList.remove('border-red-500', 'focus:ring-red-500');
        
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }

    /**
     * Initialize tooltips
     */
    function initializeTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            let tooltip;
            
            element.addEventListener('mouseenter', () => {
                tooltip = createTooltip(element);
            });
            
            element.addEventListener('mouseleave', () => {
                if (tooltip) {
                    tooltip.remove();
                    tooltip = null;
                }
            });
        });
    }

    /**
     * Create tooltip
     */
    function createTooltip(element) {
        const text = element.dataset.tooltip;
        const position = element.dataset.tooltipPosition || 'top';
        
        const tooltip = document.createElement('div');
        tooltip.className = 'absolute z-50 px-2 py-1 text-sm text-white bg-gray-900 rounded shadow-lg pointer-events-none';
        tooltip.textContent = text;
        
        document.body.appendChild(tooltip);
        
        const elementRect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        let left, top;
        
        switch (position) {
            case 'top':
                left = elementRect.left + (elementRect.width / 2) - (tooltipRect.width / 2);
                top = elementRect.top - tooltipRect.height - 8;
                break;
            case 'bottom':
                left = elementRect.left + (elementRect.width / 2) - (tooltipRect.width / 2);
                top = elementRect.bottom + 8;
                break;
            case 'left':
                left = elementRect.left - tooltipRect.width - 8;
                top = elementRect.top + (elementRect.height / 2) - (tooltipRect.height / 2);
                break;
            case 'right':
                left = elementRect.right + 8;
                top = elementRect.top + (elementRect.height / 2) - (tooltipRect.height / 2);
                break;
        }
        
        tooltip.style.left = Math.max(8, Math.min(left, window.innerWidth - tooltipRect.width - 8)) + 'px';
        tooltip.style.top = Math.max(8, top) + 'px';
        
        return tooltip;
    }

    /**
     * Initialize modals
     */
    function initializeModals() {
        const modalTriggers = document.querySelectorAll('[data-modal]');
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.dataset.modal;
                const modal = document.querySelector(`#${modalId}`);
                if (modal) {
                    showModal(modal);
                }
            });
        });
        
        // Close modals on backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                hideModal(e.target.querySelector('.modal-content').closest('.modal'));
            }
        });
        
        // Close modals on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal.show');
                if (openModal) {
                    hideModal(openModal);
                }
            }
        });
    }

    /**
     * Show modal
     */
    function showModal(modal) {
        modal.classList.add('show');
        document.body.classList.add('overflow-hidden');
        
        // Focus first input
        const firstInput = modal.querySelector('input:not([type="hidden"]), textarea, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }

    /**
     * Hide modal
     */
    function hideModal(modal) {
        modal.classList.remove('show');
        document.body.classList.remove('overflow-hidden');
    }

    /**
     * Initialize keyboard shortcuts
     */
    function initializeKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + S to save form
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                const form = document.querySelector('form');
                if (form) {
                    form.requestSubmit();
                }
            }
            
            // Escape to close modals/dropdowns
            if (e.key === 'Escape') {
                // Close any open dropdowns
                document.querySelectorAll('[x-show]').forEach(element => {
                    if (element.style.display !== 'none') {
                        element.dispatchEvent(new Event('click.outside'));
                    }
                });
            }
            
            // Ctrl/Cmd + / to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === '/') {
                e.preventDefault();
                const searchInput = document.querySelector('input[type="search"], input[data-search]');
                if (searchInput) {
                    searchInput.focus();
                }
            }
        });
    }

    /**
     * Execute custom action
     */
    function executeAction(actionName, element) {
        switch (actionName) {
            case 'refresh':
                window.location.reload();
                break;
            case 'back':
                window.history.back();
                break;
            case 'print':
                window.print();
                break;
            default:
                console.warn('Unknown action:', actionName);
        }
    }

    // Export utilities to global scope
    window.CoffeeFactoryUI = {
        showConfirmDialog,
        showModal,
        hideModal,
        validateForm,
        validateField,
        showFieldError,
        clearFieldError,
        performSearch,
        filterContent
    };

})();