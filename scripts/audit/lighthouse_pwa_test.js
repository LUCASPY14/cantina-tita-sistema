#!/usr/bin/env node

/**
 * Lighthouse PWA Testing Script
 * Sprint 8 - Testing y QA
 * 
 * Este script ejecuta Lighthouse para auditar el PWA
 * Targets:
 * - PWA Score: >90
 * - Performance: >90
 * - Accessibility: >88
 * - Best Practices: >95
 * - SEO: >90
 */

const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');
const fs = require('fs');
const path = require('path');

// Configuración
const CONFIG = {
  urls: [
    'http://localhost:8000/pos/',           // POS Dashboard (PWA principal)
    'http://localhost:8000/pos/venta/',     // POS Venta
    'http://localhost:8000/portal/dashboard/', // Portal Padres
  ],
  output: {
    dir: path.join(__dirname, '../../docs/sprints/lighthouse-reports'),
    format: ['html', 'json']
  },
  thresholds: {
    performance: 90,
    accessibility: 88,
    'best-practices': 95,
    seo: 90,
    pwa: 90
  }
};

// Configuración de Lighthouse
const lighthouseConfig = {
  extends: 'lighthouse:default',
  settings: {
    onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo', 'pwa'],
    formFactor: 'mobile',
    throttling: {
      rttMs: 40,
      throughputKbps: 10 * 1024,
      cpuSlowdownMultiplier: 1,
    },
    screenEmulation: {
      mobile: true,
      width: 412,
      height: 823,
      deviceScaleFactor: 2.625,
      disabled: false,
    }
  }
};

// Función para ejecutar Lighthouse
async function runLighthouse(url) {
  console.log(`\n🔍 Auditando: ${url}`);
  
  const chrome = await chromeLauncher.launch({
    chromeFlags: ['--headless', '--no-sandbox']
  });
  
  try {
    const runnerResult = await lighthouse(url, {
      port: chrome.port,
      output: CONFIG.output.format,
      logLevel: 'info',
    }, lighthouseConfig);

    // Guardar reportes
    const urlSlug = url.replace(/[^a-z0-9]/gi, '_');
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    
    // Crear directorio si no existe
    if (!fs.existsSync(CONFIG.output.dir)) {
      fs.mkdirSync(CONFIG.output.dir, { recursive: true });
    }

    // Guardar HTML
    const htmlPath = path.join(CONFIG.output.dir, `${urlSlug}_${timestamp}.html`);
    fs.writeFileSync(htmlPath, runnerResult.report[0]);
    
    // Guardar JSON
    const jsonPath = path.join(CONFIG.output.dir, `${urlSlug}_${timestamp}.json`);
    fs.writeFileSync(jsonPath, runnerResult.report[1]);

    console.log(`✅ Reportes guardados en: ${CONFIG.output.dir}`);
    
    return {
      url,
      scores: runnerResult.lhr.categories,
      htmlPath,
      jsonPath
    };
  } finally {
    await chrome.kill();
  }
}

// Función para verificar scores contra thresholds
function checkThresholds(results) {
  console.log('\n📊 RESUMEN DE SCORES\n');
  console.log('=' .repeat(80));
  
  let allPassed = true;
  
  results.forEach(result => {
    console.log(`\n🔗 ${result.url}`);
    console.log('-'.repeat(80));
    
    Object.entries(result.scores).forEach(([category, data]) => {
      const score = Math.round(data.score * 100);
      const threshold = CONFIG.thresholds[category.toLowerCase()] || 0;
      const passed = score >= threshold;
      const icon = passed ? '✅' : '❌';
      
      if (!passed) allPassed = false;
      
      console.log(`  ${icon} ${data.title.padEnd(20)} ${String(score).padStart(3)}% (threshold: ${threshold}%)`);
    });
  });
  
  console.log('\n' + '='.repeat(80));
  console.log(`\n${allPassed ? '✅ TODOS LOS TESTS PASARON' : '❌ ALGUNOS TESTS FALLARON'}\n`);
  
  return allPassed;
}

// Función para generar reporte markdown
function generateMarkdownReport(results) {
  let markdown = `# Lighthouse PWA Testing Report

**Fecha**: ${new Date().toLocaleString('es-PY')}  
**Sprint**: Sprint 8 - Testing y QA

---

## Resumen Ejecutivo

`;

  // Tabla de scores
  markdown += `| URL | Performance | Accessibility | Best Practices | SEO | PWA |\n`;
  markdown += `|-----|-------------|---------------|----------------|-----|-----|\n`;
  
  results.forEach(result => {
    const urlShort = result.url.replace('http://localhost:8000', '');
    const scores = result.scores;
    markdown += `| ${urlShort} | `;
    markdown += `${Math.round(scores.performance.score * 100)}% | `;
    markdown += `${Math.round(scores.accessibility.score * 100)}% | `;
    markdown += `${Math.round(scores['best-practices'].score * 100)}% | `;
    markdown += `${Math.round(scores.seo.score * 100)}% | `;
    markdown += `${Math.round(scores.pwa.score * 100)}% |\n`;
  });

  markdown += `\n---\n\n## Thresholds\n\n`;
  Object.entries(CONFIG.thresholds).forEach(([category, threshold]) => {
    markdown += `- **${category}**: >${threshold}%\n`;
  });

  markdown += `\n---\n\n## Reportes Detallados\n\n`;
  results.forEach(result => {
    markdown += `### ${result.url}\n\n`;
    markdown += `- [Reporte HTML](${path.relative(path.join(__dirname, '../../docs/sprints'), result.htmlPath)})\n`;
    markdown += `- [Datos JSON](${path.relative(path.join(__dirname, '../../docs/sprints'), result.jsonPath)})\n\n`;
  });

  // Guardar markdown
  const mdPath = path.join(CONFIG.output.dir, `LIGHTHOUSE_REPORT_${new Date().toISOString().split('T')[0]}.md`);
  fs.writeFileSync(mdPath, markdown);
  console.log(`\n📄 Reporte Markdown: ${mdPath}\n`);
}

// Main
async function main() {
  console.log('🚀 Lighthouse PWA Testing - Sprint 8');
  console.log('=' .repeat(80));
  
  const results = [];
  
  for (const url of CONFIG.urls) {
    try {
      const result = await runLighthouse(url);
      results.push(result);
    } catch (error) {
      console.error(`❌ Error auditando ${url}:`, error.message);
      console.log('⚠️  Asegúrate de que el servidor Django está corriendo en http://localhost:8000');
    }
  }
  
  if (results.length > 0) {
    const allPassed = checkThresholds(results);
    generateMarkdownReport(results);
    
    process.exit(allPassed ? 0 : 1);
  } else {
    console.error('\n❌ No se pudieron ejecutar las auditorías');
    console.log('💡 Inicia el servidor Django con: python backend/manage.py runserver');
    process.exit(1);
  }
}

// Ejecutar
if (require.main === module) {
  main().catch(error => {
    console.error('❌ Error fatal:', error);
    process.exit(1);
  });
}

module.exports = { runLighthouse, checkThresholds };
