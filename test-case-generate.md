# eFamilyPro Life Insurance Application - Comprehensive Test Plan

## Application Overview

The eFamilyPro Life Insurance Application is a multi-page online insurance application on Hang Seng Bank's website. Users progress from generating a quote through to submitting a full application.

**Application URL:** `https://www.hangseng.com/en-hk/personal/insurance-mpf/digital-service/application/?formType=core&productCode=eFP`

**Critical Requirement:** All tests require geolocation API mocking via Playwright route interception to bypass the "Invalid location" dialog.

---

## Application Flow (Explored Pages)

| Step | Page Name | Key Elements | Status |
|------|-----------|-------------|--------|
| 1 | **Quote Form** | Gender, Smoking Habit, DOB, Sum Insured, Promo Code, PICS checkbox | ✅ Fully Explored |
| 2 | **Quote Result** | Premium summary, Sum insured, Cover details, Apply now / Get new quote | ✅ Fully Explored |
| 3 | **Plan Selection (Cross-sell)** | Selected plan summary, Cross-sell products, Proceed / Back | ✅ Fully Explored |
| 4 | **Plan Details** | Product understanding docs, Plan brochure checkbox, Apply now / Back | ✅ Fully Explored |
| 5 | **Application Step 1/3** | Section A: Vulnerable Customer Assessment | ✅ Fully Explored |
| 5 | **Application Step 1/3** | Section B: Medical Information (3 health questions) | ✅ Fully Explored |
| 5 | **Application Step 1/3** | Section C: Personal Details (Name, HKID, DOB, Place of Birth, Email, Beneficiary) | ✅ Fully Explored |
| 5 | **Application Step 1/3** | Section D: Premium Payment | ⚠️ Partially Explored (requires filling C first) |
| 6 | **Application Step 2/3** | Review & Declaration | ⚠️ Blocked (requires completing Step 1) |
| 7 | **Application Step 3/3** | Confirmation | ⚠️ Blocked (requires completing Steps 1-2) |

---

## Geolocation Bypass Strategy

### Playwright Route Interception (Verified Working)

```typescript
// In test.beforeEach or fixture setup
await page.route('**/*get-location-country*', async route => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ countryCode: 'HK', countryName: 'HK' }),
  });
});
```

**Why this works:** The application calls `rbwm-api.hsbc.com.hk/pws-hk-hase-gogingeronion-papi-prod-proxy/v1/get-location-country` during page load. Playwright route interception catches this at the network level before the browser processes the response.

---

## File Structure (Page Object Model)

```
__tests__/
├── e2e/
│   ├── pages/
│   │   ├── base-page.ts                              # Base page with shared logic & geo bypass
│   │   ├── efamilypro-quote-page.ts                  # Page 1: Quote form
│   │   ├── efamilypro-quote-result-page.ts           # Page 2: Quote results
│   │   ├── efamilypro-plan-selection-page.ts         # Page 3: Plan selection / cross-sell
│   │   ├── efamilypro-plan-details-page.ts           # Page 4: Plan details & understanding
│   │   ├── efamilypro-application-page.ts            # Page 5: Application Step 1/3
│   │   ├── efamilypro-vulnerable-customer-dialog.ts  # VCA modal dialog component
│   │   └── efamilypro-medical-section.ts             # Section B: Medical information component
│   ├── efamilypro-quote.spec.ts                      # Quote page tests
│   ├── efamilypro-quote-result.spec.ts               # Quote result tests
│   ├── efamilypro-plan-selection.spec.ts             # Plan selection tests
│   ├── efamilypro-plan-details.spec.ts               # Plan details tests
│   ├── efamilypro-application.spec.ts                # Application form tests (Step 1/3)
│   ├── efamilypro-e2e-flow.spec.ts                   # Full E2E happy path flow
│   └── efamilypro-geolocation.spec.ts                # Geolocation bypass verification tests
└── constants/
    └── test-data.ts                                  # All test data constants
```

---

## Page Object Designs

### 1. BasePage (`base-page.ts`)

**Shared Logic:**
- `setupGeolocationBypass()` — route interception for all tests
- `dismissCookieBanner()` — close cookie consent if visible
- `waitForPageLoad()` — wait for main content to be ready

---

### 2. QuotePage (`efamilypro-quote-page.ts`)

