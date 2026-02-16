"""
JavaScript integration for enhanced interactivity in the Smart Bus Dashboard.

This module provides JavaScript components for tooltips, animations,
accessibility features, and enhanced user interactions.
"""

from typing import Dict, List, Optional


class JavaScriptManager:
    """Manages JavaScript components and interactions for the dashboard."""
    
    def __init__(self):
        self.base_scripts = self._get_base_scripts()
        self.tooltip_scripts = self._get_tooltip_scripts()
        self.accessibility_scripts = self._get_accessibility_scripts()
        self.animation_scripts = self._get_animation_scripts()
    
    def get_complete_javascript(self, features: Optional[List[str]] = None) -> str:
        """Generate complete JavaScript based on requested features."""
        if features is None:
            features = ['base', 'tooltips', 'accessibility', 'animations']
        
        scripts = []
        
        if 'base' in features:
            scripts.append(self.base_scripts)
        if 'tooltips' in features:
            scripts.append(self.tooltip_scripts)
        if 'accessibility' in features:
            scripts.append(self.accessibility_scripts)
        if 'animations' in features:
            scripts.append(self.animation_scripts)
        
        return "\n".join(scripts)
    
    def _get_base_scripts(self) -> str:
        """Base JavaScript functionality."""
        return """
        <script>
        // Smart Bus Dashboard - Enhanced JavaScript Framework
        
        class DashboardManager {
            constructor() {
                this.initialized = false;
                this.performanceMetrics = {
                    interactionTimes: [],
                    loadTimes: [],
                    transitionTimes: []
                };
                this.init();
            }
            
            init() {
                if (this.initialized) return;
                
                this.setupEventListeners();
                this.initializePerformanceMonitoring();
                this.setupKeyboardNavigation();
                this.initializeResponsiveHandlers();
                
                this.initialized = true;
                console.log('Smart Bus Dashboard Enhanced - JavaScript Framework Loaded');
            }
            
            setupEventListeners() {
                // Global click handler for enhanced interactions
                document.addEventListener('click', (e) => {
                    this.handleInteraction(e, 'click');
                });
                
                // Global focus handler for accessibility
                document.addEventListener('focusin', (e) => {
                    this.handleFocus(e);
                });
                
                // Global keyboard handler
                document.addEventListener('keydown', (e) => {
                    this.handleKeyboard(e);
                });
                
                // Window resize handler for responsive updates
                window.addEventListener('resize', () => {
                    this.handleResize();
                });
            }
            
            handleInteraction(event, type) {
                const startTime = performance.now();
                
                // Add visual feedback
                this.addInteractionFeedback(event.target);
                
                // Track performance
                setTimeout(() => {
                    const endTime = performance.now();
                    this.recordPerformance('interaction', endTime - startTime);
                }, 0);
            }
            
            addInteractionFeedback(element) {
                // Add ripple effect for buttons and interactive elements
                if (element.classList.contains('btn') || element.classList.contains('interactive')) {
                    this.createRippleEffect(element);
                }
                
                // Add focus ring for accessibility
                element.classList.add('interaction-active');
                setTimeout(() => {
                    element.classList.remove('interaction-active');
                }, 200);
            }
            
            createRippleEffect(element) {
                const ripple = document.createElement('span');
                ripple.classList.add('ripple-effect');
                
                const rect = element.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = (event.clientX - rect.left - size / 2) + 'px';
                ripple.style.top = (event.clientY - rect.top - size / 2) + 'px';
                
                element.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            }
            
            handleFocus(event) {
                // Ensure focus is visible
                event.target.classList.add('focused');
                
                // Remove focus class when element loses focus
                event.target.addEventListener('focusout', () => {
                    event.target.classList.remove('focused');
                }, { once: true });
            }
            
            handleKeyboard(event) {
                // Handle keyboard shortcuts
                if (event.ctrlKey || event.metaKey) {
                    switch(event.key) {
                        case 'h':
                            event.preventDefault();
                            this.toggleHelp();
                            break;
                        case 'f':
                            event.preventDefault();
                            this.focusSearch();
                            break;
                        case 's':
                            event.preventDefault();
                            this.openSettings();
                            break;
                    }
                }
                
                // Handle tab navigation
                if (event.key === 'Tab') {
                    this.handleTabNavigation(event);
                }
                
                // Handle escape key
                if (event.key === 'Escape') {
                    this.handleEscape();
                }
            }
            
            handleTabNavigation(event) {
                // Ensure tab navigation stays within modal dialogs
                const modal = document.querySelector('.modal.active');
                if (modal) {
                    const focusableElements = modal.querySelectorAll(
                        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                    );
                    
                    const firstElement = focusableElements[0];
                    const lastElement = focusableElements[focusableElements.length - 1];
                    
                    if (event.shiftKey && document.activeElement === firstElement) {
                        event.preventDefault();
                        lastElement.focus();
                    } else if (!event.shiftKey && document.activeElement === lastElement) {
                        event.preventDefault();
                        firstElement.focus();
                    }
                }
            }
            
            handleResize() {
                // Update responsive components
                this.updateResponsiveComponents();
                
                // Recalculate chart dimensions
                this.updateChartDimensions();
            }
            
            updateResponsiveComponents() {
                const width = window.innerWidth;
                const body = document.body;
                
                // Update responsive classes
                body.classList.remove('mobile', 'tablet', 'desktop', 'large-desktop');
                
                if (width < 768) {
                    body.classList.add('mobile');
                } else if (width < 1024) {
                    body.classList.add('tablet');
                } else if (width < 1440) {
                    body.classList.add('desktop');
                } else {
                    body.classList.add('large-desktop');
                }
            }
            
            updateChartDimensions() {
                // Trigger Plotly resize for all charts
                const charts = document.querySelectorAll('.js-plotly-plot');
                charts.forEach(chart => {
                    if (window.Plotly) {
                        window.Plotly.Plots.resize(chart);
                    }
                });
            }
            
            initializePerformanceMonitoring() {
                // Monitor page load performance
                window.addEventListener('load', () => {
                    const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
                    this.recordPerformance('load', loadTime);
                });
                
                // Monitor Streamlit component updates
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                            this.handleComponentUpdate(mutation);
                        }
                    });
                });
                
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
            }
            
            handleComponentUpdate(mutation) {
                const startTime = performance.now();
                
                // Initialize new components
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.initializeNewComponent(node);
                    }
                });
                
                // Record update performance
                setTimeout(() => {
                    const endTime = performance.now();
                    this.recordPerformance('update', endTime - startTime);
                }, 0);
            }
            
            initializeNewComponent(element) {
                // Initialize tooltips
                const tooltipElements = element.querySelectorAll('[data-tooltip]');
                tooltipElements.forEach(el => this.initializeTooltip(el));
                
                // Initialize interactive elements
                const interactiveElements = element.querySelectorAll('.interactive');
                interactiveElements.forEach(el => this.initializeInteractive(el));
                
                // Initialize charts
                const chartElements = element.querySelectorAll('.chart-container');
                chartElements.forEach(el => this.initializeChart(el));
            }
            
            recordPerformance(type, time) {
                this.performanceMetrics[type + 'Times'] = this.performanceMetrics[type + 'Times'] || [];
                this.performanceMetrics[type + 'Times'].push(time);
                
                // Check performance thresholds
                this.checkPerformanceThresholds(type, time);
            }
            
            checkPerformanceThresholds(type, time) {
                const thresholds = {
                    interaction: 200,
                    load: 3000,
                    update: 500,
                    transition: 1000
                };
                
                if (time > thresholds[type]) {
                    console.warn(`Performance warning: ${type} took ${time}ms (threshold: ${thresholds[type]}ms)`);
                    this.reportPerformanceIssue(type, time);
                }
            }
            
            reportPerformanceIssue(type, time) {
                // Create performance issue notification
                this.showNotification(`Performance issue detected: ${type} operation took ${Math.round(time)}ms`, 'warning');
            }
            
            showNotification(message, type = 'info') {
                const notification = document.createElement('div');
                notification.className = `notification notification-${type}`;
                notification.textContent = message;
                
                document.body.appendChild(notification);
                
                // Animate in
                setTimeout(() => notification.classList.add('show'), 100);
                
                // Remove after delay
                setTimeout(() => {
                    notification.classList.remove('show');
                    setTimeout(() => notification.remove(), 300);
                }, 5000);
            }
            
            setupKeyboardNavigation() {
                // Create skip links for accessibility
                this.createSkipLinks();
                
                // Setup focus management
                this.setupFocusManagement();
            }
            
            createSkipLinks() {
                const skipLinks = document.createElement('div');
                skipLinks.className = 'skip-links';
                skipLinks.innerHTML = `
                    <a href="#main-content" class="skip-link">Skip to main content</a>
                    <a href="#navigation" class="skip-link">Skip to navigation</a>
                    <a href="#sidebar" class="skip-link">Skip to sidebar</a>
                `;
                
                document.body.insertBefore(skipLinks, document.body.firstChild);
            }
            
            setupFocusManagement() {
                // Manage focus for dynamic content
                document.addEventListener('streamlit:componentUpdate', (e) => {
                    this.manageFocusAfterUpdate(e.detail);
                });
            }
            
            manageFocusAfterUpdate(updateInfo) {
                // Restore focus to appropriate element after Streamlit updates
                const activeElement = document.activeElement;
                if (activeElement && activeElement.tagName === 'BODY') {
                    // Focus was lost, try to restore to a logical element
                    const firstFocusable = document.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
                    if (firstFocusable) {
                        firstFocusable.focus();
                    }
                }
            }
            
            // Public API methods
            toggleHelp() {
                const helpPanel = document.querySelector('.help-panel');
                if (helpPanel) {
                    helpPanel.classList.toggle('active');
                }
            }
            
            focusSearch() {
                const searchInput = document.querySelector('input[type="search"], .search-input');
                if (searchInput) {
                    searchInput.focus();
                }
            }
            
            openSettings() {
                const settingsPanel = document.querySelector('.settings-panel');
                if (settingsPanel) {
                    settingsPanel.classList.add('active');
                }
            }
            
            handleEscape() {
                // Close any open modals or panels
                const activeModals = document.querySelectorAll('.modal.active, .panel.active');
                activeModals.forEach(modal => {
                    modal.classList.remove('active');
                });
            }
        }
        
        // Initialize dashboard manager when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                window.dashboardManager = new DashboardManager();
            });
        } else {
            window.dashboardManager = new DashboardManager();
        }
        
        // CSS for JavaScript-enhanced elements
        const style = document.createElement('style');
        style.textContent = `
            .ripple-effect {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
            }
            
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
            
            .interaction-active {
                transform: scale(0.98);
                transition: transform 0.1s ease-out;
            }
            
            .focused {
                outline: 2px solid var(--primary-color, #2E86AB);
                outline-offset: 2px;
            }
            
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 16px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 10000;
                transform: translateX(100%);
                transition: transform 0.3s ease-out;
            }
            
            .notification.show {
                transform: translateX(0);
            }
            
            .notification-info {
                background: var(--primary-color, #2E86AB);
            }
            
            .notification-warning {
                background: var(--warning-color, #FFD23F);
                color: #000;
            }
            
            .notification-error {
                background: var(--error-color, #F72585);
            }
            
            .skip-links {
                position: absolute;
                top: -100px;
                left: 0;
                z-index: 10000;
            }
            
            .skip-link:focus {
                position: absolute;
                top: 10px;
                left: 10px;
                background: var(--primary-color, #2E86AB);
                color: white;
                padding: 8px 12px;
                text-decoration: none;
                border-radius: 4px;
            }
        `;
        document.head.appendChild(style);
        </script>
        """
    
    def _get_tooltip_scripts(self) -> str:
        """JavaScript for enhanced tooltip functionality."""
        return """
        <script>
        // Enhanced Tooltip System
        class TooltipManager {
            constructor() {
                this.tooltips = new Map();
                this.init();
            }
            
            init() {
                this.createTooltipContainer();
                this.setupEventListeners();
                this.initializeExistingTooltips();
            }
            
            createTooltipContainer() {
                if (document.querySelector('.tooltip-container')) return;
                
                const container = document.createElement('div');
                container.className = 'tooltip-container';
                container.setAttribute('role', 'tooltip');
                container.setAttribute('aria-hidden', 'true');
                document.body.appendChild(container);
            }
            
            setupEventListeners() {
                document.addEventListener('mouseenter', (e) => {
                    if (e.target.hasAttribute('data-tooltip')) {
                        this.showTooltip(e.target);
                    }
                }, true);
                
                document.addEventListener('mouseleave', (e) => {
                    if (e.target.hasAttribute('data-tooltip')) {
                        this.hideTooltip(e.target);
                    }
                }, true);
                
                document.addEventListener('focus', (e) => {
                    if (e.target.hasAttribute('data-tooltip')) {
                        this.showTooltip(e.target);
                    }
                }, true);
                
                document.addEventListener('blur', (e) => {
                    if (e.target.hasAttribute('data-tooltip')) {
                        this.hideTooltip(e.target);
                    }
                }, true);
            }
            
            initializeExistingTooltips() {
                const tooltipElements = document.querySelectorAll('[data-tooltip]');
                tooltipElements.forEach(el => this.initializeTooltip(el));
            }
            
            initializeTooltip(element) {
                if (this.tooltips.has(element)) return;
                
                const tooltipData = {
                    content: element.getAttribute('data-tooltip'),
                    position: element.getAttribute('data-tooltip-position') || 'top',
                    delay: parseInt(element.getAttribute('data-tooltip-delay')) || 500,
                    timeout: null
                };
                
                this.tooltips.set(element, tooltipData);
                
                // Add ARIA attributes
                element.setAttribute('aria-describedby', 'tooltip-' + this.generateId());
            }
            
            showTooltip(element) {
                const tooltipData = this.tooltips.get(element);
                if (!tooltipData) return;
                
                // Clear any existing timeout
                if (tooltipData.timeout) {
                    clearTimeout(tooltipData.timeout);
                }
                
                tooltipData.timeout = setTimeout(() => {
                    this.displayTooltip(element, tooltipData);
                }, tooltipData.delay);
            }
            
            hideTooltip(element) {
                const tooltipData = this.tooltips.get(element);
                if (!tooltipData) return;
                
                // Clear timeout
                if (tooltipData.timeout) {
                    clearTimeout(tooltipData.timeout);
                    tooltipData.timeout = null;
                }
                
                // Hide tooltip
                const container = document.querySelector('.tooltip-container');
                container.style.opacity = '0';
                container.setAttribute('aria-hidden', 'true');
                
                setTimeout(() => {
                    container.style.display = 'none';
                }, 200);
            }
            
            displayTooltip(element, tooltipData) {
                const container = document.querySelector('.tooltip-container');
                const rect = element.getBoundingClientRect();
                
                // Set content
                container.textContent = tooltipData.content;
                container.style.display = 'block';
                
                // Calculate position
                const position = this.calculatePosition(rect, container, tooltipData.position);
                
                // Apply position
                container.style.left = position.x + 'px';
                container.style.top = position.y + 'px';
                
                // Show tooltip
                container.style.opacity = '1';
                container.setAttribute('aria-hidden', 'false');
            }
            
            calculatePosition(elementRect, tooltip, position) {
                const tooltipRect = tooltip.getBoundingClientRect();
                const margin = 8;
                
                let x, y;
                
                switch (position) {
                    case 'top':
                        x = elementRect.left + (elementRect.width - tooltipRect.width) / 2;
                        y = elementRect.top - tooltipRect.height - margin;
                        break;
                    case 'bottom':
                        x = elementRect.left + (elementRect.width - tooltipRect.width) / 2;
                        y = elementRect.bottom + margin;
                        break;
                    case 'left':
                        x = elementRect.left - tooltipRect.width - margin;
                        y = elementRect.top + (elementRect.height - tooltipRect.height) / 2;
                        break;
                    case 'right':
                        x = elementRect.right + margin;
                        y = elementRect.top + (elementRect.height - tooltipRect.height) / 2;
                        break;
                    default:
                        x = elementRect.left + (elementRect.width - tooltipRect.width) / 2;
                        y = elementRect.top - tooltipRect.height - margin;
                }
                
                // Ensure tooltip stays within viewport
                x = Math.max(margin, Math.min(x, window.innerWidth - tooltipRect.width - margin));
                y = Math.max(margin, Math.min(y, window.innerHeight - tooltipRect.height - margin));
                
                return { x, y };
            }
            
            generateId() {
                return Math.random().toString(36).substr(2, 9);
            }
        }
        
        // Initialize tooltip manager
        window.tooltipManager = new TooltipManager();
        
        // Add tooltip styles
        const tooltipStyle = document.createElement('style');
        tooltipStyle.textContent = `
            .tooltip-container {
                position: fixed;
                background: var(--text-primary, #2D3748);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                z-index: 10000;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s ease-out;
                max-width: 300px;
                word-wrap: break-word;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
        `;
        document.head.appendChild(tooltipStyle);
        </script>
        """
    
    def _get_accessibility_scripts(self) -> str:
        """JavaScript for accessibility enhancements."""
        return """
        <script>
        // Accessibility Enhancement Manager
        class AccessibilityManager {
            constructor() {
                this.announcements = [];
                this.init();
            }
            
            init() {
                this.createLiveRegions();
                this.setupKeyboardTraps();
                this.initializeARIA();
                this.setupFocusManagement();
            }
            
            createLiveRegions() {
                // Create polite live region
                const politeRegion = document.createElement('div');
                politeRegion.setAttribute('aria-live', 'polite');
                politeRegion.setAttribute('aria-atomic', 'true');
                politeRegion.className = 'live-region';
                politeRegion.id = 'live-region-polite';
                document.body.appendChild(politeRegion);
                
                // Create assertive live region
                const assertiveRegion = document.createElement('div');
                assertiveRegion.setAttribute('aria-live', 'assertive');
                assertiveRegion.setAttribute('aria-atomic', 'true');
                assertiveRegion.className = 'live-region';
                assertiveRegion.id = 'live-region-assertive';
                document.body.appendChild(assertiveRegion);
            }
            
            announce(message, priority = 'polite') {
                const regionId = priority === 'assertive' ? 'live-region-assertive' : 'live-region-polite';
                const region = document.getElementById(regionId);
                
                if (region) {
                    // Clear previous announcement
                    region.textContent = '';
                    
                    // Add new announcement after a brief delay
                    setTimeout(() => {
                        region.textContent = message;
                    }, 100);
                    
                    // Clear announcement after it's been read
                    setTimeout(() => {
                        region.textContent = '';
                    }, 5000);
                }
            }
            
            setupKeyboardTraps() {
                // Handle modal focus trapping
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'Tab') {
                        const modal = document.querySelector('.modal.active');
                        if (modal) {
                            this.trapFocus(e, modal);
                        }
                    }
                });
            }
            
            trapFocus(event, container) {
                const focusableElements = container.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                
                const firstElement = focusableElements[0];
                const lastElement = focusableElements[focusableElements.length - 1];
                
                if (event.shiftKey) {
                    if (document.activeElement === firstElement) {
                        event.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        event.preventDefault();
                        firstElement.focus();
                    }
                }
            }
            
            initializeARIA() {
                // Add ARIA labels to unlabeled interactive elements
                const unlabeledButtons = document.querySelectorAll('button:not([aria-label]):not([aria-labelledby])');
                unlabeledButtons.forEach(button => {
                    const text = button.textContent.trim();
                    if (text) {
                        button.setAttribute('aria-label', text);
                    }
                });
                
                // Add ARIA roles to semantic elements
                const charts = document.querySelectorAll('.chart-container');
                charts.forEach(chart => {
                    chart.setAttribute('role', 'img');
                    if (!chart.hasAttribute('aria-label')) {
                        const title = chart.querySelector('.chart-title');
                        if (title) {
                            chart.setAttribute('aria-label', `Chart: ${title.textContent}`);
                        }
                    }
                });
                
                // Add ARIA landmarks
                this.addLandmarks();
            }
            
            addLandmarks() {
                // Main content area
                const mainContent = document.querySelector('.main-content, main');
                if (mainContent && !mainContent.hasAttribute('role')) {
                    mainContent.setAttribute('role', 'main');
                }
                
                // Navigation areas
                const navElements = document.querySelectorAll('.nav-tabs, .navigation');
                navElements.forEach(nav => {
                    if (!nav.hasAttribute('role')) {
                        nav.setAttribute('role', 'navigation');
                    }
                });
                
                // Sidebar
                const sidebar = document.querySelector('.sidebar, .sidebar-enhanced');
                if (sidebar && !sidebar.hasAttribute('role')) {
                    sidebar.setAttribute('role', 'complementary');
                }
            }
            
            setupFocusManagement() {
                // Manage focus for dynamic content updates
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'childList') {
                            mutation.addedNodes.forEach(node => {
                                if (node.nodeType === Node.ELEMENT_NODE) {
                                    this.initializeNewAccessibilityFeatures(node);
                                }
                            });
                        }
                    });
                });
                
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
            }
            
            initializeNewAccessibilityFeatures(element) {
                // Add ARIA labels to new interactive elements
                const newButtons = element.querySelectorAll('button:not([aria-label])');
                newButtons.forEach(button => {
                    const text = button.textContent.trim();
                    if (text) {
                        button.setAttribute('aria-label', text);
                    }
                });
                
                // Add roles to new charts
                const newCharts = element.querySelectorAll('.chart-container');
                newCharts.forEach(chart => {
                    chart.setAttribute('role', 'img');
                    const title = chart.querySelector('.chart-title');
                    if (title) {
                        chart.setAttribute('aria-label', `Chart: ${title.textContent}`);
                    }
                });
            }
            
            // Public API methods
            announcePageChange(pageName) {
                this.announce(`Navigated to ${pageName}`, 'polite');
            }
            
            announceDataUpdate(description) {
                this.announce(`Data updated: ${description}`, 'polite');
            }
            
            announceError(errorMessage) {
                this.announce(`Error: ${errorMessage}`, 'assertive');
            }
            
            announceSuccess(successMessage) {
                this.announce(`Success: ${successMessage}`, 'polite');
            }
        }
        
        // Initialize accessibility manager
        window.accessibilityManager = new AccessibilityManager();
        </script>
        """
    
    def _get_animation_scripts(self) -> str:
        """JavaScript for smooth animations and transitions."""
        return """
        <script>
        // Animation and Transition Manager
        class AnimationManager {
            constructor() {
                this.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
                this.init();
            }
            
            init() {
                this.setupMotionPreferences();
                this.initializeAnimations();
            }
            
            setupMotionPreferences() {
                // Listen for motion preference changes
                window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
                    this.reducedMotion = e.matches;
                    this.updateAnimationSettings();
                });
            }
            
            updateAnimationSettings() {
                if (this.reducedMotion) {
                    document.body.classList.add('reduced-motion');
                } else {
                    document.body.classList.remove('reduced-motion');
                }
            }
            
            initializeAnimations() {
                // Intersection Observer for scroll animations
                this.setupScrollAnimations();
                
                // Page transition animations
                this.setupPageTransitions();
                
                // Chart animation enhancements
                this.setupChartAnimations();
            }
            
            setupScrollAnimations() {
                if (this.reducedMotion) return;
                
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('animate-in');
                        }
                    });
                }, {
                    threshold: 0.1,
                    rootMargin: '0px 0px -50px 0px'
                });
                
                // Observe cards and charts
                const animatableElements = document.querySelectorAll('.dashboard-card, .chart-container');
                animatableElements.forEach(el => {
                    el.classList.add('animate-on-scroll');
                    observer.observe(el);
                });
            }
            
            setupPageTransitions() {
                // Smooth transitions between sections
                document.addEventListener('streamlit:sectionChange', (e) => {
                    this.animatePageTransition(e.detail.from, e.detail.to);
                });
            }
            
            animatePageTransition(fromSection, toSection) {
                if (this.reducedMotion) return;
                
                const mainContent = document.querySelector('.main-content, main');
                if (mainContent) {
                    mainContent.classList.add('transitioning');
                    
                    setTimeout(() => {
                        mainContent.classList.remove('transitioning');
                    }, 300);
                }
            }
            
            setupChartAnimations() {
                // Enhanced chart loading animations
                const chartObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            this.animateChart(entry.target);
                        }
                    });
                }, { threshold: 0.5 });
                
                const charts = document.querySelectorAll('.chart-container');
                charts.forEach(chart => chartObserver.observe(chart));
            }
            
            animateChart(chartContainer) {
                if (this.reducedMotion) return;
                
                const plotlyDiv = chartContainer.querySelector('.js-plotly-plot');
                if (plotlyDiv && window.Plotly) {
                    // Add entrance animation to Plotly charts
                    const layout = plotlyDiv.layout || {};
                    layout.transition = {
                        duration: 500,
                        easing: 'cubic-in-out'
                    };
                    
                    window.Plotly.relayout(plotlyDiv, layout);
                }
            }
            
            // Public API methods
            fadeIn(element, duration = 300) {
                if (this.reducedMotion) {
                    element.style.opacity = '1';
                    return Promise.resolve();
                }
                
                return new Promise(resolve => {
                    element.style.opacity = '0';
                    element.style.transition = `opacity ${duration}ms ease-out`;
                    
                    requestAnimationFrame(() => {
                        element.style.opacity = '1';
                        setTimeout(resolve, duration);
                    });
                });
            }
            
            slideIn(element, direction = 'up', duration = 300) {
                if (this.reducedMotion) {
                    return Promise.resolve();
                }
                
                return new Promise(resolve => {
                    const transforms = {
                        up: 'translateY(20px)',
                        down: 'translateY(-20px)',
                        left: 'translateX(20px)',
                        right: 'translateX(-20px)'
                    };
                    
                    element.style.transform = transforms[direction];
                    element.style.opacity = '0';
                    element.style.transition = `transform ${duration}ms ease-out, opacity ${duration}ms ease-out`;
                    
                    requestAnimationFrame(() => {
                        element.style.transform = 'translate(0)';
                        element.style.opacity = '1';
                        setTimeout(resolve, duration);
                    });
                });
            }
        }
        
        // Initialize animation manager
        window.animationManager = new AnimationManager();
        
        // Add animation styles
        const animationStyle = document.createElement('style');
        animationStyle.textContent = `
            .animate-on-scroll {
                opacity: 0;
                transform: translateY(20px);
                transition: opacity 0.6s ease-out, transform 0.6s ease-out;
            }
            
            .animate-in {
                opacity: 1 !important;
                transform: translateY(0) !important;
            }
            
            .transitioning {
                opacity: 0.7;
                transform: scale(0.98);
                transition: opacity 0.3s ease-out, transform 0.3s ease-out;
            }
            
            .reduced-motion * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
            
            .reduced-motion .animate-on-scroll {
                opacity: 1;
                transform: none;
            }
        `;
        document.head.appendChild(animationStyle);
        </script>
        """


# Global JavaScript manager instance
javascript_manager = JavaScriptManager()