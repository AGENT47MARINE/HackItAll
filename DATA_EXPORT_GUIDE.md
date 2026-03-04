# Data Export Guide

## Overview

The Opportunity Access Platform provides a comprehensive data export feature that allows users to download all their personal data in JSON format. This feature ensures compliance with GDPR (Article 20 - Right to data portability) and CCPA data access requirements.

## Endpoint

```
GET /api/export
```

**Authentication**: Required (Bearer token)

## What Data is Exported

The export includes all data associated with a user account:

### 1. Export Metadata
- Export date and time
- User ID
- Data format version

### 2. Account Information
- Email address
- Phone number (if provided)
- Account creation date
- Last updated date

### 3. Profile Data
- Interests (list)
- Skills (list)
- Education level
- Notification preferences (email/SMS)
- Low bandwidth mode setting
- Profile last updated date

### 4. Tracked Opportunities
- Count of tracked opportunities
- For each tracked opportunity:
  - Opportunity ID
  - Opportunity title
  - Opportunity type
  - Deadline
  - Date saved
  - Expiration status

### 5. Participation History
- Count of participation entries
- For each participation:
  - Participation ID
  - Opportunity ID
  - Opportunity title
  - Opportunity type
  - Status (applied, accepted, rejected, completed)
  - Personal notes
  - Date created

## Usage

### Using cURL

```bash
curl -X GET http://localhost:8000/api/export \
  -H "Authorization: Bearer YOUR_CLERK_TOKEN" \
  -o my_data_export.json
```

### Using JavaScript/Fetch

```javascript
const response = await fetch('http://localhost:8000/api/export', {
  headers: {
    'Authorization': `Bearer ${clerkToken}`
  }
});

const exportData = await response.json();
console.log(exportData);

// Save to file
const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = `my_data_export_${new Date().toISOString()}.json`;
a.click();
```

### Using Python

```python
import requests
import json

response = requests.get(
    'http://localhost:8000/api/export',
    headers={'Authorization': f'Bearer {clerk_token}'}
)

if response.status_code == 200:
    export_data = response.json()
    
    # Save to file
    with open('my_data_export.json', 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print("Data exported successfully!")
else:
    print(f"Error: {response.status_code}")
```

## Example Export

```json
{
  "export_metadata": {
    "export_date": "2024-03-15T14:30:00.000000",
    "user_id": "user_2abc123xyz",
    "data_format_version": "1.0"
  },
  "account_information": {
    "email": "student@example.com",
    "phone": "+1234567890",
    "account_created": "2024-01-15T10:00:00.000000",
    "last_updated": "2024-03-10T15:30:00.000000"
  },
  "profile": {
    "interests": ["AI", "Machine Learning", "Web Development"],
    "skills": ["Python", "JavaScript", "React"],
    "education_level": "undergraduate",
    "notification_preferences": {
      "email": true,
      "sms": false
    },
    "low_bandwidth_mode": false,
    "profile_updated": "2024-03-10T15:30:00.000000"
  },
  "tracked_opportunities": {
    "count": 2,
    "opportunities": [
      {
        "opportunity_id": "opp_123",
        "opportunity_title": "AI Hackathon 2024",
        "opportunity_type": "hackathon",
        "opportunity_deadline": "2024-04-30T23:59:59",
        "saved_at": "2024-03-01T12:00:00",
        "is_expired": false
      },
      {
        "opportunity_id": "opp_456",
        "opportunity_title": "Tech Scholarship",
        "opportunity_type": "scholarship",
        "opportunity_deadline": "2024-05-15T23:59:59",
        "saved_at": "2024-03-05T14:30:00",
        "is_expired": false
      }
    ]
  },
  "participation_history": {
    "count": 1,
    "entries": [
      {
        "participation_id": "part_789",
        "opportunity_id": "opp_100",
        "opportunity_title": "Winter Hackathon 2024",
        "opportunity_type": "hackathon",
        "status": "completed",
        "notes": "Won 2nd place! Great experience.",
        "created_at": "2024-02-01T10:00:00"
      }
    ]
  }
}
```

## Response Codes

- `200 OK` - Export successful, data returned
- `401 Unauthorized` - Not authenticated or invalid token
- `404 Not Found` - User data not found

## Use Cases