**Locators:**
| Element | Selector Description | Ref |
|---------|---------------------|-----|
| cookieCloseButton | button "Close" | e11 |
| eligibilityAlert | alert banner | e100 |
| promotionalBanner | promotional section | e106 |
| viewDetailsButton | button "View details" | e115 |
| planNameDisplay | text "eFamilyPro Life Insurance Plan" | e121 |
| genderMaleRadio | radio "Male" | e132 |
| genderFemaleRadio | radio "Female" | e135 |
| smokingTooltip | button tooltip on smoking | e142 |
| smokerRadio | radio "Smoker" | e144 |
| nonSmokerRadio | radio "Non-Smoker" | e147 |
| dobTooltip | button tooltip on DOB | e154 |
| dobInput | textbox "Date of birth" | e156 |
| datePickerButton | button "Select date" | e157 |
| sumInsuredTooltip | button tooltip on sum insured | e162 |
| sumInsuredDropdown | combobox "How much cover" | e164 |
| promoCodeInput | textbox "Promo code" | e175 |
| picsCheckbox | checkbox PICS agreement | e184 |
| picsLink | link to PICS PDF | e189 |
| clearButton | button "Clear" | e193 |
| getQuoteButton | button "Get a quote" | e194 |

**Methods:**
- `goto()` — navigate with geo bypass
- `selectGender(gender: 'Male' | 'Female')`
- `selectSmokingHabit(habit: 'Smoker' | 'Non-Smoker')`
- `fillDateOfBirth(date: string)` — DD/MM/YYYY format
- `selectSumInsured(amount: string)` — e.g. 'HKD 2,000,000'
- `fillPromoCode(code: string)`
- `checkPicsAgreement()`
- `clickGetQuote()` — returns `QuoteResultPage`
- `clickClear()`
- `fillCompleteForm(data)` — fills all fields + checkbox

**Sum Insured Options (age ≤ 50):**
- HKD 8,000,000, HKD 6,500,000, HKD 5,000,000, HKD 3,500,000
- HKD 3,000,000, HKD 2,000,000, HKD 1,500,000, HKD 1,000,000, HKD 500,000

---

### 3. QuoteResultPage (`efamilypro-quote-result-page.ts`)

**Locators:**
| Element | Selector Description | Ref |
|---------|---------------------|-----|
| resultHeading | heading "Your quote result" | e292 |
| quoteSummaryHeading | heading "Quote summary" | e295 |
| planNameHeading | heading "eFamilyPro Life Insurance Plan" | e297 |
| premiumSummaryHeading | heading "Premium summary" | e306 |
| monthlyPremiumAmount | text "HKD xxx.xx" | e312 |
| premiumBreakdown | premium details text | e313 |
| sumInsuredValue | text "HKD 2,000,000" | e321 |
| deathBenefitItem | listitem "Death Benefit" | e324 |
| getNewQuoteButton | button "Get a new quote" | e325 |
| applyNowButton | button "Apply now" | e326 |
| premiumIllustrationLink | link "Premium Illustration" | e340 |

**Methods:**
- `getMonthlyPremium()` — returns premium text
- `getSumInsured()` — returns sum insured text
- `clickApplyNow()` — returns `PlanSelectionPage`
- `clickGetNewQuote()` — returns `QuotePage`
- `verifyQuoteResult(expectedPremium, expectedSum)`

---

### 4. PlanSelectionPage (`efamilypro-plan-selection-page.ts`)

**Locators:**
| Element | Selector Description | Ref |
|---------|---------------------|-----|
| selectedPlanHeading | heading "Your selected plan(s)" | e341 |
| planCountHeading | heading "1 plan(s) selected" | e348 |
| selectedPlanLabel | heading "Selected plan:" | e351 |
| totalPremiumLabel | text "Total first premium to be paid:" | e354 |
| totalPremiumAmount | text "HKD171.97" | e355 |
| showMoreButton | button "Show more" | e357 |
| crossSellHeading | heading "You may be interested in" | e359 |
| learnMoreButtons | button "Learn more" | e374, e385, e399, e409 |
| showAllPlansLink | link "Show all other plans" | e387 |
| backButton | button "Back" | e410 |
| proceedButton | button "Proceed" | e411 |

**Methods:**
- `getSelectedPlanName()` — returns plan name text
- `getTotalPremium()` — returns total premium amount
- `clickProceed()` — returns `PlanDetailsPage`
- `clickBack()` — returns `QuoteResultPage`
- `clickLearnMore(planIndex)`
- `clickShowAllPlans()`

---

### 5. PlanDetailsPage (`efamilypro-plan-details-page.ts`)

