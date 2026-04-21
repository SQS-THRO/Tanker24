---
icon: simple/openstreetmap
---

# ADR 006: Choosing OpenStreetMap as Map Tiles Provider

**Date:** 2026-03-25  
**Context:** Mapping and Geospatial Services  
**Status:** Currently accepted

---

## 1. Context

Our project requires a reliable map tiles provider for displaying geospatial data. The key requirements include:

- Map tiles API for rendering interactive maps
- Global coverage with good detail
- Cost-effective solution with no vendor lock-in
- Customization options for map styling
- No API key requirements or usage-based billing

We evaluated several map providers to determine the best fit for our requirements.

---

## 2. Decision

We decided to adopt **OpenStreetMap** as the primary map tiles provider for our application.

---

## 3. Rationale

### Benefits of using OpenStreetMap:

- **Cost-Effective**:
	- Free to use with no API key requirements
	- No usage-based billing or rate limits on public instances
	- Multiple public tile servers available
- **Open Source & Community-Driven**:
	- Community-contributed data with extensive global coverage
	- Transparent data sources and methodology
	- Continuous improvement by thousands of contributors
- **Customization**:
	- Multiple render styles and themes available
	- Ability to host custom tile servers if needed
	- Full control over map appearance and data
- **Privacy-Friendly**:
	- No tracking or data collection requirements
	- No vendor dependency for core functionality
- **Good Technical Integration**:
	- Standardized tile API compatible with Leaflet, MapLibre, OpenLayers
	- Multiple public tile providers as fallbacks
	- WMS support for advanced use cases

### Alternatives considered:

| Option | Pros | Cons |
|--------|------|------|
| Google Maps | High-quality tiles, extensive APIs, global coverage | Requires API key with credit card, usage-based pricing, restrictive ToS |
| Apple Maps | Good quality, native iOS integration | Limited API access, primarily Apple ecosystem focused |
| Yandex Maps | Strong in Russia and CIS countries, good APIs | Weak coverage outside primary regions, Russian data sovereignty concerns |
| Bing Maps | Good global coverage, Microsoft integration | Requires API key, usage-based pricing, less intuitive API |

**Google Maps** was rejected due to mandatory API key requirements, credit card registration, and usage-based pricing model that could lead to unexpected costs at scale.

**Apple Maps** was not chosen due to limited API accessibility and ecosystem focus that does not align with our cross-platform requirements.

**Yandex Maps** has insufficient coverage outside Russia and CIS regions, making it unsuitable for our global use case.

**Bing Maps** requires API keys and has a more complex pricing structure compared to the free options.

OpenStreetMap provides the best balance of cost, coverage, customization, and privacy for our project.

---

## 4. Consequences

### Positive Outcomes

- No API costs or billing complexity
- Full control over map infrastructure and data
- Privacy-respecting mapping solution
- Easy integration with popular JavaScript mapping libraries
- Multiple fallback tile providers available

### Tradeoffs and Considerations

- Tile quality and freshness varies by region (community-dependent)
- Public tile servers have fair-use policies; high-traffic apps may need custom server
- No built-in geocoding or routing services (separate integrations needed)
- Less polished default styling compared to commercial alternatives

---

## 5. References

- [OpenStreetMap Wiki](https://wiki.openstreetmap.org/)
- [OpenStreetMap Tile Usage Policy](https://wiki.openstreetmap.org/wiki/Tile_usage_policy)
- [Leaflet.js](https://leafletjs.com/) (recommended frontend library)
- [MapLibre GL](https://maplibre.org/) (alternative for vector tiles)
