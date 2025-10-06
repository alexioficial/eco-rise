# Cache System Documentation

## Overview
The application now implements a smart caching system to avoid unnecessary AI calculations and internet searches when the same parameters are used.

## Collection: `data`

### Purpose
Stores calculated results indexed by input parameters to enable fast retrieval without recalculating.

### Document Structure

```json
{
  "cache_key": "5f4dcc3b5aa765d61d8327deb882cf99",
  "input_params": {
    "width": 50.0,
    "length": 30.0,
    "plant_type": "tomate",
    "latitude": 18.7357,
    "longitude": -70.1627,
    "water_ph": 6.5,
    "water_conductivity": 1.5,
    "soil_salinity": 0.8,
    "soil_moisture": 45.0
  },
  "calculated_at": "2025-10-05T23:30:00.000Z",
  "url_mapa": "static/imgs/data/m_18.7357_-70.1627.png",
  "temperatura_suelo": "78.5",
  "demanda_producto": "High",
  "probabilidad_lluvia": "35",
  "efectividad_cultivo": "85",
  "advice": "Your 85% crop effectiveness is excellent, driven by optimal soil moisture...",
  "advice_generated_at": "2025-10-05T23:46:55.000Z"
}
```

## Cache Key Generation

### Algorithm
The cache key is an MD5 hash of all input parameters that affect the calculation:

```python
cache_key_data = {
    "width": main_data.get("width"),
    "length": main_data.get("length"),
    "plant_type": main_data.get("plant_type"),
    "latitude": main_data.get("latitude"),
    "longitude": main_data.get("longitude"),
    "water_ph": field_data.get("water_ph"),
    "water_conductivity": field_data.get("water_conductivity"),
    "soil_salinity": field_data.get("soil_salinity"),
    "soil_moisture": field_data.get("soil_moisture"),
}
cache_key = hashlib.md5(
    json.dumps(cache_key_data, sort_keys=True).encode()
).hexdigest()
```

### Why MD5?
- Fast generation
- Unique per parameter combination
- Fixed length (32 characters)
- No collisions for our use case

## How It Works

### Flow Diagram

```
┌─────────────────────────────────────────┐
│  User loads /Principal page             │
│  JavaScript calls Calculate()           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Backend: Load main_data + field_data   │
│  from database                           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Generate cache_key from all params     │
└──────────────┬──────────────────────────┘
               │
               ▼
         ┌─────┴─────┐
         │ Check     │
         │ Cache     │
         └─────┬─────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
   ┌────────┐   ┌─────────┐
   │ FOUND  │   │  MISS   │
   └────┬───┘   └────┬────┘
        │            │
        │            ▼
        │      ┌──────────────────────────┐
        │      │ • Take screenshot        │
        │      │ • Search internet (3x)   │
        │      │ • Call Gemini AI         │
        │      │ • Parse JSON response    │
        │      └──────┬───────────────────┘
        │             │
        │             ▼
        │      ┌──────────────────────────┐
        │      │ Save results to cache    │
        │      └──────┬───────────────────┘
        │             │
        └─────┬───────┘
              │
              ▼
      ┌────────────────┐
      │ Return results │
      │ to frontend    │
      └────────────────┘
```

## Cache Hit vs Cache Miss

### Cache HIT (Fast Response ~50ms)
When parameters match an existing calculation:
1. ✅ Load from database
2. ✅ Return immediately
3. ✅ No internet searches
4. ✅ No AI calls
5. ✅ No screenshot needed
6. Response includes `from_cache: true`

**Console Output:**
```
Cache HIT for key: 5f4dcc3b5aa765d61d8327deb882cf99
```

### Cache MISS (Slow Response ~15-30 seconds)
When parameters are new or changed:
1. ⏳ Take satellite map screenshot
2. ⏳ Search internet for soil temperature
3. ⏳ Search internet for market demand
4. ⏳ Search internet for weather forecast
5. ⏳ Send all data to Gemini AI
6. ⏳ Parse AI response
7. ✅ Save to cache
8. ✅ Return results

**Console Output:**
```
Cache MISS for key: 5f4dcc3b5aa765d61d8327deb882cf99. Calculating...
Saved calculation to cache with key: 5f4dcc3b5aa765d61d8327deb882cf99
```

## When Cache is Invalidated

The cache is specific to the exact combination of:

### Main Variables
- Width changes
- Length changes
- Plant type changes
- Latitude changes
- Longitude changes

### Field Data
- Water pH changes
- Water conductivity changes
- Soil salinity changes
- Soil moisture changes

**Any change to ANY parameter = New cache key = Cache MISS = Recalculation**

## Benefits

### 1. Performance
- **First calculation**: ~20 seconds
- **Subsequent calculations**: ~50ms
- **Speed improvement**: 400x faster

### 2. Cost Savings
- Reduces Gemini AI API calls
- Reduces internet search API calls
- Reduces server processing time

### 3. Consistency
- Same inputs always return same outputs
- Results are reproducible
- Historical data preserved

### 4. User Experience
- Instant results for repeated scenarios
- No waiting for recalculation
- Smooth navigation

## Database Indexes

For optimal performance, create indexes on:

```javascript
// MongoDB Shell
db.data.createIndex({ "cache_key": 1 }, { unique: true })
db.data.createIndex({ "calculated_at": 1 })
db.data.createIndex({ "input_params.latitude": 1, "input_params.longitude": 1 })
db.data.createIndex({ "input_params.plant_type": 1 })
```

## Future Enhancements

### Planned (Date field will be used for this)
- **Time-based cache expiration**: Weather and market data become stale
- **Historical comparisons**: Compare results over time
- **Trend analysis**: Track how conditions change
- **Seasonal adjustments**: Different recommendations per season

### Potential Features
- Manual cache invalidation per user
- Cache statistics dashboard
- Most common parameter combinations
- Cache warming for popular scenarios

## Cache Invalidation Strategy

Currently: **Never expires** (permanent cache)

Future considerations:
- Weather data: Expire after 24 hours
- Market data: Expire after 7 days
- Soil temperature: Expire after 1 day
- Location/plant data: Never expire (static)

## Testing the Cache

### Test 1: Cache MISS
1. Go to `/VariablesDeInicio`
2. Enter width: 50, length: 30, plant: tomate
3. Save and go to `/Principal`
4. Wait ~20 seconds for calculation
5. Check console: "Cache MISS"

### Test 2: Cache HIT
1. Refresh `/Principal` page
2. Wait ~50ms for instant results
3. Check console: "Cache HIT"

### Test 3: Cache MISS (Changed Parameter)
1. Go to `/VariablesDeInicio`
2. Change width to 60 (everything else same)
3. Save and go to `/Principal`
4. Wait ~20 seconds for new calculation
5. Check console: "Cache MISS" (new cache key generated)

## Monitoring

Check cache effectiveness with:

```javascript
// MongoDB Shell - Total cached calculations
db.data.count()

// Recent calculations
db.data.find().sort({calculated_at: -1}).limit(10)

// Find calculations for specific location
db.data.find({
  "input_params.latitude": 18.7357,
  "input_params.longitude": -70.1627
})
```

## Summary

The cache system dramatically improves performance by storing calculated results indexed by input parameters. Users experience instant results when revisiting scenarios, while new or modified parameters trigger fresh calculations that are then cached for future use.
