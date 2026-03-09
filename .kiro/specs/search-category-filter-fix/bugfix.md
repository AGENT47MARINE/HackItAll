# Bugfix Requirements Document

## Introduction

The search page category filter buttons (hackathon, scholarship, internship, skill program) are not filtering the displayed opportunities correctly. When a user clicks on a specific category button, the page continues to show all opportunities from all categories instead of filtering to show only the selected category. This bug affects the core search functionality and prevents users from efficiently browsing opportunities by category.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN a user clicks the "hackathon" category filter button THEN the system displays all opportunities from all categories instead of only hackathons

1.2 WHEN a user clicks the "scholarship" category filter button THEN the system displays all opportunities from all categories instead of only scholarships

1.3 WHEN a user clicks the "internship" category filter button THEN the system displays all opportunities from all categories instead of only internships

1.4 WHEN a user clicks the "skill_program" category filter button THEN the system displays all opportunities from all categories instead of only skill programs

1.5 WHEN a user clicks any category filter button THEN the system does not trigger a search request with the selected category type parameter

### Expected Behavior (Correct)

2.1 WHEN a user clicks the "hackathon" category filter button THEN the system SHALL display only opportunities with type "hackathon"

2.2 WHEN a user clicks the "scholarship" category filter button THEN the system SHALL display only opportunities with type "scholarship"

2.3 WHEN a user clicks the "internship" category filter button THEN the system SHALL display only opportunities with type "internship"

2.4 WHEN a user clicks the "skill_program" category filter button THEN the system SHALL display only opportunities with type "skill_program"

2.5 WHEN a user clicks any category filter button THEN the system SHALL immediately trigger a search request with the selected category type parameter

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a user clicks the "All" filter button THEN the system SHALL CONTINUE TO display opportunities from all categories

3.2 WHEN a user enters a search query in the search input field THEN the system SHALL CONTINUE TO filter opportunities by the search term

3.3 WHEN a user toggles AI Mode on and enters a search query THEN the system SHALL CONTINUE TO perform semantic search

3.4 WHEN a user clicks the Search button THEN the system SHALL CONTINUE TO execute the search with current filters

3.5 WHEN opportunities are displayed THEN the system SHALL CONTINUE TO show the correct count of filtered results

3.6 WHEN a user combines a search query with a category filter THEN the system SHALL CONTINUE TO apply both filters together
