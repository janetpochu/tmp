# Step 1: Create Field Mapping Matrix

## Objective
Create a comprehensive mapping between Mobile UI requirements, PAPI responses, and EAPI design.

## Input Files Required
- `mobile_spec.json` - Mobile UI field requirements
- `papi_spec.json` - PAPI request/response specifications

## Task Instructions

### 1.1 Extract Mobile Required Fields
```
Read mobile_spec.json and extract:
- All field names marked as required
- Field data types
- Field descriptions
- UI component using each field

Output format: JSON array
[
  {
    "mobile_field_name": "userName",
    "data_type": "string",
    "required": true,
    "used_in_screen": "ProfileScreen"
  }
]

Save as: mobile_fields_extracted.json
```

### 1.2 Extract PAPI Available Fields
```
Read papi_spec.json and extract:
- All response field names from each endpoint
- Field data types
- Endpoint providing each field
- Sample values if available

Output format: JSON array
[
  {
    "papi_field_name": "user_name",
    "data_type": "string",
    "endpoint": "GET /api/user/profile",
    "sample_value": "john_doe"
  }
]

Save as: papi_fields_extracted.json
```

### 1.3 Create Mapping Matrix
```
Compare mobile_fields_extracted.json with papi_fields_extracted.json

For each mobile field, determine:
1. DIRECT_MATCH: Exact field exists in PAPI (same name/similar name)
2. TRANSFORM_NEEDED: Field exists but needs transformation
3. AGGREGATE_NEEDED: Multiple PAPI fields needed
4. MISSING: Field not available in PAPI
5. MULTIPLE_CALLS: Requires data from multiple PAPI endpoints

Output format: CSV with columns:
mobile_field | papi_source | mapping_type | transformation_notes | papi_endpoint

Save as: field_mapping_matrix.csv
```

## Validation Checklist
- [ ] All mobile required fields are listed
- [ ] Each field has a mapping status
- [ ] Missing fields are clearly identified
- [ ] Transformation logic is noted

## Expected Output Files
1. mobile_fields_extracted.json
2. papi_fields_extracted.json
3. field_mapping_matrix.csv