**Locators:**
| Element | Selector Description | Ref |
|---------|---------------------|-----|
| quotationSummaryHeading | heading "Quotation summary" | e436 |
| planDetailsHeading | heading "Plan details" | e465 |
| planAccordion | link "eFamilyPro Life Insurance Plan" | e468 |
| objectiveText | text about term life plan | e484 |
| productTypeText | text about plan type | e488 |
| paymentPeriodText | text about payment period | e492 |
| affordabilityText | text about affordability risk | e496 |
| productBrochureLink | link "Product brochure" | e501 |
| policyProvisionsLink | link "Policy provisions" | e502 |
| premiumIllustrationLink | link "Premium Illustration" | e503 |
| productCheckbox | checkbox "I have read and understood" | e509 |
| backButton | button "Back" | e511 |
| applyNowButton | button "Apply now" | e512 |

**Methods:**
- `checkProductUnderstanding()`
- `clickApplyNow()` — returns `ApplicationPage`
- `clickBack()` — returns `PlanSelectionPage`
- `verifyPlanDocLinks()`

---

### 6. ApplicationPage (`efamilypro-application-page.ts`)

**Locators - Section A (Vulnerable Customer Assessment):**
| Element | Selector Description | Ref |
|---------|---------------------|-----|
| stepIndicator | text "Step 1 of 3" | e516 |
| sectionALink | link "A Vulnerable Customer assessment" | e523 |
| vcaStartButton | button "Start" | e535 |
| vcaHelpButton | button "View help for Vulnerable Customer" | e533 |

**Locators - VCA Dialog:**
| Element | Selector Description | Ref |
|---------|---------------------|-----|
| vcaDialogHeading | heading "Vulnerable Customer Assessment" | e575 |
| vcaCloseButton | button "Close" | e581 |
| q1Education | radiogroup "Have you completed Secondary 3 or above?" | e596 |
| q2Assets | radiogroup "Are your total net liquid assets..." | e608 |
| q3Income | radiogroup "Do you have any regular source of income?" | e620 |
| q4Experience | radiogroup "Do you have any experience in applying for life insurance..." | e631 |
| seeResultButton | button "See result" | e641 |
| vcaAcknowledgeCheckbox | checkbox "I acknowledge that I have read" | e693 |
| vcaConfirmButton | button "Confirm" | e697 |
| vcaBackButton | button "Back" | e696 |

**Locators - Section B (Medical Information):**
| Element | Selector Description | Ref |
|---------|---------------------|-----|
| sectionBButton | button "B Medical information" | e536 |
| q1Cancer | radiogroup "Have you ever been diagnosed with Cancer..." | e709 |
| q2ChronicConditions | radiogroup "In past 5 years, have you been diagnosed..." | e720 |
| q3Symptoms | radiogroup "In the past year, have you had..." | e731 |

**Locators - Section C (Personal Details):**
| Element | Selector Description | Ref |
|---------|---------------------|-----|
| sectionCButton | button "C Personal details" | e540 |
| lastNameInput | textbox "Last name" | e747 |
| firstNameInput | textbox "First name" | e751 |
| hkidInput | textbox "Taxpayer Identification Number (TIN)" | e756 |
| dobDisplay | text "15/03/1990" (read-only from quote) | e761 |
| placeOfBirthDropdown | combobox "Place of Birth" | e766 |
| emailInput | textbox "Email address" | e774 |
| beneficiaryOwnEstate | radio "Own estate" | e783 |
| beneficiaryAddNew | radio "Add beneficiary" | e787 |
| personalDeclarationCheckbox | checkbox "I hereby declare..." | e796 |

**Locators - Section D (Premium Payment):**
| Element | Selector Description | Ref |
|---------|---------------------|-----|
| sectionDLink | link "D Premium payment" | e544 |

**Navigation:**
| Element | Selector Description | Ref |
|---------|---------------------|-----|
| backButton | button "Back" | e549 |
| nextButton | button "Next" | e550 |

**Methods:**
- `startVulnerableCustomerAssessment()`
- `completeVCA(answers)` — fill all 4 questions, see result, confirm
- `completeMedicalQuestions(answers)` — answer 3 medical questions
- `fillPersonalDetails(data)` — fill name, HKID, place of birth, email
- `selectBeneficiary(type: 'own-estate' | 'add-beneficiary')`
- `checkPersonalDeclaration()`
- `clickNext()` — proceed to Step 2/3
- `clickBack()` — go back to Plan Details

---

## Test Scenarios

### Suite 1: Quote Page Tests (`efamilypro-quote.spec.ts`)

#### 1.1 Form Validation
| # | Test Name | Priority |
|---|-----------|----------|
| 1 | should display validation errors for empty form submission | Critical |
| 2 | should display validation error for missing PICS checkbox | Critical |
| 3 | should display validation error for invalid date format | High |
| 4 | should display validation error for future date of birth | High |
| 5 | should display validation errors state @visual | High |

