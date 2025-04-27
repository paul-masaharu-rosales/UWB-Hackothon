/**
 * MediTrack - PDF Report Generator
 * This file handles client-side PDF generation using jsPDF
 */

// Main function to generate a PDF report
function generatePDFReport() {
  console.log("Generating PDF report...");
  
  // Show loading spinner
  showLoadingSpinner();
  
  // Fetch report data from server
  fetch('/get_report_data')
    .then(response => {
      console.log("Get report data response status:", response.status);
      // Log the actual response text for debugging
      return response.text().then(text => {
        try {
          // Try to parse as JSON
          const data = JSON.parse(text);
          return data;
        } catch (e) {
          // If it's not valid JSON (like HTML), log it and throw an error
          console.error("Server returned non-JSON response:", text.substring(0, 200) + "...");
          throw new Error("Server returned non-JSON response. Check server logs for details.");
        }
      });
    })
    .then(data => {
      // Hide loading spinner
      hideLoadingSpinner();
      console.log("Processed report data:", data);
      
      if (data.success === false) {
        showError(data.message || 'Failed to generate report data');
        return;
      }
      
      // Create PDF from the data
      try {
        createPDF(data);
        console.log("PDF created successfully");
      } catch (error) {
        console.error("Error creating PDF:", error);
        showError("Error creating PDF: " + error.message);
      }
    })
    .catch(error => {
      console.error('Error fetching report data:', error);
      hideLoadingSpinner();
      showError('An error occurred while generating the report: ' + error.message);
    });
}

// Function to create PDF from data
function createPDF(data) {
  // Initialize jsPDF
  const doc = new jspdf.jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  });
  
  // Set font styles
  doc.setFont('helvetica');
  
  // Add header
  addHeader(doc, data);
  
  // Add patient information
  addPatientInfo(doc, data.user);
  
  // Add journal entries
  addJournalEntries(doc, data.journals);
  
  // Add recovery plans
  addRecoveryPlans(doc, data.plans);
  
  // Add footer
  addFooter(doc, data.generated_date);
  
  // Save the PDF
  doc.save(`${data.title.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`);
}

// Function to add header to PDF
function addHeader(doc, data) {
  // Add title
  doc.setFontSize(22);
  doc.setTextColor(30, 136, 229); // Primary blue
  doc.text(data.title, 105, 20, { align: 'center' });
  
  // Add subtitle
  doc.setFontSize(12);
  doc.setTextColor(100, 100, 100);
  doc.text(`Generated on: ${data.generated_date}`, 105, 28, { align: 'center' });
  
  // Add horizontal line
  doc.setDrawColor(30, 136, 229);
  doc.setLineWidth(0.5);
  doc.line(20, 32, 190, 32);
}

// Function to add patient information to PDF
function addPatientInfo(doc, user) {
  const startY = 40;
  
  // Section title
  doc.setFontSize(16);
  doc.setTextColor(30, 136, 229);
  doc.text('Patient Information', 20, startY);
  
  // Patient details
  doc.setFontSize(11);
  doc.setTextColor(60, 60, 60);
  
  let y = startY + 8;
  
  // Format user name
  const name = `${user.first_name || ''} ${user.last_name || ''}`.trim();
  const displayName = name ? name : 'Name not provided';
  
  // Add user details
  doc.text(`Name: ${displayName}`, 20, y); y += 6;
  doc.text(`Email: ${user.email}`, 20, y); y += 6;
  
  // Create two columns for remaining details
  // Left column
  if (user.age) doc.text(`Age: ${user.age} years`, 20, y);
  if (user.gender) doc.text(`Gender: ${formatGender(user.gender)}`, 105, y);
  y += 6;
  
  if (user.weight) doc.text(`Weight: ${user.weight} kg`, 20, y);
  if (user.height) doc.text(`Height: ${user.height} cm`, 105, y);
  y += 6;
  
  if (user.bmi) doc.text(`BMI: ${user.bmi}`, 20, y);
  y += 6;
  
  // Add horizontal line
  doc.setDrawColor(200, 200, 200);
  doc.setLineWidth(0.2);
  doc.line(20, y + 2, 190, y + 2);
  
  // Return the new Y position
  return y + 8;
}

