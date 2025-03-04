<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <q-layout view="hHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-toolbar-title>Mind vs Wild</q-toolbar-title>
        <q-btn flat to="/" label="Home" />
        <q-btn flat to="/about" label="About" />
        <q-btn flat to="/login" label="Login" />
        <q-btn flat to="/register" label="Register" />
        <q-btn flat to="/rooms" label="Rooms" />
        <q-btn flat to="/groups" label="Groups" />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
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
