# AI Response Format Documentation

## Overview
The `/Calculate` endpoint uses Gemini AI to analyze agricultural data and provide recommendations. The AI response has been updated with specific formatting requirements.

## Updated JSON Response Format

```json
{
    "temperatura_suelo": "75.2",
    "demanda_producto": "High",
    "probabilidad_lluvia": "20",
    "efectividad_cultivo": "80"
}
```

## Field Specifications

### 1. `temperatura_suelo` (Soil Temperature)
- **Format**: Numeric value in Fahrenheit (°F)
- **Example**: `"75.2"`, `"68.5"`, `"82.0"`
- **Display**: Shows in input field with label "Temperature (F°)"
- **Rules**: Must be in Fahrenheit, not Celsius

### 2. `demanda_producto` (Product Demand)
- **Format**: Single word ONLY
- **Allowed Values**: `"High"`, `"Medium"`, `"Low"`
- **Example**: `"High"` ✅ | `"High, market is growing"` ❌
- **Display**: Shows in input field with label "Product Demand"
- **Rules**: No additional text or context allowed

### 3. `probabilidad_lluvia` (Rain Probability)
- **Format**: Numeric percentage value WITHOUT % symbol
- **Example**: `"20"`, `"45"`, `"80"`
- **Display**: JavaScript adds "%" symbol automatically → displays as "20%"
- **Rules**: Number only, JavaScript handles the % symbol

### 4. `efectividad_cultivo` (Crop Effectiveness) - NEW ✨
- **Format**: Numeric percentage value (0-100) WITHOUT % symbol
- **Example**: `"80"`, `"65"`, `"92"`
- **Display**: JavaScript adds "%" symbol → displays as "80%" in large heading
- **Calculation Factors**:
  - Soil conditions (temperature, type)
  - Plant type suitability
  - Location and climate
  - Field measurements (pH, conductivity, salinity, moisture)
  - Weather forecast
  - Market demand

## AI Prompt Instructions

The AI receives the following data to make its analysis:

### Main Variables (from `main-variables` collection)
- Width (meters)
- Length (meters)
- Plant type
- Location (latitude, longitude)

### Field Measurements (from `field-data` collection)
- Water pH
- Water Conductivity
- Soil Salinity
- Soil Moisture

### Internet Search Results
- Soil temperature for location
- Market demand for crop type
- Weather forecast for location

### Satellite Map
- Screenshot from CropSmart map for the specified coordinates

## System Prompt

```
You are an agriculture expert. Analyze the provided information and respond ONLY with a valid JSON:

{
    "temperatura_suelo": "<numeric value in °F (Fahrenheit)>",
    "demanda_producto": "<ONLY one word: High, Medium, or Low>",
    "probabilidad_lluvia": "<numeric percentage value without % symbol, e.g., 20, 45, 80>",
    "efectividad_cultivo": "<numeric percentage (0-100) representing crop effectiveness based on all conditions>"
}

RULES:
- Only return the JSON, nothing else
- temperatura_suelo must be in Fahrenheit (°F)
- demanda_producto must be EXACTLY one of these words: High, Medium, Low (no additional text)
- probabilidad_lluvia must be a number only (e.g., 20, not "20%")
- efectividad_cultivo should consider soil conditions, plant type, location, field measurements, and climate
- If info is missing, make a reasonable estimate based on available context
```

## Frontend Display

### Temperature
```javascript
$('#txt_temperatura_suelo').val(resp.temperatura_suelo);
// Displays: "75.2" in input field
```

### Product Demand
```javascript
$('#txt_demanda_producto').val(resp.demanda_producto);
// Displays: "High" in input field
```

### Rain Probability
```javascript
$('#txt_probabilidad_lluvia').val(resp.probabilidad_lluvia + '%');
// Displays: "20%" in input field
```

### Crop Effectiveness
```javascript
$('.porcentaje_efectividad').text(resp.efectividad_cultivo + '%');
// Displays: "80%" in large heading
```

## Error Handling

### Default Values on Error
```javascript
{
    "temperatura_suelo": "Not available",
    "demanda_producto": "Medium",
    "probabilidad_lluvia": "Not available",
    "efectividad_cultivo": "Not available"
}
```

## Example Full Response

### Input Data:
- Width: 50m, Length: 30m
- Plant: Tomato
- Location: 18.7357, -70.1627
- Water pH: 6.5
- Soil Moisture: 45%

### AI Response:
```json
{
    "temperatura_suelo": "78.5",
    "demanda_producto": "High",
    "probabilidad_lluvia": "35",
    "efectividad_cultivo": "85"
}
```

### Display Result:
- Temperature (F°): `78.5`
- Product Demand: `High`
- Rain Probability: `35%`
- Crop Effectiveness: `85%`