// Function to add journal entries to PDF
function addJournalEntries(doc, journals) {
  if (!journals || journals.length === 0) {
    return 50; // Return early if no journals
  }
  
  let startY = 70;
  
  // Section title
  doc.setFontSize(16);
  doc.setTextColor(30, 136, 229);
  doc.text('Medical Journal Entries', 20, startY);
  startY += 8;
  
  // Column headers
  doc.setFontSize(10);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(80, 80, 80);
  doc.text('Date', 20, startY);
  doc.text('Symptom', 50, startY);
  doc.text('Severity', 120, startY);
  doc.text('Description', 140, startY);
  startY += 5;
  
  // Draw header line
  doc.setDrawColor(200, 200, 200);
  doc.setLineWidth(0.2);
  doc.line(20, startY, 190, startY);
  startY += 5;
  
  // Reset font
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9);
  doc.setTextColor(60, 60, 60);
  
  // Add journals
  journals.forEach((journal, index) => {
    // Check if we need a new page
    if (startY > 270) {
      doc.addPage();
      startY = 20;
    }
    
    const date = new Date(journal.date_experienced).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
    
    // Journal entries
    doc.text(date, 20, startY);
    doc.text(journal.symptom, 50, startY);
    doc.text(`${journal.severity}/10`, 120, startY);
    
    // Handle description text wrapping
    const description = journal.description || 'No description provided';
    const descriptionLines = doc.splitTextToSize(description, 50);
    doc.text(descriptionLines, 140, startY);
    
    // Calculate height for this row (based on description length)
    const lineHeight = 5;
    const rowHeight = Math.max(lineHeight, descriptionLines.length * lineHeight);
    
    startY += rowHeight + 2;
    
    // Add separator line (except after the last entry)
    if (index < journals.length - 1) {
      doc.setDrawColor(230, 230, 230);
      doc.setLineWidth(0.1);
      doc.line(20, startY - 1, 190, startY - 1);
    }
  });
  
  // Add horizontal line
  startY += 5;
  doc.setDrawColor(200, 200, 200);
  doc.setLineWidth(0.2);
  doc.line(20, startY, 190, startY);
  
  return startY + 8;
}

// Function to add recovery plans to PDF
function addRecoveryPlans(doc, plans) {
  if (!plans || plans.length === 0) {
    return; // Return early if no plans
  }
  
  let startY = 180;
  
  // Check if we need a new page
  if (startY > 250) {
    doc.addPage();
    startY = 20;
  }
  
  // Section title
  doc.setFontSize(16);
  doc.setTextColor(30, 136, 229);
  doc.text('Recovery Plans', 20, startY);
  startY += 10;
  
  // Add each plan
  plans.forEach((plan, index) => {
    // Check if we need a new page
    if (startY > 250) {
      doc.addPage();
      startY = 20;
    }
    
    // Plan title
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(30, 136, 229);
    doc.text(`${plan.title} (${formatPlanType(plan.plan_type)})`, 20, startY);
    startY += 6;
    
    // Plan description
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(60, 60, 60);
    
    const descriptionLines = doc.splitTextToSize(plan.description, 170);
    doc.text(descriptionLines, 20, startY);
    startY += descriptionLines.length * 5 + 5;
    
    // Check if we have recommendations
    if (plan.recommendations && plan.recommendations.length > 0) {
      doc.setFontSize(11);
      doc.setFont('helvetica', 'bold');
      doc.text('Recommendations:', 20, startY);
      startY += 5;
      
      // Reset font
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      
      // Add each recommendation
      plan.recommendations.forEach((rec, recIndex) => {
        // Check if we need a new page
        if (startY > 260) {
          doc.addPage();
          startY = 20;
        }
        
        // Priority indicator
        const priorityText = rec.priority === 1 ? 'High Priority' : 
                             rec.priority === 2 ? 'Medium Priority' : 'Low Priority';
        
        doc.setFont('helvetica', 'bold');
        doc.text(`${rec.title} (${priorityText})`, 25, startY);
        startY += 5;
        
        // Recommendation description
        doc.setFont('helvetica', 'normal');
        const recLines = doc.splitTextToSize(rec.description, 165);
        doc.text(recLines, 25, startY);
        startY += recLines.length * 4 + 4;
      });
    }
    
    // Add separator between plans
    if (index < plans.length - 1) {
      doc.setDrawColor(200, 200, 200);
      doc.setLineWidth(0.2);
      doc.line(20, startY, 190, startY);
      startY += 8;
    }
  });
}

