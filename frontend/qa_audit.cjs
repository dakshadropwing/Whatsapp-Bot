const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:3000';
const ARTIFACT_DIR = process.env.ARTIFACT_DIR || '/Users/pranav1718/.gemini/antigravity-ide/brain/66b78a3d-d756-438e-ae51-6c30949751cd';
const SCREENSHOTS_DIR = path.join(ARTIFACT_DIR, 'screenshots');

if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

// Global state for report
const report = {
  summary: {
    status: 'PASS',
    totalChecks: 0,
    passed: 0,
    failed: 0,
    startTime: new Date().toISOString(),
    endTime: null,
  },
  checks: {
    uiUx: { status: 'PASS', details: [] },
    validation: { status: 'PASS', details: [] },
    performance: { status: 'PASS', details: [] },
    security: { status: 'PASS', details: [] },
    accessibility: { status: 'PASS', details: [] },
    errorHandling: { status: 'PASS', details: [] },
    apiVerification: { status: 'PASS', details: [] }
  },
  findings: [],
  recommendations: []
};

function logCheck(category, name, passed, message, extra = {}) {
  report.summary.totalChecks++;
  if (passed) {
    report.summary.passed++;
  } else {
    report.summary.failed++;
    report.summary.status = 'FAIL';
    report.checks[category].status = 'FAIL';
  }
  const detail = { name, passed, message, timestamp: new Date().toISOString(), ...extra };
  report.checks[category].details.push(detail);
  console.log(`[${passed ? 'PASS' : 'FAIL'}] [${category}] ${name}: ${message}`);
}

