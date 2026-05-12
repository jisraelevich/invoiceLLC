// ============================================================================
// APP.JS - Lógica de UI centralizada
// ============================================================================

class InvoicePlanner {
  constructor() {
    this.config = APP_CONFIG;
    this.currentMonth = new Date().getMonth();
    this.currentYear = new Date().getFullYear();
    this.selectedMonth = this.currentMonth;
    this.selectedYear = this.currentYear;
    this.isReadOnly = false;
    this.parsedInvoices = [];
    this.originalTextareaContent = '';
    this.inEditMode = false;  // Track if user clicked "Back" button (actively editing textarea)
    
    // Default textarea content (shown when preview is empty)
    this.defaultTextareaContent = `5/2/2026 65000
5/3/2026 78000
5/12/2026 103000`;
    
    // Initialize the application
    this.init();
  }

  // ========================================================================
  // HELPER: Safe number extraction - handles both en-US & es-AR formats
  // ========================================================================
  cleanNumberInput(value) {
    if (!value) return 0;
    
    // Convert to string if needed
    value = String(value).trim();
    
    console.log('[cleanNumberInput] INPUT:', value);
    
    // Remove ALL non-digit characters (1,234 → 1234 | 1.234 → 1234 | 1 234 → 1234)
    const digitsOnly = value.replace(/[^0-9]/g, '');
    
    console.log('[cleanNumberInput] DIGITS ONLY:', digitsOnly);
    
    // Parse as integer
    const parsed = parseInt(digitsOnly, 10) || 0;
    
    console.log('[cleanNumberInput] FINAL PARSED:', parsed);
    
    return parsed;
  }

  // Format number for display with thousands separator (en-US: 1,234,567)
  formatNumberDisplay(num) {
    if (!num || num === 0) return '';
    return parseInt(num, 10).toLocaleString('en-US', {minimumFractionDigits: 0});
  }

  // Convert date from MM/DD/YYYY (US input) to DD/MM/YYYY (AFIP Argentine format)
  convertToAFIPDateFormat(dateStr) {
    if (!dateStr || !dateStr.includes('/')) return dateStr;
    
    const parts = dateStr.split('/');
    if (parts.length !== 3) return dateStr;  // Invalid format, return as-is
    
    const month = parts[0].padStart(2, '0');  // MM
    const day = parts[1].padStart(2, '0');    // DD
    const year = parts[2];                     // YYYY
    
    // Return DD/MM/YYYY for AFIP
    return `${day}/${month}/${year}`;
  }

  // Convert date from DD/MM/YYYY (AFIP format) back to MM/DD/YYYY (display format)
  convertFromAFIPDateFormat(dateStr) {
    if (!dateStr || !dateStr.includes('/')) return dateStr;
    
    const parts = dateStr.split('/');
    if (parts.length !== 3) return dateStr;  // Invalid format, return as-is
    
    const day = parts[0];      // DD
    const month = parts[1];    // MM
    const year = parts[2];     // YYYY
    
    // Return MM/DD/YYYY for display
    return `${month}/${day}/${year}`;
  }

