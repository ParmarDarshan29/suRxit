describe('Dashboard E2E', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should load the dashboard and show prescription form', () => {
    cy.contains('Analyze Prescription').should('be.visible');
    cy.get('textarea[placeholder*="prescription"]').should('be.visible');
    cy.get('input[type="file"]').should('be.visible');
  });

  it('should submit prescription form and show results', () => {
    // Fill out form
    cy.get('textarea[placeholder*="prescription"]')
      .type('Warfarin 5mg daily, Aspirin 81mg daily');
    
    // Check some allergies
    cy.contains('Penicillin').click();
    cy.contains('Aspirin').click();

    // Submit form
    cy.contains('Analyze Prescription').click();

    // Wait for loading to complete and check results
    cy.contains('Analyzing...', { timeout: 2000 });
    cy.contains('Drug–Drug Interactions', { timeout: 5000 }).should('be.visible');
    cy.contains('Drug–Food Interactions', { timeout: 5000 }).should('be.visible');
    cy.contains('Home Remedies', { timeout: 5000 }).should('be.visible');
  });

  it('should open and interact with chatbot', () => {
    cy.get('[aria-label="Open Chatbot"]').click();
    cy.contains('MedLM Assistant').should('be.visible');
    cy.get('[aria-label="Chat input"]').type('What foods should I avoid?');
    cy.contains('Send').click();
  });

  it('should navigate to patient portal', () => {
    cy.contains('Patient Portal').click();
    cy.url().should('include', '/patient');
    cy.contains('Your Medication Dashboard').should('be.visible');
  });
});