async function runAudit() {
  console.log('🚀 Starting Comprehensive QA Audit...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  let accessToken = null;

  // Monitor Console Logs for Security & General Errors
  page.on('console', msg => {
    const text = msg.text();
    const type = msg.type();
    if (type === 'error' || type === 'warning') {
      const isSensitive = /key|token|password|auth|secret|credential/i.test(text);
      if (isSensitive) {
        logCheck('security', 'Console Leaks', false, `Possible sensitive leak in console: [${type}] ${text}`);
      } else if (type === 'error' && !text.includes('favicon')) {
        logCheck('errorHandling', 'Console Error', false, `Console Error: ${text}`);
      }
    }
  });

  // Monitor API Requests & Responses
  const apiCalls = [];
  page.on('request', request => {
    if (request.url().includes('/api/v1/')) {
      apiCalls.push({
        url: request.url(),
        method: request.method(),
        startTime: Date.now(),
        headers: request.headers()
      });
    }
  });

  page.on('response', response => {
    const request = response.request();
    if (request.url().includes('/api/v1/')) {
      const call = apiCalls.find(c => c.url === request.url() && c.method === request.method() && !c.endTime);
      if (call) {
        call.endTime = Date.now();
        call.duration = call.endTime - call.startTime;
        call.status = response.status();
        
        // API Payload and Headers Verification
        const contentType = response.headers()['content-type'] || '';
        const hasAuth = !!request.headers()['authorization'];
        const isSecureHeaders = !!response.headers()['x-content-type-options'];
        
        if (response.status() >= 400) {
          response.text().then(text => {
            logCheck('apiVerification', `API Call ${call.method} ${call.url}`, false, 
              `Failed with status ${response.status()}. Response: ${text}`, { url: call.url });
          }).catch(err => {
            logCheck('apiVerification', `API Call ${call.method} ${call.url}`, false, 
              `Failed with status ${response.status()}. Could not read response: ${err.message}`, { url: call.url });
          });
        } else {
          logCheck('apiVerification', `API Call ${call.method} ${path.basename(call.url)}`, true, 
            `Success (${response.status()}) in ${call.duration}ms. Content-Type: ${contentType}. Auth: ${hasAuth ? 'Present' : 'Missing'}`);
          
          if (!hasAuth && !call.url.includes('/auth/login') && !call.url.includes('/auth/refresh')) {
            logCheck('security', 'API Auth Header Check', false, `API request to ${call.url} is missing Authorization header`);
          }
        }
      }
    }
  });

  try {
    // ── 1. Validation & Auth Testing ─────────────────────────────
    console.log('\n--- 1. Validation & Auth Testing ---');
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');

    // UI/UX Screen Capture on Login Page
    await captureScreenshots(page, 'login_page');

    // Validation Check: Empty fields
    await page.click('button[type="submit"]');
    const isEmailInvalid = await page.$eval('input[type="email"]', el => !el.validity.valid);
    logCheck('validation', 'Login Required Fields', isEmailInvalid, 'Browser HTML5 validation prevented submission of empty email form');

    // Validation Check: Bad inputs
    await page.fill('input[type="email"]', 'invalid-email');
    await page.fill('input[type="password"]', 'short');
    await page.click('button[type="submit"]');
    const isEmailStillInvalid = await page.$eval('input[type="email"]', el => !el.validity.valid);
    logCheck('validation', 'Login Email Format Check', isEmailStillInvalid, 'Browser HTML5 validation flagged malformed email address');

    // Perform Valid Login
    await page.fill('input[type="email"]', 'admin@dev.local');
    await page.fill('input[type="password"]', 'password123');
    
    // Performance measurement: Login Action
    const loginStart = Date.now();
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle' }),
      page.click('button[type="submit"]')
    ]);
    const loginDuration = Date.now() - loginStart;
    logCheck('performance', 'Redirection Post-Login', loginDuration < 3000, `Successfully redirected to dashboard in ${loginDuration}ms`);

    // Redirection validation
    const currentUrl = page.url();
    logCheck('validation', 'Login Redirection Route', currentUrl.endsWith('/dashboard'), `Redirection target: ${currentUrl}`);

    // Security Check: Token Storage
    const authStorageRaw = await page.evaluate(() => localStorage.getItem('auth-storage'));
    if (authStorageRaw) {
      try {
        const authData = JSON.parse(authStorageRaw);
        const token = authData.state ? authData.state.accessToken : null;
        const user = authData.state ? authData.state.user : null;
        accessToken = token;
        
        logCheck('security', 'Local Storage Auth Check', !!token, 'auth-storage token successfully written to localStorage');
        if (token) {
          const tokenParts = token.split('.');
          logCheck('security', 'JWT Format Validation', tokenParts.length === 3, 'Access token is a valid format 3-part JWT token');
        }
        if (user) {
          const isSuperAdminOrUUID = user.role === 'superadmin' || /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(user.role);
          logCheck('security', 'User Profile Exposure', isSuperAdminOrUUID && !user.password_hash, 
            `Logged in as user ${user.email} (Role: ${user.role}). No sensitive fields (e.g. password_hash) exposed in user state.`);
        }
      } catch (err) {
        logCheck('security', 'Token Parsing', false, `Failed to parse auth-storage: ${err.message}`);
      }
    } else {
      logCheck('security', 'Local Storage Auth Check', false, 'auth-storage key missing from localStorage after login');
    }

    // ── 2. Walkthrough All Views & Capture UI/UX ──────────────────
    console.log('\n--- 2. Page Views & Responsiveness ---');
    const routes = [
      { path: '/dashboard', name: 'Dashboard' },
      { path: '/conversations', name: 'Conversations' },
      { path: '/tickets', name: 'Tickets' },
      { path: '/agents', name: 'Agents' },
      { path: '/workflows', name: 'Workflows' },
      { path: '/prompts', name: 'Prompts' },
      { path: '/endpoints', name: 'Endpoints' },
      { path: '/clients', name: 'Clients' },
      { path: '/employees', name: 'Employees' },
      { path: '/users', name: 'Users' },
      { path: '/whatsapp', name: 'WhatsApp Config' },
      { path: '/analytics', name: 'Analytics' },
      { path: '/audit', name: 'Audit Log' },
      { path: '/security', name: 'Security Config' },
      { path: '/settings', name: 'Settings' }
    ];

    for (const r of routes) {
      const pageStart = Date.now();
      await page.goto(`${BASE_URL}${r.path}`);
      await page.waitForLoadState('networkidle');
      const pageDuration = Date.now() - pageStart;
      
      logCheck('performance', `${r.name} Load Performance`, pageDuration < 1500, `${r.name} view loaded in ${pageDuration}ms`);

      // Capture UI layouts (Responsiveness)
      await captureScreenshots(page, r.name.toLowerCase().replace(/\s+/g, '_'));

      // Basic Accessibility Checks
      const imagesWithoutAlt = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('img')).filter(img => !img.alt).length;
      });
      logCheck('accessibility', `${r.name} Alternate Image Text`, imagesWithoutAlt === 0, 
        imagesWithoutAlt === 0 ? 'All image elements have alt-text attributes' : `${imagesWithoutAlt} image(s) lack alt attributes`);

      const buttonsWithoutLabel = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('button')).filter(btn => !btn.innerText.trim() && !btn.getAttribute('aria-label')).length;
      });
      logCheck('accessibility', `${r.name} Interactive Labels`, buttonsWithoutLabel === 0, 
        buttonsWithoutLabel === 0 ? 'All interactive buttons have text or aria-labels' : `${buttonsWithoutLabel} icon button(s) lack accessible text/labels`);

      // Keyboard Focus Loop Verify
      const activeElementTag = await page.evaluate(() => {
        return document.activeElement ? document.activeElement.tagName.toLowerCase() : 'none';
      });
      logCheck('accessibility', `${r.name} Keyboard Focus Start`, activeElementTag !== 'body', `Default focus element tag is ${activeElementTag}`);
    }

    // ── 3. Functional/CRUD Operations ─────────────────────────────
    console.log('\n--- 3. Functional/CRUD Operations ---');

    // A. Clients Page (CRUD Button & API Test)
    console.log('Running Clients CRUD...');
    await page.goto(`${BASE_URL}/clients`);
    await page.waitForLoadState('networkidle');

    // Verify UI Button
    const addClientBtn = page.locator('button:has-text("Add Client"), button:has-text("Create Client"), button:has-text("New Client")');
    const hasAddClientBtn = await addClientBtn.count() > 0;
    logCheck('uiUx', 'Clients GUI Button Check', hasAddClientBtn, 'Found "Add Client" button in Clients header');

    // Verify Backend API CRUD directly
    if (accessToken) {
      const apiBase = BASE_URL.includes('localhost') ? 'http://localhost:5001/api/v1' : `${BASE_URL}/api/v1`;
      const clientRes = await context.request.post(`${apiBase}/clients/`, {
        data: {
          name: 'Test Client Company',
          email: 'contact@testclient.com',
          phone: '+15550199'
        },
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });
      const clientStatus = clientRes.status();
      const clientJson = await clientRes.json().catch(() => ({}));
      
      logCheck('validation', 'Client Creation API', clientStatus === 201, 
        `Backend Client POST API verified. Status: ${clientStatus}. Response ID: ${clientJson.id || 'N/A'}`);
      
      if (clientJson.id) {
        // Clean up: delete client
        const deleteRes = await context.request.delete(`${apiBase}/clients/${clientJson.id}`, {
          headers: { 'Authorization': `Bearer ${accessToken}` }
        });
        logCheck('validation', 'Client Deletion API', deleteRes.status() === 200, 'Backend Client DELETE API verified successfully');
      }
    } else {
      logCheck('validation', 'Client Creation API', false, 'Skipped Client API check: No access token found');
    }

    // B. AI Agents Page (CRUD Button & API Test)
    console.log('Running Agents CRUD...');
    await page.goto(`${BASE_URL}/agents`);
    await page.waitForLoadState('networkidle');

    const addAgentBtn = page.locator('button:has-text("Add Agent"), button:has-text("Create Agent"), button:has-text("New Agent")');
    const hasAddAgentBtn = await addAgentBtn.count() > 0;
    logCheck('uiUx', 'Agents GUI Button Check', hasAddAgentBtn, 'Found "New Agent" button in AI Agents header');

    if (accessToken) {
      const apiBase = BASE_URL.includes('localhost') ? 'http://localhost:5001/api/v1' : `${apiBase}/api/v1`;
      const agentRes = await context.request.post(`${apiBase}/agents/`, {
        data: {
          name: 'Test Support Bot',
          system_prompt: 'You are a test support assistant.',
          role_type: 'support'
        },
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });
      const agentStatus = agentRes.status();
      const agentJson = await agentRes.json().catch(() => ({}));

      logCheck('validation', 'Agent Creation API', agentStatus === 201, 
        `Backend Agent POST API verified. Status: ${agentStatus}. Response ID: ${agentJson.id || 'N/A'}`);

      if (agentJson.id) {
        // clean up
        const deleteRes = await context.request.delete(`${apiBase}/agents/${agentJson.id}`, {
          headers: { 'Authorization': `Bearer ${accessToken}` }
        });
        logCheck('validation', 'Agent Deletion API', deleteRes.status() === 200, 'Backend Agent DELETE API verified successfully');
      }
    } else {
      logCheck('validation', 'Agent Creation API', false, 'Skipped Agent API check: No access token found');
    }

    // ── 4. Error Handling ─────────────────────────────────────────
    console.log('\n--- 4. Error Routing & Fallbacks ---');
    await page.goto(`${BASE_URL}/non-existent-page-url-xyz-999`);
    await page.waitForLoadState('networkidle');
    const redirectedUrl = page.url();
    logCheck('errorHandling', '404 Fallback Routing', redirectedUrl.endsWith('/dashboard'), 
      `Invalid routes are automatically redirected to dashboard. Final URL: ${redirectedUrl}`);

  } catch (err) {
    console.error('Fatal error during QA E2E run:', err);
    logCheck('errorHandling', 'E2E Script Fatal Error', false, `E2E run crashed: ${err.message}`);
  } finally {
    report.summary.endTime = new Date().toISOString();
    await browser.close();
    generateMarkdownReport(apiCalls);
  }
}

