# Discover Page Performance Fix Bugfix Design

## Overview

The discover page's "For You" section suffers from critical performance and accuracy issues that create a poor user experience. The system currently loads all opportunities inefficiently, makes excessive database queries, has broken Redis caching, and displays misleading match percentages. This design outlines a comprehensive fix that addresses both performance bottlenecks and match percentage accuracy through optimized data fetching, proper caching implementation, and an improved scoring algorithm with proper normalization.

## Glossary

- **Bug_Condition (C)**: The condition that triggers performance issues and inaccurate match percentages - when the For You section loads or calculates recommendations
- **Property (P)**: The desired behavior when the For You section loads - efficient data loading with accurate match percentages in 0-100% range
- **Preservation**: Existing discover page functionality, opportunity card interactions, and empty state handling that must remain unchanged
- **For You Section**: The personalized recommendation area on the discover page that displays matched opportunities
- **Match Percentage**: The compatibility score displayed to users, should be normalized to 0-100% range
- **Redis Caching**: The caching layer that should store processed recommendation data to improve performance
- **Scoring Algorithm**: The logic that calculates how well an opportunity matches a user's profile and preferences

## Bug Details

### Fault Condition

The bug manifests when the For You section loads or when match percentages are calculated. The system either loads data inefficiently (causing performance issues), fails to use caching properly, or calculates inaccurate match percentages that mislead users about opportunity compatibility.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type PageLoadRequest OR MatchCalculationRequest
  OUTPUT: boolean
  
  RETURN (input.section == "ForYou" AND input.requestType == "load")
         OR (input.requestType == "calculateMatch" AND input.hasOpportunities == true)
         AND (inefficientDataLoading(input) OR brokenCaching(input) OR inaccurateScoring(input))
