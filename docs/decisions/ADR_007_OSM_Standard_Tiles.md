---
icon: simple/openstreetmap
---

# ADR 007: Choosing OpenStreetMap Standard Raster Tile Provider

**Date:** 2026-03-25  
**Context:** Mapping and Geospatial Services  

---

## 1. Context

Our project requires a reliable raster tile provider for rendering OpenStreetMap data on interactive maps. Having chosen OpenStreetMap as the data source (ADR-006), we now need to select which tile server to use. The key requirements include:

- Standard OSM Carto styling matching openstreetmap.org
- No API key requirements
- No usage-based billing
- Global coverage with consistent quality
- Support for standard {z}/{x}/{y} tile coordinates

We evaluated several raster tile providers based on OpenStreetMap data.

---

## 2. Decision

We decided to use the **OpenStreetMap Standard tile layer** (`https://tile.openstreetmap.org/{z}/{x}/{y}.png`) as our primary raster tile provider.

---

## 3. Rationale

### Benefits of using OpenStreetMap Standard:

- **Official Standard Layer**:
	- Matches the openstreetmap.org front page appearance
	- Most widely recognized OSM visual style
	- Consistent with user expectations
- **Free and Open**:
	- No API key required
	- Free for use following the [OSM tile usage policy](https://operations.osmfoundation.org/policies/tiles/)
	- Funded by donations, no commercial interests
- **Global Coverage**:
	- Same comprehensive global coverage as OSM data itself
	- Consistent quality across all regions
	- Regular updates with OSM data changes
- **Technical Reliability**:
	- CDN-backed infrastructure with multiple subdomains (a, b, c)
	- IPv6 support enabled
	- Well-documented and stable API
- **No Vendor Lock-in**:
	- Multiple fallback tile servers available
	- Easy to switch providers if needed

### Alternatives considered:

| Option | Pros | Cons |
|--------|------|------|
| OpenStreetMap.de | German/local language labels, free | Restricted commercial use, German-focused styling |
| OpenStreetMap.fr | French labels, some enhanced features, HTTPS/HTTP2 | French-focused labels may not suit all use cases |
| Humanitarian (HOT) | High contrast, disaster relief focused | Different visual style, not standard appearance |
| CyclOSM | Cycling-focused, bicycle routes highlighted | Not general-purpose, specialized styling |
| Carto (Positron/Dark Matter) | Clean minimal design, dark mode option | Commercial service, requires attribution, registration |
| MapTiler | Multiple styles, professional quality | Commercial pricing, requires API key registration |
| Stadia Maps (Alidade Smooth) | Modern styling, free tier available | Commercial service, no registration required for dev |

The **German** and **French** variants were not chosen as they localize labels to specific languages, which may not match user expectations for a general-purpose application.

**Carto**, **MapTiler**, and **Stadia Maps** are commercial services that, while offering quality tiles, introduce vendor dependencies and potential costs at scale.

The **Humanitarian** style and **CyclOSM** have specialized visual designs better suited for specific use cases rather than general mapping.

OpenStreetMap Standard provides the familiar, neutral appearance that best serves our application's general-purpose mapping needs.

---

## 4. Consequences

### Positive Outcomes

- Consistent map appearance matching the OSM website users know
- No API costs or registration requirements
- Full compliance with OSM licensing (attribution required)
- Easy integration with Leaflet, MapLibre, and OpenLayers
- Multiple fallback options if the standard server is unavailable

### Tradeoffs and Considerations

- Fair usage policy limits apply (see [OSM Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/))
- High-traffic applications may need to run their own tile server
- Update latency varies (1 minute to 1 day depending on zoom level)
- Limited customization compared to commercial alternatives
- Must display proper OSM attribution on maps

---

## 5. Extending to Dark Theme

### 5.1 Context

Our application requires both light and dark theme map options to match user interface preferences. The dark theme is particularly important for:
- Night-time usage
- Reducing eye strain in low-light environments
- Aesthetic consistency with dark-mode UI designs

### 5.2 Decision

We decided to use **CartoDB Dark Matter** (`https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png`) as our dark theme tile provider.

### 5.3 Rationale

- **High-Quality Dark Design**:
  - Clean, minimal dark basemap with excellent contrast
  - Subtle colors optimized for dark backgrounds
  - Well-balanced label readability on dark tiles
- **No Authentication Required**:
  - Free to use with attribution
  - No API key or registration needed
  - Same free tier as standard Carto tiles
- **Consistent API Structure**:
  - Same {z}/{x}/{y} coordinate format as standard tiles
  - Easy to swap between light and dark themes in code
  - Both use HTTPS endpoints
- **Technical Reliability**:
  - CDN-backed with global distribution
  - Stable, well-maintained service
  - Regular updates matching OSM data

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| Stadia Maps Alidade Smooth Dark | Modern styling, free tier available | Commercial service, requires attribution |
| MapTiler Dark | Professional quality, multiple styles | Commercial pricing, requires API key |
| OSM Bright (self-hosted) | Full control, customizable | Requires self-hosting infrastructure |
| Humanitarian Dark | High contrast | Not a standard dark theme option |

**Stadia Maps** was considered but requires commercial terms and attribution that differs from our preference for more permissive usage.

**MapTiler** offers excellent dark styles but requires API key registration and has usage-based pricing at scale.

The **CartoDB Dark Matter** layer provides the best balance of quality, accessibility, and ease of integration for our dark theme needs.

### 5.4 Consequences

### Positive Outcomes
- Dark theme available for night-time and low-light usage
- Maintains consistent tile API format across themes
- No additional costs or registration requirements
- Easy to implement theme switching in the UI

### Tradeoffs and Considerations
- CartoDB is a commercial service (recently acquired by MapTiler); terms may change
- Attribution required: "© OpenStreetMap contributors © CARTO"
- Dark theme has slightly different coverage than standard OSM (same data source)
- Consider implementing theme detection based on system preferences

---

## 6. References

- [OSM Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/)
- [OpenStreetMap Standard Tile Layer](https://wiki.openstreetmap.org/wiki/Standard_tile_layer)
- [OpenStreetMap Carto](https://github.com/gravitystorm/openstreetmap-carto/) (rendering style source code)
- [Leaflet Documentation](https://leafletjs.com/) (our map library)
- [CartoDB Dark Matter](https://carto.com/basemaps/) (dark theme tiles)
