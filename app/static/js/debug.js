/**
 * Phoenix Debug Utilities
 * Debugging-Hilfsfunktionen für die Entwicklung
 */

window.PhoenixDebug = (function() {
    'use strict';

    // Debug-Status
    let debugEnabled = false;

    /**
     * Aktiviere Debug-Modus
     */
    function enable() {
        debugEnabled = true;
        console.log('%cPhoenix Debug Mode aktiviert', 'color: #ff6b35; font-weight: bold;');
        console.log('%cVerfügbare Befehle:', 'color: #666; font-weight: bold;');
        console.log('  debug.status()      - Zeige System-Status');
        console.log('  debug.testComponents() - Teste alle Komponenten');
        console.log('  debug.checkElement(selector) - Prüfe DOM-Element');
        console.log('  debug.watchDOM()    - Überwache DOM-Änderungen');
        console.log('  debug.disable()     - Debug-Modus deaktivieren');
    }

    /**
     * Deaktiviere Debug-Modus  
     */
    function disable() {
        debugEnabled = false;
        console.log('%cPhoenix Debug Mode deaktiviert', 'color: #666; font-weight: bold;');
    }

    /**
     * Debug-Log mit Zeitstempel
     */
    function log(message, data = null) {
        if (!debugEnabled) return;
        
        const timestamp = new Date().toLocaleTimeString();
        console.log(`%c[Phoenix Debug ${timestamp}]%c ${message}`, 
                   'color: #ff6b35; font-weight: bold;', 
                   'color: inherit;', data || '');
    }

    /**
     * Überprüfe DOM-Element-Verfügbarkeit
     */
    function checkElement(selector, context = document) {
        const element = context.querySelector(selector);
        const exists = !!element;
        
        log(`Element "${selector}": ${exists ? '✓ Gefunden' : '✗ Nicht gefunden'}`, element);
        
        return element;
    }

    /**
     * Überprüfe mehrere DOM-Elemente
     */
    function checkElements(selectors, context = document) {
        const results = {};
        
        log('=== DOM Element Check ===');
        selectors.forEach(selector => {
            results[selector] = checkElement(selector, context);
        });
        log('=== Ende DOM Element Check ===');
        
        return results;
    }

    /**
     * Überwache DOM-Änderungen
     */
    function watchDOM(callback = null) {
        if (!debugEnabled) return;
        
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    log('DOM-Änderung erkannt:', mutation.addedNodes);
                    if (callback) callback(mutation);
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        log('DOM-Überwachung gestartet');
        return observer;
    }

    /**
     * Überprüfe JavaScript-Fehler
     */
    function watchErrors() {
        try {
            window.addEventListener('error', function(event) {
                if (!debugEnabled) return;
                
                console.group('%cJavaScript Fehler erkannt:', 'color: red; font-weight: bold;');
                console.error('Datei:', event.filename || 'Unbekannt');
                console.error('Zeile:', event.lineno || 'Unbekannt');
                console.error('Spalte:', event.colno || 'Unbekannt');
                console.error('Fehler:', event.error || event.message);
                console.error('Message:', event.message || 'Keine Nachricht');
                console.error('Stack:', event.error && event.error.stack ? event.error.stack : 'Kein Stack verfügbar');
                console.groupEnd();
            });

            window.addEventListener('unhandledrejection', function(event) {
                if (!debugEnabled) return;
                
                console.group('%cUnbehandelte Promise Rejection:', 'color: red; font-weight: bold;');
                console.error('Grund:', event.reason);
                console.error('Promise:', event.promise);
                console.groupEnd();
            });

            log('Fehler-Überwachung aktiviert');
        } catch (error) {
            console.warn('Phoenix Debug: Fehler-Überwachung konnte nicht aktiviert werden:', error);
        }
    }

    /**
     * Zeige Phoenix-Status
     */
    function status() {
        try {
            console.group('%cPhoenix Status Report', 'color: #ff6b35; font-size: 16px; font-weight: bold;');
            
            // Phoenix Objekt
            console.log('Phoenix Objekt:', typeof window.Phoenix !== 'undefined' ? window.Phoenix : 'Nicht verfügbar');
            
            // DOM Readiness
            console.log('DOM Status:', document.readyState);
            console.log('URL:', window.location.href);
            console.log('User Agent:', navigator.userAgent.substring(0, 100) + '...');
            
            // Wichtige Elemente
            const elements = [
                'header', 'nav', 'main', 'footer',
                '.navbar', '.container', '.btn'
            ];
            
            console.log('=== DOM Elemente ===');
            elements.forEach(selector => {
                try {
                    const element = document.querySelector(selector);
                    console.log(`${selector}:`, element ? '✓' : '✗', element || '');
                } catch (e) {
                    console.log(`${selector}: ✗ Fehler - ${e.message}`);
                }
            });
            
            // JavaScript Bibliotheken
            console.log('=== JavaScript Bibliotheken ===');
            console.log('jQuery:', typeof $ !== 'undefined' ? `✓ ${$.fn ? $.fn.jquery : 'Version unbekannt'}` : '✗');
            console.log('Bootstrap:', typeof bootstrap !== 'undefined' ? '✓' : '✗');
            
            // Event Listeners (nur verfügbar in Chrome DevTools)
            try {
                if (typeof getEventListeners !== 'undefined') {
                    console.log('Event Listeners auf window:', getEventListeners(window));
                } else {
                    console.log('Event Listeners: DevTools Console erforderlich (getEventListeners nicht verfügbar)');
                }
            } catch (e) {
                console.log('Event Listeners: Nicht verfügbar außerhalb der DevTools');
            }
            
            console.groupEnd();
        } catch (error) {
            console.error('Fehler im Status Report:', error);
        }
    }

    /**
     * Teste alle Phoenix-Komponenten
     */
    function testComponents() {
        log('=== Phoenix Komponenten Test ===');
        
        // Teste Phoenix Utils
        if (window.Phoenix && window.Phoenix.Utils) {
            log('Phoenix.Utils: ✓ Verfügbar');
            
            // Teste Toast
            try {
                window.Phoenix.Utils.showToast('Debug Test', 'info');
                log('Toast-Funktion: ✓ Funktioniert');
            } catch (e) {
                log('Toast-Funktion: ✗ Fehler - ' + e.message);
            }
        } else {
            log('Phoenix.Utils: ✗ Nicht verfügbar');
        }
        
        // Teste andere Komponenten
        const components = ['Header', 'Footer', 'Navigation'];
        components.forEach(comp => {
            log(`${comp} Komponente: ${document.querySelector(`.${comp.toLowerCase()}`) ? '✓' : '✗'}`);
        });
        
        log('=== Ende Komponenten Test ===');
    }

    /**
     * Safe querySelector mit Error Handling
     */
    function safeQuery(selector, context = document) {
        try {
            const element = context.querySelector(selector);
            log(`Safe Query "${selector}": ${element ? '✓' : '✗'}`);
            return element;
        } catch (error) {
            log(`Safe Query "${selector}": ✗ Fehler - ${error.message}`);
            return null;
        }
    }

    /**
     * Safe querySelectorAll mit Error Handling
     */
    function safeQueryAll(selector, context = document) {
        try {
            const elements = context.querySelectorAll(selector);
            log(`Safe Query All "${selector}": ${elements.length} Elemente gefunden`);
            return elements;
        } catch (error) {
            log(`Safe Query All "${selector}": ✗ Fehler - ${error.message}`);
            return [];
        }
    }

    // Automatisch in Development-Modus aktivieren (sicher)
    try {
        if (window.location.hostname === 'localhost' || 
            window.location.hostname === '127.0.0.1' ||
            window.location.hostname.includes('dev') ||
            (window.Phoenix && window.Phoenix.debug === true)) {
            
            enable();
            watchErrors();
            
            // Status nach DOM-Load
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', function() {
                    setTimeout(status, 100);
                });
            } else {
                setTimeout(status, 100);
            }
        }
    } catch (error) {
        console.warn('Phoenix Debug: Automatische Aktivierung fehlgeschlagen:', error);
    }

    // Public API
    return {
        enable,
        disable,
        log,
        checkElement,
        checkElements,
        watchDOM,
        watchErrors,
        status,
        testComponents,
        safeQuery,
        safeQueryAll
    };

})();

// Konsolenhelfer
if (typeof window !== 'undefined') {
    window.debug = window.PhoenixDebug;
}
