<script setup>
import {
  Activity,
  Container,
  Database,
  Hammer,
  Hexagon,
  PackageSearch,
  Puzzle,
  Settings,
  Terminal
} from 'lucide-vue-next'
</script>

<template>
  <div class="desktop-shell">
    <aside class="desktop-sidebar">
      <nav class="sidebar-section">
        <RouterLink to="/colima" class="sidebar-link">
          <Activity size="22" />
          <span>Colima</span>
        </RouterLink>

        <RouterLink to="/containers" class="sidebar-link">
          <Container size="22" />
          <span>Containers</span>
        </RouterLink>

        <RouterLink to="/images" class="sidebar-link">
          <PackageSearch size="22" />
          <span>Images</span>
        </RouterLink>

        <RouterLink to="/volumes" class="sidebar-link">
          <Database size="22" />
          <span>Volumes</span>
        </RouterLink>

        <RouterLink to="/builds" class="sidebar-link">
          <Hammer size="22" />
          <span>Builds</span>
        </RouterLink>
      </nav>

      <div class="sidebar-separator"></div>

      <nav class="sidebar-section">
        <a href="https://github.com/abiosoft/colima" target="_blank" class="sidebar-link">
          <Hexagon size="22" />
          <span>Colima on GitHub</span>
        </a>

        <a href="https://hub.docker.com" target="_blank" class="sidebar-link">
          <Terminal size="22" />
          <span>Docker Hub</span>
        </a>
      </nav>

      <div class="sidebar-separator"></div>

      <nav class="sidebar-section">
        <RouterLink to="/settings" class="sidebar-link">
          <Puzzle size="22" />
          <span>Extensions</span>
        </RouterLink>
      </nav>

      <div class="sidebar-bottom">
        <RouterLink to="/settings" class="sidebar-link compact">
          <Settings size="20" />
          <span>Settings</span>
        </RouterLink>
      </div>
    </aside>

    <main class="desktop-main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.desktop-shell { display: flex; min-height: 100vh; background: white; }
.desktop-sidebar {
  position: sticky; top: 0; display: flex; flex-direction: column; width: 350px; height: 100vh;
  padding: 18px 10px; background: #f6f6f7; border-right: 1px solid #eceff2;
}
.sidebar-section { display: grid; gap: 4px; }
.sidebar-link {
  display: flex; align-items: center; gap: 22px; min-height: 48px; padding: 0 24px;
  border-radius: 5px; color: #17191c; text-decoration: none; font-size: 21px; font-weight: 450;
}
.sidebar-link svg { color: #596272; }
.sidebar-link:hover, .sidebar-link.router-link-active { background: #d1d1d4; }
.sidebar-separator { height: 1px; background: #dedfe2; margin: 18px 0; }
.sidebar-bottom { margin-top: auto; }
.sidebar-link.compact { font-size: 18px; }
.desktop-main { flex: 1; min-width: 0; }
@media (max-width: 1050px) {
  .desktop-sidebar { width: 270px; }
  .sidebar-link { gap: 14px; font-size: 18px; }
}
</style>
