<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <div class="wrapper">
      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/about">About</RouterLink>
        <RouterLink to="/login">Login</RouterLink>
      </nav>
    </div>
  </header>
  <RouterView />
</template>

<style scoped>
header {
  position: fixed; 
  top: 0;
  left: 0;
  width: 100%;
  height: auto; 
  max-height: 60px;
  background-color: var(--color-background);
  padding: 1rem 0;
  z-index: 1000;
  display: flex;
  align-items: flex-start; 
}

nav {
  display: flex;
  align-items: center;
  justify-content: flex-start; 
  font-size: 14px;
  padding-left: 1rem;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}
</style>


