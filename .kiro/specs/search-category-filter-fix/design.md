# Search Category Filter Fix - Bugfix Design

## Overview

The search page category filter buttons (hackathon, scholarship, internship, skill_program) are not triggering a search when clicked. Users can select a category filter, but the page continues to display all opportunities instead of filtering by the selected category. The root cause is that the `useEffect` hook in `Opportunities.jsx` only triggers `searchOpportunities()` when `selectedType` or `isAISearch` changes, but when a user first lands on the page without any search query, clicking a category button sets `selectedType` but doesn't trigger a search because the `useEffect` has a guard condition `if (searchQuery || selectedType)` that prevents execution when `searchQuery` is empty on initial load. Additionally, the search is never triggered automatically when the page loads with no filters.

The fix will ensure that clicking any category filter button immediately triggers a search request with the selected category type parameter, regardless of whether a search query is present.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when a user clicks a category filter button and no search is triggered
- **Property (P)**: The desired behavior when category filters are clicked - the system should immediately execute a search filtered by the selected category
- **Preservation**: Existing search functionality (text search, AI mode, "All" button, combined filters) that must remain unchanged by the fix
- **searchOpportunities**: The function in `web/src/pages/Opportunities.jsx` that executes the API call to fetch filtered opportunities
- **selectedType**: The state variable that stores the currently selected category filter (null for "All", or one of: 'hackathon', 'scholarship', 'internship', 'skill_program')
- **useEffect**: React hook that runs side effects when dependencies change - currently triggers search when `selectedType` or `isAISearch` changes

## Bug Details

### Fault Condition

The bug manifests when a user clicks any of the four category filter buttons (hackathon, scholarship, internship, skill_program) without having entered a search query. The `selectedType` state updates correctly, but the `searchOpportunities()` function is not called, so no filtered results are displayed.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type { buttonType: string, currentSearchQuery: string, currentSelectedType: string | null }
  OUTPUT: boolean
  
  RETURN input.buttonType IN ['hackathon', 'scholarship', 'internship', 'skill_program']
         AND input.currentSearchQuery === ''
         AND input.currentSelectedType !== input.buttonType
         AND NOT searchTriggered(input.buttonType)