#### 1.2 Happy Path
| # | Test Name | Priority |
|---|-----------|----------|
| 6 | should submit quote - Male Non-Smoker | Critical |
| 7 | should submit quote - Female Smoker | Critical |
| 8 | should submit quote with promo code | Medium |
| 9 | should clear all form fields with Clear button | Medium |

#### 1.3 Visual Regression
| # | Test Name | Priority |
|---|-----------|----------|
| 10 | should display quote form initial state @visual | High |
| 11 | should display quote form filled state @visual | High |
| 12 | should display eligibility alert @visual | Medium |
| 13 | should display promotional banner @visual | Medium |
| 14 | should display help section @visual | Low |

#### 1.4 Edge Cases
| # | Test Name | Priority |
|---|-----------|----------|
| 15 | should filter sum insured options by age (> 50) | High |
| 16 | should show all sum insured options for age ≤ 50 | High |
| 17 | should open PICS PDF in new tab | Medium |
| 18 | should display tooltips on click | Medium |
| 19 | should handle age boundary - minimum eligible age | Medium |
| 20 | should handle age boundary - maximum eligible age | Medium |

#### 1.5 Accessibility
| # | Test Name | Priority |
|---|-----------|----------|
| 21 | should support keyboard navigation through form | Medium |
| 22 | should have visible focus indicators | Medium |

---

### Suite 2: Quote Result Tests (`efamilypro-quote-result.spec.ts`)

| # | Test Name | Priority |
|---|-----------|----------|
| 1 | should display correct premium for Male Non-Smoker | Critical |
| 2 | should display correct sum insured amount | Critical |
| 3 | should display death benefit coverage | High |
| 4 | should navigate to plan selection via Apply now | Critical |
| 5 | should navigate back to quote form via Get new quote | High |
| 6 | should display premium illustration link | Medium |
| 7 | should display quote result @visual | High |
| 8 | should display levy breakdown correctly | Medium |

---

### Suite 3: Plan Selection Tests (`efamilypro-plan-selection.spec.ts`)

| # | Test Name | Priority |
|---|-----------|----------|
| 1 | should display selected plan summary | Critical |
| 2 | should display total premium amount | Critical |
| 3 | should proceed to plan details | Critical |
| 4 | should navigate back to quote result | High |
| 5 | should display cross-sell products | Medium |
| 6 | should expand plan details via Show more | Medium |
| 7 | should display plan selection page @visual | High |

---

### Suite 4: Plan Details Tests (`efamilypro-plan-details.spec.ts`)

| # | Test Name | Priority |
|---|-----------|----------|
| 1 | should display plan understanding sections | Critical |
| 2 | should require product checkbox before Apply | Critical |
| 3 | should proceed to application after checking checkbox | Critical |
| 4 | should navigate back to plan selection | High |
| 5 | should display product brochure link | Medium |
| 6 | should display policy provisions link | Medium |
| 7 | should display premium illustration link | Medium |
| 8 | should display plan details page @visual | High |

---

### Suite 5: Application Form Tests (`efamilypro-application.spec.ts`)

#### 5A: VCA Section
| # | Test Name | Priority |
|---|-----------|----------|
| 1 | should display VCA start screen | Critical |
| 2 | should complete VCA with all Yes answers | Critical |
| 3 | should display Non-Vulnerable Customer result | High |
| 4 | should require VCA acknowledgement checkbox | High |
| 5 | should handle VCA with mixed answers | Medium |
| 6 | should display VCA dialog @visual | High |

#### 5B: Medical Section
| # | Test Name | Priority |
|---|-----------|----------|
| 7 | should display 3 medical questions | Critical |
| 8 | should answer No to all medical questions | Critical |
| 9 | should handle Yes answer to cancer question | High |
| 10 | should validate all medical questions answered | High |

#### 5C: Personal Details Section
| # | Test Name | Priority |
|---|-----------|----------|
| 11 | should display personal details form fields | Critical |
| 12 | should fill in all personal details | Critical |
| 13 | should validate HKID format | High |
| 14 | should validate email format | High |
| 15 | should select beneficiary - Own estate | High |
| 16 | should select beneficiary - Add beneficiary | Medium |
| 17 | should display DOB from quote (read-only) | Medium |
| 18 | should display personal form @visual | High |

#### 5D: Premium Payment Section
| # | Test Name | Priority |
|---|-----------|----------|
| 19 | should display premium payment options | High |
| 20 | should fill payment details | High |

---

### Suite 6: E2E Full Flow Tests (`efamilypro-e2e-flow.spec.ts`)