// Function to add footer to PDF
function addFooter(doc, date) {
  // Get the current number of pages
  const pageCount = doc.internal.getNumberOfPages();
  
  // For each page, add the footer
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    
    doc.setFontSize(8);
    doc.setTextColor(100, 100, 100);
    
    // Add page number
    doc.text(`Page ${i} of ${pageCount}`, 20, 287);
    
    // Add app name
    doc.text('Generated by MediTrack - Medical Recovery Planner', 105, 287, { align: 'center' });
    
    // Add date
    doc.text(date, 190, 287, { align: 'right' });
  }
}

// Helper function to format gender
function formatGender(gender) {
  if (!gender) return 'Not specified';
  
  const genderMap = {
    'male': 'Male',
    'female': 'Female',
    'other': 'Other',
    'prefer_not_to_say': 'Prefer not to say'
  };
  
  return genderMap[gender] || gender;
}

// Helper function to format plan type
function formatPlanType(planType) {
  if (!planType) return 'General';
  
  const typeMap = {
    'general': 'General Recovery',
    'nutrition': 'Nutrition Plan',
    'sports': 'Sports Recovery'
  };
  
  return typeMap[planType] || planType;
}

// Function to show loading spinner
function showLoadingSpinner() {
  const container = document.getElementById('reportGenerationStatus');
  if (!container) return;
  
  container.innerHTML = `
    <div class="d-flex align-items-center text-primary">
      <div class="spinner-border spinner-border-sm me-2" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <span>Generating PDF report...</span>
    </div>
  `;
  container.style.display = 'block';
}

// Function to hide loading spinner
function hideLoadingSpinner() {
  const container = document.getElementById('reportGenerationStatus');
  if (!container) return;
  
  container.style.display = 'none';
}

// Function to show error message
function showError(message) {
  const container = document.getElementById('reportGenerationStatus');
  if (!container) return;
  
  container.innerHTML = `
    <div class="alert alert-danger">
      <i class="fas fa-exclamation-triangle me-2"></i>
      ${message}
    </div>
  `;
  container.style.display = 'block';
}

// Function to prepare report data
function prepareReport() {
  console.log("Preparing report data...");
  
  // Get form data
  const form = document.getElementById('reportForm');
  if (!form) {
    console.error("Report form not found!");
    return;
  }
  
  // Check if any items are selected
  const selectedJournals = form.querySelectorAll('input[name="journal_ids"]:checked');
  const selectedPlans = form.querySelectorAll('input[name="plan_ids"]:checked');
  
  if (selectedJournals.length === 0 && selectedPlans.length === 0) {
    showError("Please select at least one symptom or recovery plan for the report.");
    return;
  }
  
  console.log(`Selected items: ${selectedJournals.length} journals and ${selectedPlans.length} plans`);
  
  const formData = new FormData(form);
  
  // Show loading message
  showLoadingSpinner();
  
  // Send request to server
  fetch('/generate_report', {
    method: 'POST',
    body: formData,
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(response => {
    console.log("Response status:", response.status);
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}: ${response.statusText}`);
    }
    return response.json();
  })
  .then(data => {
    console.log("Response data:", data);
    if (data.success) {
      // Generate PDF
      generatePDFReport();
    } else {
      hideLoadingSpinner();
      showError(data.message || 'Failed to prepare report data');
    }
  })
  .catch(error => {
    console.error('Error preparing report:', error);
    hideLoadingSpinner();
    showError('An error occurred while preparing the report: ' + error.message);
  });
}



// Initialize event listeners when document is ready
document.addEventListener('DOMContentLoaded', function() {
  const generateReportBtn = document.getElementById('generateReportBtn');
  if (generateReportBtn) {
    generateReportBtn.addEventListener('click', function(e) {
      e.preventDefault();
      prepareReport();
    });
  }
});
