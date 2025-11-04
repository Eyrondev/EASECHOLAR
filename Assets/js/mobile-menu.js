/**
 * EASECHOLAR - Mobile Menu Handler
 * Version: 1.0.0
 * 
 * Handles mobile sidebar toggle, overlay, and responsive behavior
 */

(function() {
    'use strict';

    // Initialize mobile menu on DOM load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileMenu);
    } else {
        initMobileMenu();
    }

    function initMobileMenu() {
        // Create mobile menu toggle button
        createMobileMenuToggle();
        
        // Create mobile overlay
        createMobileOverlay();
        
        // Add event listeners
        setupEventListeners();
        
        // Handle window resize
        handleResize();
        window.addEventListener('resize', handleResize);
    }

    function createMobileMenuToggle() {
        // Check if toggle already exists
        if (document.querySelector('.mobile-menu-toggle')) {
            return;
        }

        // Only create toggle if sidebar exists
        const sidebar = document.querySelector('aside[id="sidebar"], #sidebar-container > aside, .fixed.left-0.top-0.w-64');
        if (!sidebar) {
            return;
        }

        // Create toggle button
        const toggle = document.createElement('button');
        toggle.className = 'mobile-menu-toggle';
        toggle.setAttribute('aria-label', 'Toggle Mobile Menu');
        toggle.innerHTML = '<i class="fas fa-bars"></i>';
        
        // Insert into body
        document.body.insertBefore(toggle, document.body.firstChild);
    }

    function createMobileOverlay() {
        // Check if overlay already exists
        if (document.querySelector('.mobile-overlay')) {
            return;
        }

        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'mobile-overlay';
        overlay.setAttribute('aria-hidden', 'true');
        
        // Insert into body
        document.body.appendChild(overlay);
    }

    function setupEventListeners() {
        const toggle = document.querySelector('.mobile-menu-toggle');
        const overlay = document.querySelector('.mobile-overlay');
        const sidebar = document.querySelector('aside[id="sidebar"], #sidebar-container > aside, .fixed.left-0.top-0.w-64');

        if (!toggle || !overlay || !sidebar) {
            return;
        }

        // Toggle menu on button click
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleMenu();
        });

        // Close menu on overlay click
        overlay.addEventListener('click', function() {
            closeMenu();
        });

        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && isMenuOpen()) {
                closeMenu();
            }
        });

        // Close menu when clicking links in sidebar (on mobile)
        const sidebarLinks = sidebar.querySelectorAll('a');
        sidebarLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    closeMenu();
                }
            });
        });
    }

    function toggleMenu() {
        const sidebar = document.querySelector('aside[id="sidebar"], #sidebar-container > aside, .fixed.left-0.top-0.w-64');
        const overlay = document.querySelector('.mobile-overlay');
        const toggle = document.querySelector('.mobile-menu-toggle');

        if (!sidebar || !overlay || !toggle) {
            return;
        }

        const isOpen = sidebar.classList.contains('mobile-open');

        if (isOpen) {
            closeMenu();
        } else {
            openMenu();
        }
    }

    function openMenu() {
        const sidebar = document.querySelector('aside[id="sidebar"], #sidebar-container > aside, .fixed.left-0.top-0.w-64');
        const overlay = document.querySelector('.mobile-overlay');
        const toggle = document.querySelector('.mobile-menu-toggle');

        if (!sidebar || !overlay || !toggle) {
            return;
        }

        sidebar.classList.add('mobile-open');
        overlay.classList.add('active');
        toggle.innerHTML = '<i class="fas fa-times"></i>';
        
        // Prevent body scroll when menu is open
        document.body.style.overflow = 'hidden';
        
        // Set aria attributes
        toggle.setAttribute('aria-expanded', 'true');
        overlay.setAttribute('aria-hidden', 'false');
    }

    function closeMenu() {
        const sidebar = document.querySelector('aside[id="sidebar"], #sidebar-container > aside, .fixed.left-0.top-0.w-64');
        const overlay = document.querySelector('.mobile-overlay');
        const toggle = document.querySelector('.mobile-menu-toggle');

        if (!sidebar || !overlay || !toggle) {
            return;
        }

        sidebar.classList.remove('mobile-open');
        overlay.classList.remove('active');
        toggle.innerHTML = '<i class="fas fa-bars"></i>';
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Set aria attributes
        toggle.setAttribute('aria-expanded', 'false');
        overlay.setAttribute('aria-hidden', 'true');
    }

    function isMenuOpen() {
        const sidebar = document.querySelector('aside[id="sidebar"], #sidebar-container > aside, .fixed.left-0.top-0.w-64');
        return sidebar && sidebar.classList.contains('mobile-open');
    }

    function handleResize() {
        // Close menu when resizing to desktop
        if (window.innerWidth > 768 && isMenuOpen()) {
            closeMenu();
        }
    }

    // Expose functions globally if needed
    window.EASECHOLAR = window.EASECHOLAR || {};
    window.EASECHOLAR.mobile = {
        openMenu: openMenu,
        closeMenu: closeMenu,
        toggleMenu: toggleMenu,
        isMenuOpen: isMenuOpen
    };

})();