END FUNCTION
```

### Examples

- **Performance Issue**: User loads For You section → System queries all 10,000+ opportunities → Page takes 5+ seconds to load
- **Caching Issue**: Redis is enabled → System ignores cached data → Makes fresh database queries every time
- **Match Percentage Issue**: User sees "Match: -15%" → Confusing negative percentage from hard eligibility filter
- **Scoring Issue**: Two similar opportunities show vastly different percentages (23% vs 87%) due to simple algorithm
- **Edge Case**: User with no interests → System should show 0% matches, not crash or show negative values

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Other discover page sections (trending, recent, categories) must continue to work exactly as before
- Opportunity card click handling and navigation must remain unchanged
- Empty state messaging when no opportunities match must continue to display properly
- All opportunity details (title, description, tags, etc.) must continue to be shown correctly
- User interaction patterns (scrolling, filtering, searching) must remain unchanged

**Scope:**
All functionality that does NOT involve the For You section's data loading or match percentage calculation should be completely unaffected by this fix. This includes:
- Other page sections and their data loading
- Opportunity card UI components and interactions
- Navigation and routing behavior
- User authentication and session handling

## Hypothesized Root Cause

Based on the bug description, the most likely issues are:

1. **Inefficient Database Queries**: The system loads all opportunities before filtering
   - No database-level filtering by user preferences
   - Multiple separate queries during response formatting
   - Missing query optimization and indexing

2. **Broken Redis Caching Implementation**: The caching layer is not properly utilized
   - Cache keys may be incorrectly generated or invalidated
   - Cache hit/miss logic may be faulty
   - Serialization/deserialization issues with cached data

3. **Overly Simple Scoring Algorithm**: The current algorithm is too basic for accurate matching
   - Fixed point values (+10, +5) don't reflect real compatibility
   - No weighting based on importance of different factors
   - No consideration of user behavior or preferences strength

4. **Missing Score Normalization**: Raw scores are displayed without proper scaling
   - No conversion to 0-100% range
   - Negative scores from eligibility filters are shown directly
   - No handling of edge cases (no matches, perfect matches)

## Correctness Properties

Property 1: Fault Condition - Efficient Loading and Accurate Match Percentages

_For any_ request to load the For You section or calculate match percentages, the fixed system SHALL load data efficiently using optimized queries and caching, and SHALL display accurate match percentages normalized to 0-100% range that properly reflect opportunity compatibility.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

Property 2: Preservation - Non-For You Section Functionality

_For any_ user interaction that does NOT involve the For You section's data loading or match percentage calculation, the fixed system SHALL produce exactly the same behavior as the original system, preserving all existing discover page functionality and user interactions.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File**: `src/components/DiscoverPage/ForYouSection.js` (or similar)

**Function**: Data loading and recommendation logic

**Specific Changes**:
1. **Database Query Optimization**: Replace inefficient data loading
   - Implement database-level filtering by user preferences before loading
   - Use JOIN queries to fetch related data in single requests
   - Add proper indexing on frequently queried fields (user_id, interests, etc.)

2. **Redis Caching Implementation**: Fix broken caching layer
   - Implement proper cache key generation based on user profile
   - Add cache invalidation logic when user preferences change
   - Fix serialization/deserialization of cached recommendation data

3. **Improved Scoring Algorithm**: Replace simple point-based system
   - Implement weighted scoring based on multiple factors (interests, skills, location, etc.)
   - Add user behavior analysis (previous applications, views, etc.)
   - Consider opportunity popularity and success rates

4. **Score Normalization**: Add proper percentage calculation
   - Implement min-max normalization to convert raw scores to 0-100% range
   - Handle edge cases (no matches = 0%, perfect match = 100%)
   - Filter out ineligible opportunities instead of showing negative percentages

5. **Performance Monitoring**: Add metrics to track improvements
   - Implement query performance logging
   - Add cache hit/miss rate monitoring
   - Track page load times and user engagement metrics

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the performance and accuracy issues on unfixed code, then verify the fix works correctly and preserves existing functionality.

### Exploratory Fault Condition Checking

**Goal**: Surface counterexamples that demonstrate the bugs BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write tests that simulate For You section loading and match percentage calculation. Run these tests on the UNFIXED code to observe failures and understand the root cause.

**Test Cases**:
1. **Performance Test**: Load For You section with large dataset (will be slow on unfixed code)
2. **Caching Test**: Enable Redis and verify cache usage (will fail to use cache on unfixed code)
3. **Match Percentage Test**: Calculate scores for various user profiles (will show negative/unnormalized values on unfixed code)
4. **Edge Case Test**: Test with users having no interests or no matching opportunities (may crash or show invalid percentages on unfixed code)

**Expected Counterexamples**:
- Page load times exceed 3+ seconds with moderate data volumes
- Database queries are made even when Redis cache contains valid data
- Match percentages show negative values or scores above 100%
- Possible causes: inefficient queries, broken cache logic, missing normalization

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL input WHERE isBugCondition(input) DO
  result := forYouSection_fixed(input)
  ASSERT efficientLoading(result) AND accuratePercentages(result)
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL input WHERE NOT isBugCondition(input) DO
  ASSERT discoverPage_original(input) = discoverPage_fixed(input)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-For You interactions

**Test Plan**: Observe behavior on UNFIXED code first for other discover page sections and interactions, then write property-based tests capturing that behavior.

**Test Cases**:
1. **Other Sections Preservation**: Verify trending, recent, and category sections continue to work correctly
2. **Opportunity Card Preservation**: Verify clicking and interacting with opportunity cards works the same
3. **Navigation Preservation**: Verify page routing and navigation remains unchanged
4. **Empty State Preservation**: Verify empty state handling continues to work for users with no matches

### Unit Tests

- Test database query optimization with various user profiles and data volumes
- Test Redis caching implementation with cache hits, misses, and invalidation scenarios
- Test scoring algorithm with different user-opportunity combinations
- Test score normalization with edge cases (no matches, perfect matches, negative raw scores)

### Property-Based Tests

- Generate random user profiles and verify efficient loading across many scenarios
- Generate random opportunity datasets and verify match percentages are always 0-100%
- Test that all non-For You interactions continue to work across many user states and page configurations

### Integration Tests

- Test full discover page flow with For You section loading efficiently
- Test caching behavior across multiple page loads and user sessions
- Test that visual feedback and user experience improvements are evident
- Test performance under realistic load conditions with proper monitoring