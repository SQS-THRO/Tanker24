<script lang="ts">
  import Button from '$lib/components/button.svelte';
</script>

<main>
  <!-- HERO -->
  <section class="hero">
    <h1>Fill your Gas cheaper with Tanker24</h1>
    <p>The modern way to fill you Gas</p>
    <Button label="Go to Map" href="/map" />
  </section>

  <!-- FEATURES -->
  <section class="features">
    <div class="card">
      <h3>⚡ Fast</h3>
    </div>
    <div class="card">
      <h3>🧩 Simple</h3>
    </div>
    <div class="card">
      <h3>🚀 Powerful</h3>
    </div>
  </section>
</main>

<style>
  main {
    font-family: system-ui, sans-serif;
    text-align: center;
  }

  section {
    padding: 4rem 2rem;
  }

  .hero {
    background: #111;
    color: white;
  }

  .hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .features {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
  }

  .card {
    background: #f5f5f5;
    padding: 1.5rem;
    border-radius: 10px;
    width: 200px;
  }
</style>