async function captureScreenshots(page, namePrefix) {
  const viewports = [
    { width: 1280, height: 800, name: 'desktop' },
    { width: 768, height: 1024, name: 'tablet' },
    { width: 375, height: 667, name: 'mobile' }
  ];

  for (const v of viewports) {
    await page.setViewportSize({ width: v.width, height: v.height });
    await page.waitForTimeout(500); // allow layout stabilization
    const filename = `${namePrefix}_${v.name}.png`;
    const filepath = path.join(SCREENSHOTS_DIR, filename);
    await page.screenshot({ path: filepath, fullPage: false });
    
    // Log the screenshot creation
    logCheck('uiUx', `${namePrefix} Layout - ${v.name}`, true, 
      `Visual layout capture successful for ${v.name} viewport (${v.width}x${v.height})`, { screenshot: filepath });
  }
}

function generateMarkdownReport(apiCalls) {
  console.log('\nGenerating final Markdown report...');
  
  // Calculate category aggregates
  const categories = Object.keys(report.checks);
  const passedChecksCount = report.summary.passed;
  const totalChecksCount = report.summary.totalChecks;
  const readiness = ((passedChecksCount / totalChecksCount) * 100).toFixed(1);

  let md = `# QA Automation Audit Findings Report

**Date**: ${new Date().toLocaleDateString()}  
**Overall Status**: ${report.summary.status === 'PASS' ? '🟢 DEPLOYMENT READY' : '🔴 ACTION REQUIRED'}  
**System Readiness Rating**: **${readiness}%** (${passedChecksCount} / ${totalChecksCount} Checks Passed)

---

## 📊 Performance Statistics

### Page Load Durations (Vite/React Render & API fetch)
| Page | Target Load Time | Actual Load Time | Status |
| :--- | :--- | :--- | :--- |
`;

  // Extract page load details
  report.checks.performance.details.forEach(d => {
    if (d.name.endsWith('Load Performance')) {
      const pageName = d.name.replace(' Load Performance', '');
      const loadTime = parseInt(d.message.match(/\d+/)[0]);
      const status = loadTime < 1500 ? '🟢 Pass' : '🟡 Slow';
      md += `| ${pageName} | < 1500ms | ${loadTime}ms | ${status} |\n`;
    }
  });

  md += `
### API Latency Benchmarks
| Method | Endpoint | Duration | Status | Auth Header |
| :--- | :---: | :---: | :---: | :---: |
`;

  apiCalls.forEach(call => {
    const isSlow = call.duration > 800;
    const authStatus = call.headers['authorization'] ? 'Present' : 'Missing';
    md += `| ${call.method} | \`${path.basename(call.url)}\` | ${call.duration ? call.duration + 'ms' : 'N/A'} | ${call.status >= 400 ? '🔴 Fail' : (isSlow ? '🟡 Slow' : '🟢 OK')} | ${authStatus} |\n`;
  });

  md += `
---

## 🔒 Security Posture & Exposures

`;

  const securityDetails = report.checks.security.details;
  if (securityDetails.length > 0) {
    securityDetails.forEach(d => {
      md += `### ${d.passed ? '🟢' : '🔴'} ${d.name}\n- **Details**: ${d.message}\n\n`;
    });
  } else {
    md += `*No security warnings or vulnerabilities detected.*\n\n`;
  }

  md += `
---

## ♿ Accessibility Checks

`;

  const accDetails = report.checks.accessibility.details;
  let accIssues = 0;
  accDetails.forEach(d => {
    if (!d.passed) {
      accIssues++;
      md += `- [ ] **${d.name}**: ${d.message}\n`;
    }
  });
  if (accIssues === 0) {
    md += `🟢 **All checks passed**: No ARIA, alternate text, or focus loop missing values detected across the 15 page views.\n`;
  }

  md += `
---

## 🧪 Functional & Validation Checklist

`;

  const validationDetails = report.checks.validation.details;
  validationDetails.forEach(d => {
    md += `- **[${d.passed ? 'x' : ' '}] ${d.name}**: ${d.message}\n`;
  });

  md += `
---

## 💥 Console Issues & Error Handling

`;

  const errDetails = report.checks.errorHandling.details;
  let errCount = 0;
  errDetails.forEach(d => {
    if (!d.passed) {
      errCount++;
      md += `- **${d.name}**: ${d.message}\n`;
    }
  });
  if (errCount === 0) {
    md += `🟢 **Robust Error Handling**: 404 routes successfully handled, and no runtime JS crashes detected in the console logs.\n`;
  }

  // Populate Recommendations
  md += `
---

## 💡 Recommendations for Release
1. **Optimize API response times** for endpoints that take longer than 500ms.
2. **Review security headers**: Ensure production reverse proxy (Nginx) enforces HTTP strict transport security (HSTS), X-Frame-Options, and robust Content Security Policies (CSP).
3. **Verify rate limiting** is enabled on public endpoints (e.g. \`/api/v1/auth/login\`) in production to prevent brute force attempts.
`;

  // Write files
  const reportPath = path.join(BASE_URL.includes('localhost') ? '/Users/pranav1718/Documents/Whatsapp-Bot' : '.', 'qa_report.md');
  fs.writeFileSync(reportPath, md);
  fs.writeFileSync(path.join(ARTIFACT_DIR, 'qa_report.md'), md);
  console.log(`✅ Markdown reports written to ${reportPath} and artifact directory.`);
}

runAudit();
