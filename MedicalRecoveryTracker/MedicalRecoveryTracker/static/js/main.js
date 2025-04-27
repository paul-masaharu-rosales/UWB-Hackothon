/**
 * MediTrack - Main JavaScript File
 * This file contains general functionality for the application
 */

// Initialize all components when the document is ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips
  initTooltips();
  
  // Setup form validation
  setupFormValidation();
  
  // Initialize date pickers
  initDatePickers();
  
  // Setup event listeners
  setupEventListeners();
  
  // Setup symptom severity display
  setupSeverityDisplay();
});

// Function to initialize Bootstrap tooltips
function initTooltips() {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

// Function to setup form validation
function setupFormValidation() {
  // Get all forms with the class 'needs-validation'
  const forms = document.querySelectorAll('.needs-validation');
  
  // Loop over them and prevent submission if they're invalid
  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      
      form.classList.add('was-validated');
    }, false);
  });
}

// Function to initialize date pickers
function initDatePickers() {
  // Get all date inputs
  const dateInputs = document.querySelectorAll('input[type="date"]');
  
  // Set default value to today if empty
  dateInputs.forEach(input => {
    if (!input.value) {
      const today = new Date().toISOString().split('T')[0];
      input.value = today;
    }
  });
}

// Function to setup event listeners
function setupEventListeners() {
  // Symptom severity slider value display
  const severitySlider = document.getElementById('severity');
  const severityValue = document.getElementById('severityValue');
  
  if (severitySlider && severityValue) {
    // Update the value display when the slider changes
    severitySlider.addEventListener('input', function() {
      severityValue.textContent = this.value;
      
      // Update the color based on severity
      updateSeverityColor(this.value, severityValue);
    });
    
    // Set initial value and color
    if (severitySlider.value) {
      severityValue.textContent = severitySlider.value;
      updateSeverityColor(severitySlider.value, severityValue);
    }
  }
  
  // For recovery plan checkbox selection
  const planCheckboxes = document.querySelectorAll('.plan-checkbox');
  const generatePlanBtn = document.getElementById('generatePlanBtn');
  
  if (planCheckboxes.length > 0 && generatePlanBtn) {
    // Disable/enable the generate button based on checkbox selection
    planCheckboxes.forEach(checkbox => {
      checkbox.addEventListener('change', function() {
        const checkedCount = document.querySelectorAll('.plan-checkbox:checked').length;
        generatePlanBtn.disabled = checkedCount === 0;
      });
    });
    
    // Initial check
    const initialCheckedCount = document.querySelectorAll('.plan-checkbox:checked').length;
    if (generatePlanBtn) {
      generatePlanBtn.disabled = initialCheckedCount === 0;
    }
  }
  
  // For select all functionality in reports
  const selectAllJournals = document.getElementById('selectAllJournals');
  const journalCheckboxes = document.querySelectorAll('.journal-checkbox');
  
  if (selectAllJournals && journalCheckboxes.length > 0) {
    selectAllJournals.addEventListener('change', function() {
      journalCheckboxes.forEach(checkbox => {
        checkbox.checked = this.checked;
      });
    });
  }
  
  const selectAllPlans = document.getElementById('selectAllPlans');
  const planReportCheckboxes = document.querySelectorAll('.plan-report-checkbox');
  
  if (selectAllPlans && planReportCheckboxes.length > 0) {
    selectAllPlans.addEventListener('change', function() {
      planReportCheckboxes.forEach(checkbox => {
        checkbox.checked = this.checked;
      });
    });
  }
}

// Function to update severity color
function updateSeverityColor(value, element) {
  // Remove existing classes
  element.classList.remove('text-success', 'text-warning', 'text-danger');
  
  // Add appropriate class based on severity
  if (value <= 3) {
    element.classList.add('text-success');
  } else if (value <= 7) {
    element.classList.add('text-warning');
  } else {
    element.classList.add('text-danger');
  }
}

// Function to setup symptom severity display
function setupSeverityDisplay() {
  // Get all severity display elements
  const severityElements = document.querySelectorAll('.symptom-severity');
  
  severityElements.forEach(element => {
    const severity = parseInt(element.getAttribute('data-severity') || element.textContent);
    
    // Add appropriate class based on severity
    if (severity <= 3) {
      element.classList.add('severity-low');
    } else if (severity <= 7) {
      element.classList.add('severity-medium');
    } else {
      element.classList.add('severity-high');
    }
  });
}

// Function to confirm deletion
function confirmDelete(event, itemType) {
  if (!confirm(`Are you sure you want to delete this ${itemType}? This action cannot be undone.`)) {
    event.preventDefault();
    return false;
  }
  return true;
}