END FUNCTION
```

### Examples

- User lands on `/opportunities` page with no search query → clicks "hackathon" button → Expected: displays only hackathons, Actual: displays nothing (or stale results)
- User lands on `/opportunities` page with no search query → clicks "scholarship" button → Expected: displays only scholarships, Actual: displays nothing (or stale results)
- User searches for "AI" → clicks "internship" button → Expected: displays AI-related internships, Actual: works correctly (search query exists)
- User clicks "hackathon" button → clears search query → clicks "scholarship" button → Expected: displays all scholarships, Actual: may not update correctly

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Clicking the "All" filter button must continue to display opportunities from all categories
- Entering a search query and clicking Search must continue to filter opportunities by the search term
- Toggling AI Mode on and entering a search query must continue to perform semantic search
- Clicking the Search button must continue to execute the search with current filters
- The results count display must continue to show the correct number of filtered results
- Combining a search query with a category filter must continue to apply both filters together

**Scope:**
All inputs that do NOT involve clicking a category filter button (hackathon, scholarship, internship, skill_program) should be completely unaffected by this fix. This includes:
- Text input in the search field
- Clicking the Search button
- Toggling AI Mode on/off
- Clicking the "All" button
- Form submission via Enter key

## Hypothesized Root Cause

Based on the bug description and code analysis, the most likely issues are:

1. **Missing useEffect Trigger**: The `useEffect` hook has a guard condition `if (searchQuery || selectedType)` that prevents `searchOpportunities()` from running when `searchQuery` is empty, even though `selectedType` has changed. This means clicking a category button on initial page load (with no search query) won't trigger a search.

2. **No Initial Load**: When the page first loads with no filters selected, no search is triggered automatically, so the page shows no results until the user takes action.

3. **Dependency Logic Issue**: The `useEffect` dependencies are `[selectedType, isAISearch]`, which is correct, but the guard condition inside the effect prevents execution even when dependencies change.

4. **State Update Timing**: The category button `onClick` handlers call `setSelectedType(type)`, which updates state asynchronously. The `useEffect` should handle this, but the guard condition blocks execution.

## Correctness Properties

Property 1: Fault Condition - Category Filter Triggers Search

_For any_ user interaction where a category filter button (hackathon, scholarship, internship, skill_program) is clicked, the fixed code SHALL immediately trigger a search request with the selected category type parameter, regardless of whether a search query is present, and SHALL display only opportunities matching the selected category.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

Property 2: Preservation - Non-Category-Filter Behavior

_For any_ user interaction that is NOT clicking a category filter button (text search, AI mode toggle, "All" button, Search button, combined filters), the fixed code SHALL produce exactly the same behavior as the original code, preserving all existing search and filter functionality.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File**: `web/src/pages/Opportunities.jsx`

**Function**: `useEffect` hook (lines 17-21)

**Specific Changes**:
1. **Remove Guard Condition**: Remove or modify the `if (searchQuery || selectedType)` guard condition in the `useEffect` hook to allow search execution when only `selectedType` is set (even if `searchQuery` is empty).

2. **Trigger Search on Category Selection**: Ensure that when `selectedType` changes to a non-null value, `searchOpportunities()` is called immediately, regardless of `searchQuery` state.

3. **Handle "All" Button**: Ensure that clicking "All" (which sets `selectedType` to null) triggers a search to display all opportunities, or clears the results appropriately.

4. **Preserve Existing Logic**: Maintain the existing behavior where changing `isAISearch` triggers a search, and where having both `searchQuery` and `selectedType` works correctly.

5. **Optional - Initial Load**: Consider triggering an initial search on component mount to display all opportunities by default (this may be a separate enhancement).

**Proposed Implementation**:
```javascript
useEffect(() => {
  // Trigger search whenever selectedType or isAISearch changes
  // OR when there's a searchQuery present
  if (searchQuery || selectedType !== null || isAISearch) {
    searchOpportunities();
  }
}, [selectedType, isAISearch]);
```

Or alternatively, remove the guard entirely and let the API handle empty parameters:
```javascript
useEffect(() => {
  searchOpportunities();
}, [selectedType, isAISearch]);
```

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Fault Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write tests that simulate clicking category filter buttons in various scenarios and assert that `searchOpportunities()` is called with the correct parameters. Run these tests on the UNFIXED code to observe failures and understand the root cause.

**Test Cases**:
1. **Initial Load + Category Click**: Load page with no query → click "hackathon" → assert search is triggered with type='hackathon' (will fail on unfixed code)
2. **Category Switch**: Click "hackathon" → click "scholarship" → assert search is triggered with type='scholarship' (will fail on unfixed code if no query)
3. **Empty Query + Category**: Clear search query → click "internship" → assert search is triggered with type='internship' (will fail on unfixed code)
4. **All Button**: Click "hackathon" → click "All" → assert search is triggered with type=null (may fail on unfixed code)

**Expected Counterexamples**:
- `searchOpportunities()` is not called when category buttons are clicked without a search query
- Possible causes: guard condition in useEffect, missing dependency, incorrect state update handling

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition(input) DO
  result := handleCategoryClick_fixed(input)
  ASSERT searchTriggered(result)
  ASSERT displayedOpportunities.every(opp => opp.type === input.buttonType)
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT handleSearch_original(input) = handleSearch_fixed(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for text search, AI mode, and "All" button, then write property-based tests capturing that behavior.

**Test Cases**:
1. **Text Search Preservation**: Observe that entering a search query and clicking Search works correctly on unfixed code, then write test to verify this continues after fix
2. **AI Mode Preservation**: Observe that toggling AI Mode and searching works correctly on unfixed code, then write test to verify this continues after fix
3. **All Button Preservation**: Observe that clicking "All" works correctly on unfixed code, then write test to verify this continues after fix
4. **Combined Filters Preservation**: Observe that combining search query + category filter works correctly on unfixed code, then write test to verify this continues after fix

### Unit Tests

- Test category button click handlers update `selectedType` state correctly
- Test that `searchOpportunities()` is called when `selectedType` changes
- Test that "All" button sets `selectedType` to null and triggers search
- Test that search parameters are constructed correctly for each category type
- Test edge cases (rapid clicking, switching between categories)

### Property-Based Tests

- Generate random sequences of category button clicks and verify each triggers a search with correct parameters
- Generate random combinations of search queries and category filters and verify both are applied
- Test that all non-category interactions (text input, AI toggle, Search button) continue to work across many scenarios

### Integration Tests

- Test full user flow: land on page → click category → see filtered results
- Test switching between categories and verify results update correctly
- Test combining text search with category filters in various orders
- Test that results count updates correctly when filters are applied
- Test that visual feedback (active button state) matches the applied filter
