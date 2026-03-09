# Bug Condition Exploration Test Results

## Test Execution Date
2024-03-08

## Test Environment
- Framework: Vitest + @testing-library/react + fast-check
- Test File: `web/src/pages/Opportunities.test.jsx`
- Code Under Test: `web/src/pages/Opportunities.jsx` (UNFIXED)

## Test Results Summary

### Property 1: Category Filter Triggers Search (Property-Based Test)
**Status**: ✓ PASSED (20 runs)
**Expected**: FAIL
**Actual**: PASS

This property-based test generated 20 random category selections and verified that clicking each category button triggers a search. All 20 test cases passed, indicating that clicking category buttons DOES trigger searches when `searchQuery` is empty.

### Test Case 1: Initial load + hackathon category click
**Status**: ✓ PASSED
**Expected**: FAIL
**Actual**: PASS

When loading the page with no search query and clicking the "hackathon" button, the search IS triggered correctly with `{ type: ['hackathon'] }`.

### Test Case 2: Category switch (hackathon -> scholarship)
**Status**: ✓ PASSED
**Expected**: FAIL
**Actual**: PASS

When clicking "hackathon" then switching to "scholarship", the search IS triggered correctly with `{ type: ['scholarship'] }`.

### Test Case 3: Empty query + internship category
**Status**: ✓ PASSED
**Expected**: FAIL
**Actual**: PASS

When the search query is empty and clicking the "internship" button, the search IS triggered correctly with `{ type: ['internship'] }`.

### Test Case 4: All button after category selection
**Status**: × FAILED
**Expected**: FAIL
**Actual**: FAIL ✓ (This is the expected failure!)

**Counterexample Found**: When clicking a category button (e.g., "skill_program") and then clicking the "All" button with an empty search query, the search is NOT triggered.

**Root Cause**: When clicking "All", `selectedType` is set to `null`. With an empty `searchQuery`, the guard condition `if (searchQuery || selectedType)` evaluates to `if ('' || null)` which is `false`, preventing `searchOpportunities()` from being called.

## Analysis

### Unexpected Findings

The bug description stated that clicking category buttons without a search query would NOT trigger searches. However, testing revealed that:

1. **Category buttons DO trigger searches**: When `selectedType` changes from `null` to a category value (e.g., `'hackathon'`), the guard condition `if (searchQuery || selectedType)` evaluates to `true` because the category value is truthy, so `searchOpportunities()` IS called.

2. **The actual bug is with the "All" button**: The bug manifests when clicking the "All" button (which sets `selectedType` to `null`) with an empty search query. In this case, the guard condition evaluates to `false`, preventing the search from executing.

### Confirmed Bug Condition

**Bug Condition**: Clicking the "All" button after selecting a category, when `searchQuery` is empty, does NOT trigger a search to display all opportunities.

**Formal Specification**:
```
FUNCTION isBugCondition(input)
  INPUT: input of type { buttonType: string, currentSearchQuery: string, currentSelectedType: string | null }
  OUTPUT: boolean
  
  RETURN input.buttonType === 'All'
         AND input.currentSearchQuery === ''
         AND input.currentSelectedType !== null
         AND NOT searchTriggered()
END FUNCTION
```

### Code Analysis

The problematic code in `web/src/pages/Opportunities.jsx` (lines 17-21):

```javascript
useEffect(() => {
  if (searchQuery || selectedType) {
    searchOpportunities();
  }
}, [selectedType, isAISearch]);
```

**Issue**: The guard condition `if (searchQuery || selectedType)` prevents execution when both values are falsy. When `selectedType` is `null` (after clicking "All") and `searchQuery` is empty, the condition is false.

### Implications

1. **Category filter buttons work correctly**: The original bug description may have been based on a misunderstanding or a different scenario. The category buttons DO trigger searches.

2. **"All" button is broken**: Users cannot return to viewing all opportunities after selecting a category unless they have a search query entered.

3. **User experience impact**: Users who click a category button and then want to see all opportunities again by clicking "All" will see stale results (the last category they selected) instead of all opportunities.

## Recommendations

### Fix Strategy

The fix should ensure that clicking "All" (setting `selectedType` to `null`) triggers a search even when `searchQuery` is empty. Possible approaches:

1. **Option 1**: Change the guard condition to explicitly check for `selectedType !== undefined`:
   ```javascript
   if (searchQuery || selectedType !== undefined) {
     searchOpportunities();
   }
   ```

2. **Option 2**: Remove the guard condition entirely and always trigger search when dependencies change:
   ```javascript
   useEffect(() => {
     searchOpportunities();
   }, [selectedType, isAISearch]);
   ```

3. **Option 3**: Add `searchQuery` to the dependencies and remove the guard:
   ```javascript
   useEffect(() => {
     searchOpportunities();
   }, [selectedType, isAISearch, searchQuery]);
   ```

### Testing Strategy Update

Since the bug is specifically with the "All" button, the exploration tests should focus more on this scenario. Additional test cases to consider:

1. Multiple category switches ending with "All"
2. "All" button click on initial load (may also be broken)
3. "All" button with various search query states

## Conclusion

The bug condition exploration test successfully identified a bug in the "All" button functionality. While the original bug description focused on category filter buttons not triggering searches, testing revealed that the actual bug is with the "All" button not triggering a search when `searchQuery` is empty.

**Test Status**: Task 1 complete - bug confirmed via Test Case 4 failure.
**Next Steps**: Proceed to Task 2 (preservation tests) and Task 3 (implement fix).
