---
icon: simple/tailwindcss
---

# ADR 008: Choosing Tailwind CSS for Styling

**Date:** 2026-03-26  
**Context:** Styling and UI Development  

---

## 1. Context

Our project requires a scalable and maintainable approach to styling our Svelte components. The key requirements include:

- Consistent design system across all components
- Rapid UI development and iteration
- Easy theming and customization
- Minimal CSS bundle size
- Good integration with Svelte's component model
- Support for responsive design

We evaluated several styling approaches to determine the best fit for our requirements.

---

## 2. Decision

We decided to adopt **Tailwind CSS** as the primary styling solution for our application.

---

## 3. Rationale

### Benefits of using Tailwind CSS:

- **Utility-First Approach**:
	- Compose small, single-purpose classes to build complex designs
	- No need to invent class names for every component
	- Highly readable and self-documenting markup

- **Consistent Design System**:
	- Predefined design tokens (colors, spacing, typography)
	- Enforces visual consistency across the entire application
	- Easy to maintain and update globally

- **Rapid Development**:
	- No context switching between files (HTML and CSS together)
	- Quick prototyping with inline styles
	- Fast iteration on UI changes

- **Performance Optimization**:
	- Automatic purging removes unused styles in production
	- Generates minimal CSS bundles
	- No runtime overhead

- **Responsive Design Built-In**:
	- Mobile-first breakpoints out of the box
	- Simple responsive variants (sm:, md:, lg:, etc.)
	- Easy to create adaptive layouts

- **Theming Flexibility**:
	- Easy to customize via configuration
	- Support for dark mode, custom color palettes
	- CSS variables integration for runtime theming

- **Good Svelte Integration**:
	- Works seamlessly with Svelte components
	- Can be scoped to components when needed
	- PostCSS ecosystem compatibility

### Alternatives considered:

| Option | Pros | Cons |
|--------|------|------|
| Plain CSS | No dependencies, full control, standard browser feature | Poor scalability, naming conflicts, code duplication |
| CSS Modules | Scoped styles, no conflicts, native to build tools | Limited reusability, verbose class names, no design tokens |
| Styled Components | Component-based, dynamic styles, good DX | Runtime overhead, larger bundles, JS-in-CSS syntax |
| Sass/SCSS | Preprocessing, variables, mixins, nesting | Still requires naming conventions, no design system enforcement |
| UnoCSS | Very fast, atomic CSS, highly customizable | Newer ecosystem, smaller community, different paradigm |

**Plain CSS** was rejected due to poor scalability and naming conflicts in larger applications.

**CSS Modules** were not chosen as they don't provide a design system or design tokens out of the box.

**Styled Components** introduce runtime overhead and larger bundle sizes, which conflicts with our performance goals.

**Sass/SCSS** requires maintaining naming conventions and doesn't enforce design system consistency.

**UnoCSS** is an interesting alternative but has a smaller community and ecosystem compared to Tailwind CSS.

Tailwind CSS provides the best balance of developer experience, performance, and design system enforceability for our project.

---

## 4. Consequences

### Positive Outcomes

- Faster UI development through utility-first approach
- Consistent design system across all components
- Smaller production CSS bundles through automatic purging
- Easy responsive design implementation
- Simplified maintenance with centralized configuration
- Reduced CSS naming conflicts

### Tradeoffs and Considerations

- HTML markup can become verbose with many utility classes
- Learning curve for utility class names
- Requires build tool configuration (PostCSS, Vite plugin)
- Some team members may prefer traditional CSS/SCSS approach
- Dynamic styles may require workarounds (e.g., arbitrary values)

---

## 5. References

- [Tailwind CSS](https://tailwindcss.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind CSS with Svelte](https://tailwindcss.com/docs/guides/sveltekit)
- [Tailwind UI](https://tailwindui.com/) (component library)