| # | Test Name | Priority |
|---|-----------|----------|
| 1 | should complete full flow from quote to application Step 1 | Critical |
| 2 | should preserve data when navigating back from quote result | High |
| 3 | should handle different quote parameters in flow | High |
| 4 | should display step progress indicator | Medium |
| 5 | should complete flow visual regression @visual | High |

---

### Suite 7: Geolocation Bypass Tests (`efamilypro-geolocation.spec.ts`)

| # | Test Name | Priority |
|---|-----------|----------|
| 1 | should show Invalid location dialog WITHOUT bypass | Critical |
| 2 | should load page successfully WITH bypass | Critical |
| 3 | should intercept get-location-country API call | High |
| 4 | should maintain bypass across page navigation | High |
| 5 | should show geolocation dialog @visual | Medium |

---

## Test Data

```typescript
export const EFAMILYPRO_TEST_DATA = {
  URLS: {
    QUOTE_PAGE: 'https://www.hangseng.com/en-hk/personal/insurance-mpf/digital-service/application/?formType=core&productCode=eFP',
  },
  GEOLOCATION: {
    MOCK_ENDPOINT: '**/*get-location-country*',
    MOCK_RESPONSE: { countryCode: 'HK', countryName: 'HK' },
  },
  PROFILES: {
    MALE_NON_SMOKER: { gender: 'Male', smokingHabit: 'Non-Smoker', dob: '15/03/1990', sumInsured: 'HKD 2,000,000' },
    FEMALE_SMOKER: { gender: 'Female', smokingHabit: 'Smoker', dob: '22/08/1990', sumInsured: 'HKD 1,500,000' },
    OVER_50: { gender: 'Male', smokingHabit: 'Non-Smoker', dob: '01/01/1970', sumInsured: 'HKD 3,500,000' },
  },
  PERSONAL: {
    LAST_NAME: 'CHAN',
    FIRST_NAME: 'TAI MAN',
    HKID: 'A1234561',
    EMAIL: 'test.applicant@example.com',
    PLACE_OF_BIRTH: 'Hong Kong',
  },
  VCA_ALL_YES: { education: 'Yes', assets: 'Yes', income: 'Yes', experience: 'Yes' },
  MEDICAL_ALL_NO: { cancer: 'No', chronicConditions: 'No', symptoms: 'No' },
  SUM_INSURED_OPTIONS: [
    'HKD 8,000,000', 'HKD 6,500,000', 'HKD 5,000,000', 'HKD 3,500,000',
    'HKD 3,000,000', 'HKD 2,000,000', 'HKD 1,500,000', 'HKD 1,000,000', 'HKD 500,000',
  ],
  PROMO_CODES: { VALID: 'PROMO2026', INVALID: 'INVALIDCODE123' },
};
```

---

## Blockers & Next Steps

### Known Blockers

1. **Section D (Premium Payment)** — Requires completing sections A-C with valid data to unlock. Fields not yet mapped.
2. **Application Steps 2/3 and 3/3** — Blocked behind completing Step 1 with all valid personal/payment data.
3. **Confirmation Page** — Cannot access without full application submission.
4. **Payment Integration** — Unknown if test/sandbox payment methods exist.

### Resolved Blockers

- ✅ **Geolocation bypass** — Playwright route interception fully working
- ✅ **Page navigation** — Successfully navigated all 5 pages through to Application Step 1/3
- ✅ **Cross-sell page** — Identified as intermediate step (not originally documented)

### Implementation Status

- ✅ **Phase 1 (Complete):** All Page Objects and test specs implemented for Pages 1-5
  - 7 test spec files: quote, quote-result, plan-selection, plan-details, application, geolocation, e2e-flow
  - 6 Page Object Models: base, quote, quote-result, plan-selection, plan-details, application
  - 1 test data constants file
  - ~73 total test cases covering happy paths, edge cases, visual regression, and accessibility

### Next Steps

1. **Phase 2:** Fill Section C with valid test data, unlock Section D, explore premium payment fields
2. **Phase 3:** Complete Step 1/3, explore Steps 2/3 and 3/3, map remaining pages and create Page Objects
3. **Phase 4:** Add API mocking for quote calculation and form submissions for deterministic testing
4. **Phase 5:** Extend E2E flow tests once all pages are mapped to cover the full application journey

### Questions for Development Team

1. Is there a test/sandbox mode for payment processing?
2. Are there specific test HKID numbers that pass validation?
3. What are valid promo codes for testing?
4. Can application steps be deep-linked via URL parameters?
5. What is the session timeout duration?