### 1. Personal Backup
Users can periodically download their data for personal records:
```bash
# Create a backup
curl -X GET http://localhost:8000/api/export \
  -H "Authorization: Bearer $TOKEN" \
  -o backup_$(date +%Y%m%d).json
```

### 2. Account Migration
Users can export their data to move to another platform:
```javascript
// Export and prepare for migration
const data = await exportUserData();
const migrationPackage = {
  source: 'opportunity-access-platform',
  version: data.export_metadata.data_format_version,
  data: data
};
```

### 3. GDPR Compliance
Respond to user data access requests:
```python
# Generate export for GDPR request
export_data = get_user_export(user_id)
send_email_with_attachment(
    to=user_email,
    subject="Your Data Export Request",
    attachment=export_data
)
```

### 4. Portfolio Building
Users can extract their participation history for resumes:
```javascript
const export_data = await fetch('/api/export', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

const achievements = export_data.participation_history.entries
  .filter(e => e.status === 'completed')
  .map(e => ({
    title: e.opportunity_title,
    type: e.opportunity_type,
    notes: e.notes
  }));

console.log('Achievements:', achievements);
```

## Privacy and Security

### Data Protection
- Export requires authentication - users can only export their own data
- No password hashes are included in the export
- Export is generated on-demand (not stored)
- All dates are in ISO 8601 format (UTC)

### What's NOT Included
- Password hashes (security)
- Internal system IDs (except user-facing IDs)
- Audit logs (system data, not user data)
- Other users' data (privacy)

## Legal Compliance

### GDPR (EU)
✅ **Article 20 - Right to data portability**: Users can receive their personal data in a structured, commonly used, and machine-readable format (JSON).

✅ **Article 15 - Right of access**: Users can obtain confirmation of data processing and access to their personal data.

### CCPA (California)
✅ **Right to Know**: Consumers have the right to request disclosure of personal information collected.

✅ **Data Portability**: Data is provided in a portable format.

### Best Practices
- Respond to export requests within 30 days (GDPR requirement)
- Provide data in a commonly used format (JSON ✓)
- Include all personal data categories
- Make the export easily accessible to users

## Troubleshooting

### Empty Export
**Problem**: Export returns minimal data

**Solution**: User may be new with no activity. This is normal - the export will show:
- Account information
- Profile data
- Empty tracked opportunities (count: 0)
- Empty participation history (count: 0)

### Large Export
**Problem**: Export is very large for users with lots of data

**Solution**: The export is generated on-demand and streamed. For very large exports:
- Consider pagination (future enhancement)
- Compress the JSON (gzip)
- Provide download link instead of direct response

### Missing Data
**Problem**: Some expected data is not in the export

**Solution**: Verify:
1. User is authenticated correctly
2. Data exists in the database
3. Database relationships are correct
4. Check server logs for errors

## Future Enhancements

Potential improvements:
- [ ] Export in multiple formats (CSV, XML, PDF)
- [ ] Scheduled automatic exports
- [ ] Export history/versioning
- [ ] Selective export (choose what to include)
- [ ] Compressed exports for large datasets
- [ ] Email delivery of exports
- [ ] Export encryption option

## Testing

### Manual Test
```bash
# 1. Authenticate and get token
TOKEN="your_clerk_token_here"

# 2. Export data
curl -X GET http://localhost:8000/api/export \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'

# 3. Verify all sections are present
curl -X GET http://localhost:8000/api/export \
  -H "Authorization: Bearer $TOKEN" \
  | jq 'keys'

# Expected output:
# [
#   "account_information",
#   "export_metadata",
#   "participation_history",
#   "profile",
#   "tracked_opportunities"
# ]
```

### Automated Test
```python
def test_data_export():
    # Create test user with data
    user = create_test_user()
    track_opportunity(user.id, opp_id)
    add_participation(user.id, opp_id, "completed")
    
    # Export data
    response = client.get(
        "/api/export",
        headers={"Authorization": f"Bearer {user.token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure
    assert "export_metadata" in data
    assert "account_information" in data
    assert "profile" in data
    assert "tracked_opportunities" in data
    assert "participation_history" in data
    
    # Verify content
    assert data["account_information"]["email"] == user.email
    assert data["tracked_opportunities"]["count"] == 1
    assert data["participation_history"]["count"] == 1
```

## Support

For questions or issues with data export:
1. Check this documentation
2. Verify authentication is working
3. Check server logs for errors
4. Contact support with your user ID (not included in logs for privacy)
