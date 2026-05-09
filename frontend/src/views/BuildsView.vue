<script setup>
import { Columns3, Filter, Search, Trash2, X } from 'lucide-vue-next'

const rows = [
  { name: 'frontend', id: 'o4byjh', duration: '1.9s', created: '2 minutes ago' },
  { name: 'backend', id: '9jquos', duration: '2.0s', created: '2 minutes ago' },
  { name: 'backend', id: 'l684ue', duration: '20.9s', created: '3 minutes ago' },
  { name: 'frontend', id: 'umiwuz', duration: '35.7s', created: '3 minutes ago' }
]
</script>

<template>
  <section class="page">
    <div class="page-title-row">
      <h1 class="page-title">Builds</h1>
      <a href="#" class="feedback-link">Give feedback</a>
    </div>

    <p class="page-subtitle">Build container images and artifacts from source code. <a href="#">Learn more</a></p>

    <div class="banner">
      <div>
        <strong>Build large and multi-platform Docker images faster in Docker Build Cloud.</strong>
        <span>To improve build speeds for you, your team, and even your CI, try Docker Build Cloud now</span>
      </div>
      <X />
    </div>

    <div class="tabs">
      <button class="tab active">Build history</button>
      <button class="tab">Active builds</button>
    </div>

    <div class="toolbar">
      <label class="search-box">
        <Search size="30" />
        <input placeholder="Search" />
      </label>
      <button class="icon-button"><Columns3 size="31" /></button>
      <button class="icon-button"><Filter size="31" /></button>
    </div>

    <div class="table-panel">
      <table class="docker-table">
        <thead>
          <tr>
            <th class="check-cell"><div class="checkbox"></div></th>
            <th></th>
            <th>Name</th>
            <th>ID</th>
            <th>Builder</th>
            <th>Duration</th>
            <th>Created</th>
            <th>Author</th>
            <th></th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="row in rows" :key="row.id">
            <td><div class="checkbox"></div></td>
            <td style="color: #438c82;">✓</td>
            <td>{{ row.name }}</td>
            <td>{{ row.id }}</td>
            <td><a href="#">default</a></td>
            <td>{{ row.duration }}</td>
            <td>{{ row.created }}</td>
            <td>N/A</td>
            <td><button class="icon-button danger"><Trash2 /></button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
