# Database Implementation Summary

## Overview
The application now uses MongoDB collections to store data instead of cookies. Each collection maintains only ONE document that gets updated (upsert pattern).

## Collections Created

### 1. `main-variables`
**Purpose**: Stores the main field configuration data
**Fields**:
- `width` (float): Field width in meters
- `length` (float): Field length in meters
- `plant_type` (string): Type of plant (tomate, maiz, lechuga)
- `latitude` (float): Geographic latitude
- `longitude` (float): Geographic longitude
- `updated_at` (datetime): Last update timestamp

**Endpoints**:
- `POST /SaveMainVariables` - Save/update main variables
- `GET /GetMainVariables` - Retrieve main variables

### 2. `field-data`
**Purpose**: Stores field measurement data
**Fields**:
- `water_ph` (float): Water pH level
- `water_conductivity` (float): Water conductivity measurement
- `soil_salinity` (float): Soil salinity level
- `soil_moisture` (float): Soil moisture percentage
- `updated_at` (datetime): Last update timestamp

**Endpoints**:
- `POST /SaveFieldData` - Save/update field data
- `GET /GetFieldData` - Retrieve field data

## How It Works

### Main Variables Flow:
1. User fills form in `/VariablesDeInicio` page
2. On submit, data is sent to `/SaveMainVariables` endpoint
3. Backend updates/inserts the single document in `main-variables` collection
4. User is redirected to `/Principal` page
5. Principal page loads data from database using `/GetMainVariables`
6. If no data exists, user is redirected back to `/VariablesDeInicio`

### Field Data Flow:
1. User navigates to `/DatosDeCampo` page
2. Page loads existing field data from database (if any)
3. User fills/updates measurement values
4. On save, data is sent to `/SaveFieldData` endpoint
5. Backend updates/inserts the single document in `field-data` collection
6. User is redirected to `/Principal` page

## Key Changes

### Backend (Python):
- **conexion.py**: Added `main_variables_col` and `field_data_col` collections
- **routes/VariablesDeInicio.py**: 
  - Created `save_main_variables()` endpoint
  - Created `get_main_variables()` endpoint
- **routes/DatosDeCampo.py**: 
  - Created `save_field_data()` endpoint
  - Created `get_field_data()` endpoint

### Frontend (JavaScript):
- **VariablesDeInicio.html**: 
  - Removed cookie-based storage
  - Added AJAX call to save data to database
- **VariablesDeInicio.js**: 
  - Added `loadMainVariables()` function to load existing data
- **Principal.js**: 
  - Removed cookie reading functions
  - Added `loadMainVariables()` to fetch from database
  - Added redirect to `/VariablesDeInicio` if no data exists
- **DatosDeCampo.js**: 
  - Added `loadFieldData()` to load existing measurements
  - Added `saveFieldData()` to save measurements to database

## Benefits
1. **Persistence**: Data survives browser sessions and cookie clearing
2. **Server-side**: Data is accessible from any client
3. **Single Source of Truth**: Only one record per collection
4. **Easy Updates**: Automatic upsert pattern ensures data stays current
5. **Scalability**: Ready for multi-user scenarios (can add user filtering later)

## Data Loading Strategy

### Server-Side Rendering (SSR)
All data is now loaded from the database when the page is rendered on the backend:

**VariablesDeInicio page:**
- Backend fetches data from `main-variables` collection
- Passes `main_data` to template
- HTML inputs are pre-filled with values using Jinja2: `value="{{ main_data.width or '' }}"`

**DatosDeCampo page:**
- Backend fetches data from `field-data` collection
- Passes `field_data` to template
- HTML inputs are pre-filled with values

**Principal page:**
- Backend fetches both `main-variables` and `field-data`
- If no main variables exist, redirects to `/VariablesDeInicio`
- Passes both `main_data` and `field_data` to template

### Benefits of SSR Approach
1. **Faster Initial Load**: No additional AJAX calls needed
2. **SEO Friendly**: Data is in HTML source
3. **No Flash of Empty Content**: Fields are populated immediately
4. **Simpler JavaScript**: Less client-side logic
5. **Better UX**: No loading states needed

## Testing Checklist
- [ ] Save main variables from `/VariablesDeInicio`
- [ ] Verify data persists and pre-fills form after page refresh
- [ ] Check that `/Principal` loads the saved data
- [ ] Verify redirect to `/VariablesDeInicio` if no main data exists
- [ ] Update main variables and verify changes persist and pre-fill
- [ ] Save field data from `/DatosDeCampo`
- [ ] Verify field data pre-fills on return visit
- [ ] Test with empty database (fresh start)