  // ========================================================================
  // LOGGING FUNCTIONS - Save logs and screenshots to server
  // ========================================================================
  async log(message, type = 'info') {
    console.log(`[LOG] ${message}`);
    try {
      await fetch('/api/logs/write', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message, type})
      });
    } catch (e) {
      console.error('[log] Error saving log:', e);
    }
  }

  async captureScreenshot(label = 'screenshot') {
    try {
      // Capture the container div
      const container = document.querySelector('.container');
      if (!container) {
        console.error('[captureScreenshot] Container not found');
        return;
      }

      // Use html2canvas if available, otherwise send a text snapshot
      if (typeof html2canvas !== 'undefined') {
        const canvas = await html2canvas(container, {allowTaint: true, useCORS: true});
        const imageData = canvas.toDataURL('image/png');
        
        await fetch('/api/images/save', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({image: imageData, label})
        });
        console.log('[captureScreenshot] Screenshot saved as:', label);
      } else {
        // Fallback: just log the state
        await this.log(`[SCREENSHOT] ${label}: textarea="${document.getElementById('textarea').value}" | grid rows="${document.querySelectorAll('tbody tr').length}"`, 'info');
      }
    } catch (e) {
      console.error('[captureScreenshot] Error:', e);
    }
  }

  init() {
    console.log('[init] STARTING INIT');
    console.log('[init] calling renderMonthTabs()');
    this.renderMonthTabs();
    console.log('[init] calling renderYearSelector()');
    this.renderYearSelector();
    console.log('[init] calling setupEventListeners()');
    this.setupEventListeners();
    console.log('[init] calling initializeDate()');
    this.initializeDate();
    console.log('[init] calling populateReferenceTables()');
    this.populateReferenceTables();
    console.log('[init] calling loadMonthData()');
    this.loadMonthData();
    console.log('[init] DONE - all initialization complete');
  }

  initializeDate() {
    const dateDiv = document.getElementById('current-date');
    console.log('[initializeDate] dateDiv found:', !!dateDiv);
    if (!dateDiv) {
      console.error('[initializeDate] ERROR: current-date element not found!');
      return;
    }
    
    const today = new Date();
    const formatted = today.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
    const finalText = formatted.charAt(0).toUpperCase() + formatted.slice(1);
    dateDiv.textContent = finalText;
    console.log('[initializeDate] set date to:', finalText);
  }

  populateReferenceTables() {
    // Populate Invoice Type Codes table
    const billTypeCodesBody = document.getElementById('bill-type-codes-table-body');
    if (billTypeCodesBody && this.config.billTypeCodes) {
      billTypeCodesBody.innerHTML = '';
      this.config.billTypeCodes.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td><strong>${item.code}</strong></td>
          <td>${item.label}</td>
        `;
        billTypeCodesBody.appendChild(row);
      });
    }
    
    // Populate Status Codes table
    const statusCodesBody = document.getElementById('status-codes-table-body');
    if (statusCodesBody && this.config.statusCodes) {
      statusCodesBody.innerHTML = '';
      this.config.statusCodes.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td><strong>${item.code}</strong></td>
          <td>${item.label}</td>
          <td>${item.description}</td>
        `;
        statusCodesBody.appendChild(row);
      });
    }
  }

  renderMonthTabs() {
    const tabsContainer = document.getElementById('month-tabs');
    console.log('[renderMonthTabs] tabsContainer found:', !!tabsContainer);
    if (!tabsContainer) {
      console.error('[renderMonthTabs] ERROR: month-tabs element not found!');
      return;
    }

    console.log('[renderMonthTabs] clearing container');
    tabsContainer.innerHTML = '';
    
    console.log('[renderMonthTabs] this.config.months:', this.config.months);
    console.log('[renderMonthTabs] starting loop for 12 months');
    
    for (let i = 0; i < 12; i++) {
      const tab = document.createElement('button');
      tab.className = 'month-tab';
      tab.textContent = this.config.months[i].substring(0, 3);
      tab.dataset.month = i;
      console.log(`[renderMonthTabs] created tab ${i}:`, tab.textContent);

      if (i === this.selectedMonth && this.selectedYear === this.currentYear) {
        tab.classList.add('active');
        console.log(`[renderMonthTabs] marked tab ${i} as active`);
      }

      tab.addEventListener('click', () => this.selectMonth(i));
      tabsContainer.appendChild(tab);
    }
    
    console.log('[renderMonthTabs] DONE - added', tabsContainer.children.length, 'tabs');
  }

  renderYearSelector() {
    const yearSelect = document.getElementById('year-dropdown');
    console.log('[renderYearSelector] yearSelect found:', !!yearSelect);
    if (!yearSelect) {
      console.error('[renderYearSelector] ERROR: year-dropdown element not found!');
      return;
    }

    yearSelect.innerHTML = '';
    console.log('[renderYearSelector] this.config.availableYears:', this.config.availableYears);
    
    this.config.availableYears.forEach(year => {
      const option = document.createElement('option');
      option.value = year;
      option.textContent = year;
      if (year === this.selectedYear) {
        option.selected = true;
        console.log('[renderYearSelector] selected year:', year);
      }
      yearSelect.appendChild(option);
    });

    yearSelect.addEventListener('change', (e) => {
      this.selectedYear = parseInt(e.target.value);
      this.selectedMonth = 0;
      this.renderMonthTabs();
      this.loadMonthData();
      this.checkReadOnlyStatus();
    });
    
    console.log('[renderYearSelector] DONE - added', yearSelect.options.length, 'years');
  }

  selectMonth(month) {
    this.selectedMonth = month;
    this.selectedYear = this.currentYear;
    this.renderMonthTabs();
    this.loadMonthData();
    this.checkReadOnlyStatus();
  }

  checkReadOnlyStatus() {
    // Check if selected month is older than 2 weeks
    const selectedDate = new Date(this.selectedYear, this.selectedMonth, 1);
    const today = new Date();
    const twoWeeksAgo = new Date(today.getTime() - 14 * 24 * 60 * 60 * 1000);

    this.isReadOnly = selectedDate < twoWeeksAgo && this.selectedYear < this.currentYear;

    const mainForm = document.getElementById('entry-form');
    const textarea = document.getElementById('invoice-textarea');
    const actionButtons = document.getElementById('action-buttons');

    if (this.isReadOnly) {
      if (textarea) textarea.classList.add('readonly');
      if (actionButtons) actionButtons.classList.add('hidden');
      document.getElementById('results-tab')?.classList.remove('hidden');
    } else {
      if (textarea) textarea.classList.remove('readonly');
      if (actionButtons) actionButtons.classList.remove('hidden');
    }
  }

  loadMonthData() {
    // Load data from backend for the selected month
    const month = this.selectedMonth + 1;
    
    // 🔴 DEBUG: Check if this is being called at the wrong time
    const previewSection = document.getElementById('preview-section');
    const isPreviewVisible = previewSection && previewSection.style.display !== 'none';
    
    console.log('[loadMonthData] ⚠️ CALLED');
    console.log('[loadMonthData] Preview section visible?', isPreviewVisible);
    console.log('[loadMonthData] inEditMode?', this.inEditMode);
    console.log('[loadMonthData] monthData.preview.length:', this.monthData?.preview?.length || 0);
    
    // Skip reload ONLY if user clicked "Back" button and is actively editing textarea
    // Don't skip on initial page load (inEditMode is false at startup)
    if (this.inEditMode) {
      console.warn('[loadMonthData] ⚠️ SKIPPING RELOAD - User is in edit mode after Back button, preventing data loss');
      return;
    }
    
    console.log(`Loading data for ${this.config.months[this.selectedMonth]} ${this.selectedYear}`);
    
    fetch(`/api/month/${this.selectedYear}/${month}`)
      .then(response => {
        if (!response.ok) {
          console.error('[loadMonthData] ❌ HTTP Error:', response.status, response.statusText);
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
      })
      .then(data => {
        console.warn(`[loadMonthData] Data loaded from server - preview: ${data?.preview?.length || 0} items`);
        this.monthData = data;
        this.updateMonthDisplay();
        this.resetEstimatedInput();
        this.updateBadges();
        this.renderPreviewGrid();
        this.renderResultsTab();
        this.updateTextareaContent();
      })
      .catch(error => {
        console.error('[loadMonthData] ❌ Error loading month data:', error);
        this.monthData = {
          year: this.selectedYear,
          month: month,
          estimated: 0,
          preview: [],
          results: []
        };
        this.resetEstimatedInput();
        this.updateBadges();
        this.renderPreviewGrid();
        this.updateTextareaContent();  // Set textarea empty or default based on preview
      });
  }

  updateTextareaContent() {
    // Show textarea with defaultContent from JSON (always start with defaults)
    // When preview has items AND user hasn't clicked Back yet → empty
    // When returning from grid (editMode) OR preview empty → show defaultContent + any grid items
    
    const textarea = document.getElementById('invoice-textarea');
    if (!textarea || !this.monthData) return;
    
    // If preview has items, textarea empty (user is in grid mode)
    if (this.monthData.preview && this.monthData.preview.length > 0) {
      textarea.value = '';
      console.log('[updateTextareaContent] Preview has items, textarea EMPTY');
    } else {
      // Preview empty - show defaultContent from JSON
      const defaultContent = this.monthData.defaultContent || '';
      textarea.value = defaultContent;
      console.log('[updateTextareaContent] Preview empty, showing defaultContent:', defaultContent);
    }
  }

  resetEstimatedInput() {
    // Reset estimated input to current month's value
    const estimatedInput = document.getElementById('estimated-amount');
    if (estimatedInput && this.monthData) {
      const displayValue = this.formatNumberDisplay(this.monthData.estimated);
      estimatedInput.value = displayValue;
      console.log('[resetEstimatedInput] monthData.estimated:', this.monthData.estimated, 'display:', displayValue);
    }
  }

  updateMonthDisplay() {
    const monthDisplay = document.getElementById('month-display');
    if (monthDisplay) {
      monthDisplay.textContent = `${this.config.months[this.selectedMonth]} ${this.selectedYear}`;
    }
  }

  updateBadges() {
    // Calculate and update badge values
    if (!this.monthData) return;
    
    const estimatedInput = document.getElementById('estimated-amount');
    const invoicedBadge = document.getElementById('invoiced-amount');
    const pendingBadge = document.getElementById('pending-amount');
    const subtotalBadge = document.getElementById('subtotal-amount');
    const availableBadge = document.getElementById('available-amount');
    
    // FORMULA:
    // Invoiced (Inv) = SUM of all results (already sent to AFIP)
    // Pending (Pend) = SUM of all preview (not sent yet)
    // Subtotal = Invoiced + Pending (TOTAL money involved)
    // Available = Estimated - Subtotal (money left in budget)
    // Estimated = Budget limit (user input)
    
    const resultsTotal = this.monthData.results.reduce((sum, inv) => sum + (inv.amount || 0), 0);
    const previewTotal = this.monthData.preview.reduce((sum, inv) => sum + (inv.amount || 0), 0);
    const subtotal = resultsTotal + previewTotal;
    
    // Get estimated value: prioritize input value, fallback to monthData.estimated from JSON
    let estimated = 0;
    
    // First: Check if input has a value (user is editing or just edited)
    if (estimatedInput && estimatedInput.value && estimatedInput.value.trim()) {
      const inputValue = this.cleanNumberInput(estimatedInput.value);
      if (inputValue > 0) {
        estimated = inputValue;
      }
    }
    
    // Fallback: Use saved value from monthData (from JSON)
    if (estimated === 0) {
      estimated = parseInt(this.monthData.estimated || 0, 10);
    }
    
    // Calculate Available budget
    const available = estimated - subtotal;
    
    console.log('DEBUG updateBadges - input:', estimatedInput?.value, 'monthData:', this.monthData.estimated, 'final estimated:', estimated, 'available:', available);
    
    // Update badges with proper formatting
    if (invoicedBadge) {
      invoicedBadge.textContent = `$${resultsTotal.toLocaleString('en-US', {minimumFractionDigits: 0})}`;
      console.log('Invoiced:', resultsTotal);
    }
    if (pendingBadge) {
      pendingBadge.textContent = `$${previewTotal.toLocaleString('en-US', {minimumFractionDigits: 0})}`;
      console.log('Pending:', previewTotal);
    }
    if (subtotalBadge) {
      subtotalBadge.textContent = `$${subtotal.toLocaleString('en-US', {minimumFractionDigits: 0})}`;
      console.log('Subtotal:', subtotal);
    }
    if (availableBadge) {
      if (available < 0) {
        // Over billing
        availableBadge.textContent = `⚠️ Over Billing: $${Math.abs(available).toLocaleString('en-US', {minimumFractionDigits: 0})}`;
        availableBadge.parentElement.style.background = '#fee2e2'; // Light red
        availableBadge.parentElement.style.borderColor = '#fca5a5';
        availableBadge.style.color = '#991b1b'; // Dark red
      } else {
        // Within budget
        availableBadge.textContent = `$${available.toLocaleString('en-US', {minimumFractionDigits: 0})}`;
        availableBadge.parentElement.style.background = '#f3e8ff'; // Light purple
        availableBadge.parentElement.style.borderColor = '#e9d5ff';
        availableBadge.style.color = 'inherit';
      }
      console.log('Available:', available);
    }
    
    // Update estimated input display if empty or different
    if (estimatedInput && (estimatedInput.value === '' || parseInt(estimatedInput.value.replace(/[^0-9]/g, ''), 10) === 0)) {
      const displayValue = this.monthData.estimated ? this.monthData.estimated.toLocaleString('en-US') : '';
      estimatedInput.value = displayValue;
    }
  }

  renderPreviewGrid() {
    // Render preview items from monthData.preview (called when loading month data)
    if (!this.monthData || !this.monthData.preview || this.monthData.preview.length === 0) {
      // Hide preview section if no items
      const previewSection = document.getElementById('preview-section');
      if (previewSection) {
        previewSection.style.display = 'none';
      }
      return;
    }
    
    const previewSection = document.getElementById('preview-section');
    const tableBody = document.getElementById('preview-table-body');
    const totalDisplay = document.getElementById('preview-total');
    
    if (!previewSection || !tableBody) return;
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Calculate total
    let totalAmount = 0;
    
    // Render each invoice
    this.monthData.preview.forEach((inv, idx) => {
      totalAmount += inv.amount || 0;
      
      const row = document.createElement('tr');
      row.innerHTML = `
        <td class="cell-editable" data-idx="${idx}" data-field="date">${inv.date}</td>
        <td class="cell-editable" data-idx="${idx}" data-field="amount" style="text-align: right;">$${(inv.amount || 0).toLocaleString('en-US', {minimumFractionDigits: 0})}</td>
        <td class="cell-editable" data-idx="${idx}" data-field="billType" style="text-align: right;">${inv.billType || '055'}</td>
      `;
      tableBody.appendChild(row);
      
      // Add click handlers for inline editing
      row.querySelectorAll('.cell-editable').forEach(cell => {
        cell.addEventListener('click', (e) => this.editCell(e, this.monthData.preview));
      });
    });
    
    // Update total display
    if (totalDisplay) {
      totalDisplay.textContent = `$${totalAmount.toLocaleString('en-US', {minimumFractionDigits: 0})}`;
    }
    
    // Show preview section
    previewSection.style.display = 'block';
  }

  renderResultsTab() {
    // Populate the Results tab with AFIP-sent invoices
    if (!this.monthData || !this.monthData.results) return;
    
    const tableBody = document.getElementById('results-table-body');
    const resultsTotal = document.getElementById('results-total');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    // Sort results by date (descending - newest first)
    // Dates are in MM/DD/YYYY format, so parse them correctly
    const sortedResults = [...this.monthData.results].sort((a, b) => {
      const parseDate = (dateStr) => {
        const parts = (dateStr || '').split('/');
        if (parts.length !== 3) return new Date(0);
        return new Date(parts[2], parseInt(parts[0]) - 1, parts[1]);  // YYYY, MM(0-11), DD
      };
      const dateA = parseDate(a.date);
      const dateB = parseDate(b.date);
      return dateB - dateA;  // Descending order
    });
    
    // Calculate total
    let totalAmount = 0;
    
    sortedResults.forEach(inv => {
      totalAmount += inv.amount || 0;
      
      const row = document.createElement('tr');
      const concept = this.getConceptFromBillType(inv.billType);
      row.innerHTML = `
        <td>${inv.date}</td>
        <td style="text-align: right;">$${inv.amount.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
        <td>${inv.billType}</td>
        <td>${concept}</td>
        <td>${inv.cae || 'N/A'}</td>
      `;
      tableBody.appendChild(row);
    });
    
    // Update total display
    if (resultsTotal) {
      resultsTotal.textContent = `$${totalAmount.toLocaleString('en-US', {minimumFractionDigits: 0})}`;
    }
  }

  setupEventListeners() {
    const parseBtn = document.getElementById('parse-btn');
    if (parseBtn) {
      parseBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();
        await this.parseInvoices();
      });
    }

    const editBtn = document.getElementById('edit-btn');
    if (editBtn) {
      editBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();
        await this.editMode();
      });
    }

    const facturateBtn = document.getElementById('facturate-btn');
    if (facturateBtn) {
      facturateBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();
        await this.approveFacturate();
      });
    }

    const exportCsvBtn = document.getElementById('export-csv-btn');
    if (exportCsvBtn) {
      exportCsvBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();
        await this.exportToCSV();
      });
    }

    const savePriceBtn = document.getElementById('save-price-btn');
    if (savePriceBtn) {
      savePriceBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();
        await this.savePrice();
      });
    }

    // Modal close handlers
    const modalOverlay = document.getElementById('modal-overlay');
    const modalClose = document.querySelector('.modal-close');
    
    if (modalOverlay) {
      modalOverlay.addEventListener('click', () => this.closeModal());
    }
    if (modalClose) {
      modalClose.addEventListener('click', () => this.closeModal());
    }
    
    // Estimated amount input handlers
    const estimatedInput = document.getElementById('estimated-amount');
    
    if (estimatedInput) {
      // Select all on focus
      estimatedInput.addEventListener('focus', (e) => {
        e.target.select();
      });
      
      // Format with thousands separator while typing
      estimatedInput.addEventListener('input', (e) => {
        // Clean input and format with thousands separator
        const cleanValue = this.cleanNumberInput(e.target.value);
        const displayValue = this.formatNumberDisplay(cleanValue);
        
        // Update display with formatted value
        e.target.value = displayValue;
        console.log('[INPUT EVENT] Cleaned:', cleanValue, 'Display:', displayValue);
        
        // Update badges in real-time
        this.updateBadges();
      });
      
      // Save on Enter key
      estimatedInput.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') {
          if (this.monthData) {
            const cleanValue = this.cleanNumberInput(e.target.value);
            console.log('[ENTER] Cleaned value:', cleanValue);
            this.monthData.estimated = cleanValue;
            this.updateBadges(); // Update badges immediately
            this.saveMonthData();
            console.log('[ENTER] Saved estimated:', cleanValue);
          } else {
            console.warn('monthData not initialized yet');
          }
          estimatedInput.blur(); // Lose focus after Enter
        }
      });
      
      // Blur handler to ensure value is saved and badges updated
      estimatedInput.addEventListener('blur', () => {
        if (this.monthData) {
          // Use helper function to safely extract number
          const cleanValue = this.cleanNumberInput(estimatedInput.value);
          console.log('[BLUR] Extracted clean value:', cleanValue);
          
          // Save to monthData
          this.monthData.estimated = cleanValue;
          console.log('[BLUR] Saved to monthData.estimated:', this.monthData.estimated);
          
          // Update display with formatted value
          const displayValue = this.formatNumberDisplay(cleanValue);
          estimatedInput.value = displayValue;
          console.log('[BLUR] Updated input display to:', displayValue);
          
          // Update badges and save to backend
          this.updateBadges();
          this.saveMonthData();
          console.log('[BLUR] Final saved value:', cleanValue);
        } else {
          console.warn('monthData not initialized in blur handler');
        }
      });
    }
  }

  parseTextarea() {
    /**
     * Parse textarea content and extract invoices
     * Format: DATE AMOUNT [TYPE]
     * Example:
     *   5/2/2026 65000
     *   5/3/2026 78000 055
     *   5/12/2026 103000
     */
    console.log('[parseTextarea] ========== PARSING START ==========');
    
    const textarea = document.getElementById('invoice-textarea');
    if (!textarea) {
      this.log('ERROR: Textarea not found', 'error');
      console.error('❌ Textarea not found');
      return [];
    }

    let rawValue = textarea.value;
    
    console.log('[parseTextarea] 📝 Textarea element found');
    console.log('[parseTextarea] 📝 rawValue.length:', rawValue.length);
    console.log('[parseTextarea] 📝 rawValue chars (first 100):', Array.from(rawValue.substring(0, 100)).map((c, i) => `'${c}'(${c.charCodeAt(0)})`).join(','));
    console.log('[parseTextarea] 📝 rawValue (FULL):', JSON.stringify(rawValue));
    
    // 🔴 REMOVED defaultContent fallback - always parse what's in textarea now
    // If user deleted items from textarea, we should respect that
    // If textarea is empty, parseTextarea returns empty array (no fallback to old data)
    
    this.log(`parseTextarea START: raw value length=${rawValue.length}`, 'info');
    this.log(`Raw textarea="${rawValue.substring(0, 100)}"`, 'info');

    const lines = rawValue.trim().split('\n').filter(line => line.trim());
    console.log('[parseTextarea] 📋 After trim().split("\\n").filter():');
    console.log('[parseTextarea] 📋   lines.length =', lines.length);
    console.log('[parseTextarea] 📋   lines =', JSON.stringify(lines));
    
    this.log(`After split: ${lines.length} lines: ${JSON.stringify(lines)}`, 'info');

    const invoices = [];

    lines.forEach((line, idx) => {
      const trimmed = line.trim();
      if (!trimmed) {
        this.log(`Line ${idx + 1}: empty, skipping`, 'info');
        console.log(`[parseTextarea] Line ${idx + 1}: EMPTY, skipping`);
        return;
      }

      this.log(`Line ${idx + 1}: "${trimmed}"`, 'info');
      console.log(`[parseTextarea] Line ${idx + 1}: "${trimmed}"`);
      
      // Parse: DATE AMOUNT [TYPE]
      const parts = trimmed.split(/\s+/);
      this.log(`  Parts count=${parts.length}, values=${JSON.stringify(parts)}`, 'info');
      console.log(`[parseTextarea]   Parts (${parts.length}):`, JSON.stringify(parts));
      
      if (parts.length < 2) {
        this.log(`  ERROR: Not enough parts (need 2, got ${parts.length})`, 'error');
        console.warn(`[parseTextarea] ❌ Line ${idx + 1}: Not enough parts`);
        return;
      }

      const date = parts[0];
      const amountRaw = parts[1];
      const amount = this.cleanNumberInput(amountRaw);
      const type = parts[2] || '055';

      this.log(`  date="${date}", amountRaw="${amountRaw}", amountCleaned=${amount}, type="${type}"`, 'info');
      console.log(`[parseTextarea]   date="${date}", amountRaw="${amountRaw}", amountCleaned=${amount}, type="${type}"`);

      // Validate date format (basic: should contain /)
      if (!date.includes('/')) {
        this.log(`  ERROR: Bad date format: "${date}"`, 'error');
        console.warn(`[parseTextarea] ❌ Line ${idx + 1}: Bad date: "${date}"`);
        return;
      }

      // Validate amount
      if (isNaN(amount) || amount <= 0) {
        this.log(`  ERROR: Bad amount: cleaned=${amount}, isNaN=${isNaN(amount)}`, 'error');
        console.warn(`[parseTextarea] ❌ Line ${idx + 1}: Bad amount: cleaned=${amount}, isNaN=${isNaN(amount)}`);
        return;
      }

      // Validate type (should be numeric string)
      if (isNaN(parseInt(type, 10))) {
        this.log(`  ERROR: Bad type: "${type}" (not numeric)`, 'error');
        console.warn(`[parseTextarea] ❌ Line ${idx + 1}: Bad type: "${type}"`);
        return;
      }

      this.log(`  ✅ VALID invoice`, 'info');
      console.log(`[parseTextarea] ✅ Line ${idx + 1}: VALID`);
      invoices.push({
        date: date,  // Keep as MM/DD/YYYY (US format) for UI
        amount: amount,
        billType: type,
        status: '01'
      });
    });

    this.log(`parseTextarea RESULT: ${invoices.length} invoices found`, 'info');
    console.log(`[parseTextarea] DONE: ${invoices.length} invoices found`);
    console.log(`[parseTextarea] RETURNING ARRAY WITH ${invoices.length} ELEMENTS:`, JSON.stringify(invoices));
    return invoices;
  }

  getConceptFromBillType(billType) {
    // Map bill type codes to concepts from config
    const billTypeMapping = this.config.billTypeCodes.find(item => item.code === billType);
    return billTypeMapping ? billTypeMapping.label : `Bill Type ${billType}`;
  }

  getStatusLabel(statusCode) {
    // Map status codes to labels from config
    const statusMapping = this.config.statusCodes.find(item => item.code === statusCode);
    return statusMapping ? statusMapping.label : `Status ${statusCode}`;
  }

  async parseInvoices() {
    console.log('\n╔═══════════════════════════════════════════════════╗');
    console.log('║ [parseInvoices] PARSE & PREVIEW CLICKED           ║');
    console.log('╚═══════════════════════════════════════════════════╝\n');
    
    this.inEditMode = false;
    
    const newInvoices = this.parseTextarea();
    console.log('✓ parseTextarea returned:', newInvoices.length, 'items');
    console.log('  Content:', JSON.stringify(newInvoices));
    
    if (newInvoices.length === 0) {
      console.warn('✗ WARNING: parseTextarea returned 0 items');
      return;
    }

    const textarea = document.getElementById('invoice-textarea');
    const estimatedInput = document.getElementById('estimated-amount');
    const estimated = this.cleanNumberInput(estimatedInput?.value || 0);

    // MERGE with existing
    let mergedInvoices = [];
    if (this.monthData?.preview?.length > 0) {
      mergedInvoices = [...this.monthData.preview];
    }
    mergedInvoices = mergedInvoices.concat(newInvoices);
    
    // Remove duplicates
    const uniqueInvoices = [];
    const seen = new Set();
    mergedInvoices.forEach(inv => {
      const key = `${inv.date}-${inv.amount}-${inv.billType}`;
      if (!seen.has(key)) {
        uniqueInvoices.push(inv);
        seen.add(key);
      }
    });
    
    console.log('✓ Merged + deduped:', uniqueInvoices.length, 'unique items');

    // SORT
    uniqueInvoices.sort((a, b) => {
      if (a.billType !== b.billType) return a.billType.localeCompare(b.billType);
      const dateA = new Date(a.date.split('/').reverse().join('-'));
      const dateB = new Date(b.date.split('/').reverse().join('-'));
      if (dateA.getTime() !== dateB.getTime()) return dateA - dateB;
      return a.amount - b.amount;
    });
    
    console.log('✓ Sorted by TYPE→DATE→AMOUNT');

    // Update monthData
    if (this.monthData) {
      console.log('✓ ASSIGNING to monthData.preview...');
      this.monthData.preview = uniqueInvoices;
      this.monthData.estimated = estimated || this.monthData.estimated;
      
      console.log('✓ Calling saveMonthData()...');
      await this.saveMonthData();
      
      console.log('✓ AFTER save: monthData.preview has', this.monthData.preview.length, 'items');
      console.log('  Items:', JSON.stringify(this.monthData.preview));
      
      this.updateBadges();
      
      console.log('✓ Calling renderPreviewGrid() to display grid...');
      this.renderPreviewGrid();
      console.log('✓ Grid rendered and visible');
      
      // Clear textarea after moving to grid
      if (textarea) {
        console.log('✓ Clearing textarea...');
        textarea.value = '';
        console.log('✓ Textarea cleared');
      }
    }
    
    console.log('\n╔═══════════════════════════════════════════════════╗');
    console.log('║ [parseInvoices] COMPLETE - Grid should show',
      String(uniqueInvoices.length).padEnd(2), 'items           ║');
    console.log('║ Textarea cleared, ready for new input              ║');
    console.log('╚═══════════════════════════════════════════════════╝\n');
  }

  async saveMonthData() {
    console.log('[saveMonthData] ========== SAVE START ==========');
    
    // Save current month data to backend
    if (!this.monthData) {
      console.error('[saveMonthData] ❌ monthData is null/undefined!');
      return;
    }
    
    const month = this.selectedMonth + 1;
    const url = `/api/month/${this.selectedYear}/${month}`;
    
    console.log('[saveMonthData] 💾 URL:', url);
    console.log('[saveMonthData] 📊 monthData.preview.length:', this.monthData.preview.length);
    console.log('[saveMonthData] 📊 monthData.preview:', JSON.stringify(this.monthData.preview));
    console.log('[saveMonthData] 📊 Full monthData:', JSON.stringify(this.monthData));
    
    const jsonBody = JSON.stringify(this.monthData);
    console.log('[saveMonthData] 📦 JSON size:', jsonBody.length, 'bytes');
    console.log('[saveMonthData] 📤 About to POST...');
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: jsonBody
      });
      
      console.log('[saveMonthData] 📥 Response received. Status:', response.status, response.statusText);
      
      if (!response.ok) {
        console.error('[saveMonthData] ❌ HTTP Error:', response.status, response.statusText);
        const errorText = await response.text();
        console.error('[saveMonthData] ❌ Response body:', errorText);
        return { error: `HTTP ${response.status}` };
      }
      
      const data = await response.json();
      console.log('[saveMonthData] ✅ Response JSON:', data);
      this.log(`Saved month data with ${this.monthData.preview.length} items in preview`, 'info');
      console.log('[saveMonthData] ========== SAVE END (SUCCESS) ==========');
      return data;
    } catch (error) {
      console.error('[saveMonthData] ❌ Exception caught:', error.message);
      console.error('[saveMonthData] ❌ Exception stack:', error.stack);
      this.log(`ERROR saving month data: ${error}`, 'error');
      console.log('[saveMonthData] ========== SAVE END (ERROR) ==========');
      return { error: error.message };
    }
  }

  editCell(event, invoices) {
    let cell = event.target;
    
    // If clicking on a child element, traverse up to find the cell with data-idx
    while (cell && !cell.dataset.idx) {
      cell = cell.parentElement;
      if (!cell || cell.tagName === 'TABLE') break;  // Stop if we go too far up
    }
    
    if (!cell || !cell.dataset.idx) {
      console.error('[editCell] ❌ Could not find cell with data-idx');
      return;
    }
    
    const idx = parseInt(cell.dataset.idx);
    const field = cell.dataset.field;
    
    // Always use live reference from monthData
    if (!this.monthData || !this.monthData.preview || !this.monthData.preview[idx]) {
      console.error('[editCell] ❌ Invalid data reference at idx:', idx);
      return;
    }

    const currentValue = this.monthData.preview[idx][field];
    let inputHTML = '';

    // Prevent editing if already editing
    if (cell.querySelector('input') || cell.querySelector('select')) return;

    if (field === 'date') {
      inputHTML = `<input type="text" value="${currentValue}" placeholder="MM/DD/YYYY">`;
    } else if (field === 'amount') {
      inputHTML = `<input type="number" value="${currentValue}" step="1000" min="0">`;
    } else if (field === 'billType' || field === 'type') {
      inputHTML = `<select>
        <option value="055" ${currentValue === '055' ? 'selected' : ''}>055 - Services IT</option>
        <option value="061" ${currentValue === '061' ? 'selected' : ''}>061 - Sale Goods</option>
        <option value="062" ${currentValue === '062' ? 'selected' : ''}>062 - Rental</option>
      </select>`;
    }

    cell.classList.add('editable');
    cell.innerHTML = inputHTML;

    const input = cell.querySelector('input') || cell.querySelector('select');
    if (input) {
      input.focus();
      input.select?.();

      const saveEdit = async () => {
        let newValue = field === 'amount' ? this.cleanNumberInput(input.value) : input.value;
        
        if (!newValue || (field === 'amount' && newValue <= 0)) {
          console.log('[editCell] ⚠️ Invalid value, reverting to:', currentValue);
          this.renderCellValue(cell, currentValue, field);
          return;
        }

        // Update directly in monthData.preview (live reference)
        if (!this.monthData.preview[idx]) {
          console.error('[editCell] ❌ CRITICAL: preview[' + idx + '] is undefined!');
          return;
        }
        
        console.log('[editCell] ✏️ Updating preview[%d].%s = %s', idx, field, newValue);
        this.monthData.preview[idx][field] = newValue;

        this.renderCellValue(cell, newValue, field);
        
        const totalAmount = this.monthData.preview.reduce((sum, inv) => sum + (inv.amount || 0), 0);
        const totalDisplay = document.getElementById('preview-total');
        if (totalDisplay) {
          totalDisplay.textContent = `$${totalAmount.toLocaleString('en-US', {minimumFractionDigits: 0})}`;
        }
        
        // � SAVE: Only on Enter or blur - not on typing
        console.log('[editCell] 💾 SAVING to server - preview.length:', this.monthData.preview.length);
        await this.saveMonthData();
        this.updateBadges();
        console.log('[editCell] ✅ SYNC COMPLETE - Cell saved to server');
        this.log(`Cell saved: ${field} = ${newValue}`, 'info');
      };
      
      // Save on Enter key or when leaving the cell (blur)
      input.addEventListener('blur', async () => {
        console.log('[editCell] 💾 Saving on blur (left cell)');
        await saveEdit();
      });
      
      input.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          e.stopPropagation();
          console.log('[editCell] 💾 Saving on Enter press');
          await saveEdit();
        }
        if (e.key === 'Escape') {
          console.log('[editCell] ❌ Edit cancelled with Escape');
          this.renderCellValue(cell, currentValue, field);
        }
      });
    }
  }

  renderCellValue(cell, value, field) {
    cell.classList.remove('editable');
    if (field === 'amount') {
      cell.textContent = `$${value.toLocaleString('en-US', {minimumFractionDigits: 0})}`;
      cell.style.textAlign = 'right';
    } else {
      cell.textContent = value;
    }
  }

  calculatePreview() {
    // Legacy method - now calls parseInvoices
    this.parseInvoices();
  }

  async editMode() {
    console.log('═══════════════════════════════════════════════════════════');
    console.log('[editMode] 🔴 BACK BUTTON CLICKED - STARTING RESTORATION');
    console.log('═══════════════════════════════════════════════════════════');
    
    console.log('[editMode] ⏱️ Setting inEditMode = true to prevent data loss');
    this.inEditMode = true;
    
    console.log('[editMode] 📊 Current monthData state:');
    console.log('[editMode]    monthData exists?', !!this.monthData);
    console.log('[editMode]    monthData.preview exists?', !!this.monthData?.preview);
    console.log('[editMode]    monthData.preview.length?', this.monthData?.preview?.length);
    if (this.monthData?.preview?.length > 0) {
      console.log('[editMode]    monthData.preview[0]:', JSON.stringify(this.monthData.preview[0]));
    }
    
    const previewSection = document.getElementById('preview-section');
    const previewTableBody = document.getElementById('preview-table-body');
    const previewTotal = document.getElementById('preview-total');
    const textarea = document.getElementById('invoice-textarea');
    
    console.log('[editMode] 🔍 DOM Elements found:');
    console.log('[editMode]    previewSection?', !!previewSection);
    console.log('[editMode]    previewTableBody?', !!previewTableBody);
    console.log('[editMode]    textarea?', !!textarea);
    
    if (!textarea) {
      console.error('[editMode] ❌❌❌ CRITICAL: Textarea element not found!');
      return;
    }
    
    // Hide preview section
    if (previewSection) {
      previewSection.style.display = 'none';
      console.log('[editMode] ✅ Hidden preview section');
    }
    
    // STEP 1: Backup preview data BEFORE touching anything
    console.log('[editMode] 📋 STEP 1: Creating backup of preview array');
    const previewBackup = this.monthData && this.monthData.preview ? [...this.monthData.preview] : [];
    console.log('[editMode]    previewBackup.length =', previewBackup.length);
    if (previewBackup.length > 0) {
      console.log('[editMode]    previewBackup[0] =', JSON.stringify(previewBackup[0]));
      console.log('[editMode]    previewBackup[previewBackup.length-1] =', JSON.stringify(previewBackup[previewBackup.length - 1]));
    }
    
    // STEP 2: Build textarea content from backup
    console.log('[editMode] 📝 STEP 2: Building textarea content from backup');
    let textareaContent = '';
    
    if (previewBackup && Array.isArray(previewBackup) && previewBackup.length > 0) {
      console.log('[editMode]    ✅ previewBackup has', previewBackup.length, 'items, building content...');
      
      previewBackup.forEach((inv, idx) => {
        const line = `${inv.date} ${inv.amount} ${inv.billType}`;
        console.log(`[editMode]       Item ${idx}: "${line}"`);
        textareaContent += (idx > 0 ? '\n' : '') + line;
      });
      
      console.log('[editMode]    ✅ Built textareaContent:');
      console.log('[editMode]       Length:', textareaContent.length);
      console.log('[editMode]       Content:', JSON.stringify(textareaContent));
    } else {
      console.warn('[editMode]    ⚠️ previewBackup is empty or invalid!');
      textareaContent = '';
    }
    
    // STEP 3: Set textarea value
    console.log('[editMode] 📝 STEP 3: Setting textarea.value');
    console.log('[editMode]    BEFORE: textarea.value.length =', textarea.value.length);
    textarea.value = textareaContent;
    console.log('[editMode]    AFTER: textarea.value.length =', textarea.value.length);
    console.log('[editMode]    AFTER: textarea.value =', JSON.stringify(textarea.value));
    
    if (textarea.value !== textareaContent) {
      console.error('[editMode] ❌ MISMATCH! textarea.value was not set correctly');
      console.error('[editMode]    Expected:', textareaContent);
      console.error('[editMode]    Got:', textarea.value);
    }
    
    // STEP 4: Update defaultContent
    console.log('[editMode] 💾 STEP 4: Updating defaultContent');
    if (this.monthData) {
      this.monthData.defaultContent = textareaContent;
      console.log('[editMode]    ✅ defaultContent updated, length =', this.monthData.defaultContent.length);
    }
    
    // STEP 5: Clear grid UI
    console.log('[editMode] 🗑️ STEP 5: Clearing grid UI');
    if (previewTableBody) {
      previewTableBody.innerHTML = '';
      console.log('[editMode]    ✅ Cleared previewTableBody');
    }
    if (previewTotal) {
      previewTotal.textContent = '$0';
      console.log('[editMode]    ✅ Reset previewTotal');
    }
    
    // STEP 6: Clear preview array
    console.log('[editMode] 🗑️ STEP 6: Clearing preview array');
    if (this.monthData) {
      console.log('[editMode]    BEFORE: monthData.preview.length =', this.monthData.preview.length);
      this.monthData.preview = [];
      console.log('[editMode]    AFTER: monthData.preview.length =', this.monthData.preview.length);
    }
    
    // STEP 7: Save to server
    console.log('[editMode] 💾 STEP 7: Saving to server');
    if (this.monthData) {
      console.log('[editMode]    Calling saveMonthData()...');
      await this.saveMonthData();
      console.log('[editMode]    ✅ saveMonthData() completed');
    }
    
    // STEP 8: Update badges
    console.log('[editMode] 🔄 STEP 8: Updating badges');
    this.updateBadges();
    
    console.log('═══════════════════════════════════════════════════════════');
    console.log('[editMode] ✅ BACK BUTTON COMPLETE');
    console.log('[editMode]    - textarea has', textarea.value.split('\n').length, 'lines');
    console.log('[editMode]    - preview.length =', this.monthData?.preview?.length);
    console.log('═══════════════════════════════════════════════════════════');
  }

  async exportToCSV() {
    console.log('[exportToCSV] 📁 Starting export to CSV');
    console.log('[exportToCSV] DEBUG: monthData.preview has', this.monthData?.preview?.length || 0, 'items');
    
    if (!this.monthData || !this.monthData.preview || this.monthData.preview.length === 0) {
      this.showModal('⚠️ Error', 'No invoices in Preview grid to export', ['OK']);
      return;
    }
    
    try {
      console.log('[exportToCSV] Converting', this.monthData.preview.length, 'invoices to CSV format');
      
      // Map preview grid data to facturador_afip CSV format
      const csvData = this.formatPreviewAsAFIPCSV(this.monthData.preview);
      
      console.log('[exportToCSV] CSV formatted:', csvData);
      this.log(`Exporting ${this.monthData.preview.length} invoices to facturador_afip`, 'info');
      
      // Send to backend to save in facturador_afip folder
      const response = await fetch('/api/export-to-afip-csv', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          invoices: this.monthData.preview,
          csvContent: csvData
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        console.log('[exportToCSV] ✅ CSV saved successfully:', result.filepath);
        console.log('[exportToCSV] ⚠️ IMPORTANT: Preview still has', this.monthData.preview.length, 'items (NOT cleared after export)');
        console.log('[exportToCSV] 📝 When you press Back, these items should go to textarea');
        
        this.showModal(
          '✅ Success', 
          `✓ Exported ${this.monthData.preview.length} invoices to CSV\n\nFile: ${result.filepath}\n\nNext step: Run FacturarAhora.bat in facturador_afip folder\n\n⚠️ Click Back to return to textarea`,
          ['OK']
        );
        this.log(`CSV exported successfully to ${result.filepath}`, 'info');
      } else {
        console.error('[exportToCSV] ❌ Export failed:', result.error);
        this.showModal('❌ Error', `Export failed: ${result.error}`, ['OK']);
        this.log(`CSV export error: ${result.error}`, 'error');
      }
    } catch (error) {
      console.error('[exportToCSV] ❌ Exception:', error);
      this.showModal('❌ Error', `Export error: ${error.message}`, ['OK']);
      this.log(`CSV export exception: ${error}`, 'error');
    }
  }

  formatPreviewAsAFIPCSV(invoices) {
    /**
     * Convert preview grid data to facturador_afip CSV format
     * CSV columns: FECHA,CODIGO,PRODUCTO SERVICO:,PRECIO UNITARIO,CUIT_CLIENTE,NOMBRE_CLIENTE,ESTADO,CAE,NRO_COMPROBANTE
     */
    
    // CSV Header
    const headers = ['FECHA', 'CODIGO', 'PRODUCTO SERVICO:', 'PRECIO UNITARIO', 'CUIT_CLIENTE', 'NOMBRE_CLIENTE', 'ESTADO', 'CAE', 'NRO_COMPROBANTE'];
    
    // Convert each invoice to CSV row
    const rows = invoices.map((inv) => [
      this.convertToAFIPDateFormat(inv.date),  // FECHA: Convert MM/DD/YYYY to DD/MM/YYYY
      inv.billType || '055',                   // CODIGO: 055, 061, 062 (invoice type)
      'Servicios Informáticos y capacitacion DB',  // PRODUCTO SERVICO: (correct description)
      inv.amount,                              // PRECIO UNITARIO: amount
      '99999999999',                           // CUIT_CLIENTE: (fixed - consumer)
      'Consumidor Final',                      // NOMBRE_CLIENTE: (fixed)
      'PENDIENTE',                             // ESTADO: PENDIENTE (not yet sent to AFIP)
      '',                                      // CAE: (empty - will be filled by AFIP bot)
      ''                                       // NRO_COMPROBANTE: (empty - will be filled by AFIP bot)
    ]);
    
    // Build CSV string
    const headerRow = headers.map(h => `"${h}"`).join(',');
    const dataRows = rows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
    
    const csvContent = headerRow + '\n' + dataRows;
    
    console.log('[formatPreviewAsAFIPCSV] Generated CSV content:');
    console.log(csvContent);
    
    return csvContent;
  }

  approveFacturate() {
    console.log('Approve & Facturate clicked');
    this.showModal(
      '¿Confirmar Facturación?',
      'Se enviarán los comprobantes al sistema AFIP.',
      ['Cancelar', 'Confirmar']
    );
  }

  savePrice() {
    const priceInput = document.getElementById('price-input');
    if (priceInput) {
      const price = this.cleanNumberInput(priceInput.value || 0);
      console.log('[savePrice] Saving estimated price:', price);
      
      // Update monthData estimated
      if (this.monthData) {
        this.monthData.estimated = price;
        this.saveMonthData();
        this.updateBadges();
      }
      
      this.showModal('✓ Guardado', `Presupuesto estimado: $${price.toLocaleString('en-US', {minimumFractionDigits: 0})}`, ['OK']);
    }
  }

  // ========== MODAL FUNCTIONS ==========
  
  showModal(title, message, buttons = ['Aceptar']) {
    const overlay = document.getElementById('modal-overlay');
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const modalFooter = document.getElementById('modal-footer');

    if (!overlay || !modal) return;

    modalTitle.textContent = title;
    modalBody.textContent = message;
    modalFooter.innerHTML = '';

    buttons.forEach((btnText, index) => {
      const btn = document.createElement('button');
      btn.className = index === buttons.length - 1 ? 'btn btn-primary btn-small' : 'btn btn-outline btn-small';
      btn.textContent = btnText;
      btn.addEventListener('click', () => {
        this.closeModal();
        if (btnText === 'Confirmar') {
          this.handleModalConfirm();
        }
      });
      modalFooter.appendChild(btn);
    });

    overlay.classList.remove('hidden');
    modal.classList.remove('hidden');
  }

  closeModal() {
    const overlay = document.getElementById('modal-overlay');
    const modal = document.getElementById('modal');
    if (overlay) overlay.classList.add('hidden');
    if (modal) modal.classList.add('hidden');
  }

  handleModalConfirm() {
    console.log('Confirmación: Enviando facturación a AFIP');
    
    if (!this.monthData || !this.monthData.preview || this.monthData.preview.length === 0) {
      this.showModal('\u2705 Info', 'No hay facturas para enviar', ['OK']);
      return;
    }
    
    const month = this.selectedMonth + 1;
    const totalBills = this.monthData.preview.length;
    
    // Show processing message
    this.showModal('⏳ Procesando...', `Enviando ${totalBills} factura(s) a AFIP.\n\nEsto puede tomar 1-50 minutos. Por favor espere...`, []);
    
    // Send data as-is (backend will handle date conversion)
    fetch(`/api/month/${this.selectedYear}/${month}/send-to-afip`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(this.monthData)  // Send with MM/DD/YYYY dates - backend converts
    })
    .then(response => response.json())
    .then(data => {
      this.closeModal();
      
      if (data.success) {
        // ========== CONVERSION 2: DD/MM/YYYY → MM/DD/YYYY from AFIP response ==========
        // Convert received dates back to MM/DD/YYYY for storage
        if (data.data && data.data.preview) {
          data.data.preview = data.data.preview.map(inv => ({
            ...inv,
            date: this.convertFromAFIPDateFormat(inv.date)  // DD/MM/YYYY → MM/DD/YYYY
          }));
        }
        
        // Backend returns data as-is (no conversion needed)
        this.monthData = data.data;
        
        const processed = data.processed || 0;
        const pending = data.pending || 0;
        
        // Build detailed message
        let resultMessage = `✅ Procesadas: ${processed} factura(s)\n`;
        if (pending > 0) {
          resultMessage += `⚠️  Pendientes (reintento): ${pending} factura(s)\n\n`;
          resultMessage += 'Las facturas que no fueron procesadas permanecen en preview para reintentarlo.';
        } else {
          resultMessage += '\n¡Todas las facturas fueron procesadas correctamente!';
        }
        
        // Show result with appropriate buttons
        const buttons = pending > 0 ? ['OK', 'Reintentar Fallidas'] : ['OK'];
        this.showResultModal('\u2705 Éxito', resultMessage, buttons, pending > 0);
        
        // Update AFIP status badges
        this.updateAfipStatusBadges(processed, pending);
        
        // Hide preview and reload results
        const previewSection = document.getElementById('preview-section');
        if (previewSection) {
          previewSection.style.display = 'none';
        }
        
        this.updateBadges();
        this.renderResultsTab();
      } else {
        this.showModal('\u274c Error', data.error || 'Error al enviar a AFIP', ['OK']);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      this.closeModal();
      this.showModal('\u274c Error', 'Error al conectar con el servidor: ' + error.message, ['OK']);
    });
  }
  
  showResultModal(title, message, buttons = ['OK'], hasFailedBills = false) {
    const overlay = document.getElementById('modal-overlay');
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const modalFooter = document.getElementById('modal-footer');

    if (!overlay || !modal) return;

    modalTitle.textContent = title;
    modalBody.textContent = message;
    modalBody.style.whiteSpace = 'pre-wrap';  // Preserve line breaks
    modalFooter.innerHTML = '';

    buttons.forEach((btnText, index) => {
      const btn = document.createElement('button');
      btn.className = index === buttons.length - 1 ? 'btn btn-primary btn-small' : 'btn btn-outline btn-small';
      btn.textContent = btnText;
      btn.addEventListener('click', () => {
        this.closeModal();
        if (btnText === 'Reintentar Fallidas' && hasFailedBills) {
          this.retryFailedBills();
        }
      });
      modalFooter.appendChild(btn);
    });

    overlay.classList.remove('hidden');
    modal.classList.remove('hidden');
  }
  
  retryFailedBills() {
    console.log('Reintentando facturas fallidas...');
    
    if (!this.monthData || !this.monthData.preview || this.monthData.preview.length === 0) {
      this.showModal('\u2705 Info', 'No hay facturas pendientes para reintentar', ['OK']);
      return;
    }
    
    // Show the preview section again for retry
    const previewSection = document.getElementById('preview-section');
    if (previewSection) {
      previewSection.style.display = 'block';
    }
    
    this.renderPreviewTable();
    this.showModal('\u21a9 Reintentar', `${this.monthData.preview.length} factura(s) disponible(s) para reintentar.\n\nHaz clic en "Send to AFIP" cuando estés listo.`, ['OK']);
  }
  
  updateAfipStatusBadges(processed, pending) {
    console.log(`Updating AFIP badges: processed=${processed}, pending=${pending}`);
    
    const processedBadge = document.getElementById('processed-badge');
    const failedBadge = document.getElementById('failed-badge');
    const processedCount = document.getElementById('processed-count');
    const failedCount = document.getElementById('failed-count');
    
    if (processedBadge && processedCount) {
      processedCount.textContent = processed;
      processedBadge.style.display = processed > 0 ? 'flex' : 'none';
    }
    
    if (failedBadge && failedCount) {
      failedCount.textContent = pending;
      failedBadge.style.display = pending > 0 ? 'flex' : 'none';
    }
  }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  window.invoicePlanner = new InvoicePlanner();
});
