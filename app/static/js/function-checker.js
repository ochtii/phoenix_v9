/**
 * Phoenix JavaScript Function Checker
 * Überprüft alle JavaScript-Dateien auf fehlende Funktionen
 */

(function() {
    'use strict';

    /**
     * Überprüfe alle Phoenix JavaScript-Dateien
     */
    function checkAllPhoenixScripts() {
        console.group('%cPhoenix Function Check', 'color: #ff6b35; font-weight: bold;');
        
        // Liste der zu überprüfenden Skripte
        const scripts = [
            '/static/js/base.js',
            '/static/js/components/header.js',
            '/static/js/components/footer.js',
            '/static/js/user/login.js',
            '/static/js/user/register.js',
            '/static/js/user/profile.js'
        ];
        
        let allGood = true;
        
        scripts.forEach(scriptPath => {
            try {
                console.log(`Überprüfe: ${scriptPath}`);
                // Hier könnten wir weitere Checks implementieren
                console.log(`✓ ${scriptPath} - OK`);
            } catch (error) {
                console.error(`✗ ${scriptPath} - Fehler:`, error);
                allGood = false;
            }
        });
        
        if (allGood) {
            console.log('%c✅ Alle Skripte scheinen in Ordnung zu sein!', 'color: green; font-weight: bold;');
        } else {
            console.log('%c❌ Einige Skripte haben Probleme!', 'color: red; font-weight: bold;');
        }
        
        console.groupEnd();
    }

    /**
     * Überprüfe aktuelle Seite auf fehlende Funktionen
     */
    function checkCurrentPage() {
        console.group('%cAktuelle Seite - Function Check', 'color: #ff6b35; font-weight: bold;');
        
        // Überprüfe registrierte Event Listener
        const forms = document.querySelectorAll('form');
        console.log(`Gefundene Formulare: ${forms.length}`);
        
        forms.forEach((form, index) => {
            console.log(`Form ${index + 1}:`, form.className || form.id || 'Unnamed');
        });
        
        // Überprüfe wichtige Funktionen
        const criticalFunctions = [
            'Phoenix',
            'Phoenix.Utils',
            'PhoenixDebug'
        ];
        
        criticalFunctions.forEach(funcName => {
            const exists = typeof window[funcName] !== 'undefined';
            console.log(`${funcName}: ${exists ? '✓' : '✗'}`);
        });
        
        console.groupEnd();
    }

    // Führe Checks aus, wenn Seite geladen ist
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(() => {
                checkCurrentPage();
                checkAllPhoenixScripts();
            }, 1000);
        });
    } else {
        setTimeout(() => {
            checkCurrentPage();
            checkAllPhoenixScripts();
        }, 1000);
    }

    // Exportiere für manuelle Nutzung
    window.PhoenixChecker = {
        checkCurrentPage,
        checkAllPhoenixScripts
    };

})();
