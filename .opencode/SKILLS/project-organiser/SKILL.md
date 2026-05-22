---
name: project-organiser
description: Analyse a codebase and reorganise its folder structure into a clean, feature-based layout — then automatically fix imports, barrel files, build config, and CI/CD so everything still works. Use this skill whenever the user mentions messy files, wants to reorganise their project, asks about folder structure, wants to clean up their codebase, or says things like "organise my project", "structure my files", "tidy up my repo", "fix my imports", or "how should I lay out my code". Handles any tech stack — full-stack, frontend-only (React, Vue, etc.), backend-only (Node, Python, etc.), or monorepos. Always produces a visual plan first, applies it after confirmation, then runs TypeScript, lint, test, and build checks to verify everything passes.
---

# Project Organiser Skill

Analyse a codebase, propose a clean feature-based folder structure, then apply it with the user's sign-off.

---

## Step 1: Scan the Project

Use the Filesystem MCP (if connected) or bash to get a full picture of what exists:

```bash
# Get a full recursive tree, showing files
find . -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/__pycache__/*' -not -path '*/.next/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/.venv/*' | sort
```

Also read key config files to understand the stack:
- `package.json` / `pyproject.toml` / `requirements.txt` — dependencies, scripts
- `tsconfig.json` / `.eslintrc` — frontend config
- `Dockerfile` / `docker-compose.yml` — service layout
- `README.md` — stated architecture intent

If the Filesystem MCP is connected, prefer `directory_tree` for a clean overview, then `read_file` for configs.

---

## Step 2: Identify the Project Type

Based on the scan, classify the project:

| Type | Signals |
|---|---|
| **Frontend SPA** | React/Vue/Svelte entry, no server routes |
| **Backend API** | Express/FastAPI/Django, route handlers, no UI |
| **Full-stack (unified)** | Both frontend + backend in one repo |
| **Monorepo** | Multiple `package.json` / top-level `apps/` or `packages/` |
| **CLI tool** | `bin/`, argparse/yargs usage |

---

## Step 3: Build the Reorganisation Plan

### Core principle: Feature-based organisation

Group code by **what it does**, not what kind of file it is.

```
# ❌ Layer-based (avoid)
src/
  components/
  hooks/
  utils/
  types/

# ✅ Feature-based (prefer)
src/
  features/
    auth/
      components/
      hooks/
      api.ts
      types.ts
    dashboard/
      ...
  shared/        ← truly cross-cutting code only
    ui/
    utils/
    types/
```

### Universal top-level structure

```
project-root/
├── src/                   # All application source code
│   ├── features/          # Feature modules (see below)
│   ├── shared/            # Genuinely shared code
│   └── app/               # App entry, routing, global providers
├── tests/                 # All tests (mirrors src/ structure)
├── scripts/               # Build, deploy, seed scripts
├── docs/                  # Architecture docs, ADRs
├── config/                # Environment configs, tooling configs
├── public/                # Static assets (frontend)
└── [stack-specific]       # See per-stack additions below
```

### Per-stack additions

**Full-stack (unified repo)**
```
src/
  features/
    [feature]/
      components/     ← React/Vue components
      hooks/          ← frontend hooks
      routes/         ← backend route handlers
      services/       ← business logic
      models/         ← DB models / schemas
      api.ts          ← frontend API calls
      types.ts        ← shared types
  shared/
    ui/               ← design system components
    middleware/       ← shared Express/Fastify middleware
    db/               ← DB client, migrations
    utils/
```

**Frontend only**
```
src/
  features/
    [feature]/
      components/
      hooks/
      api.ts
      types.ts
  shared/
    ui/               ← design system / base components
    hooks/
    utils/
    assets/
  app/
    routes/
    providers/
    layout/
```

**Backend only**
```
src/
  features/
    [feature]/
      routes.ts       ← HTTP handlers
      service.ts      ← business logic
      model.ts        ← DB model
      types.ts
  shared/
    middleware/
    db/
    utils/
    errors/
  app/
    server.ts
    config.ts
```

**Monorepo**
```
apps/
  web/               ← frontend app
  api/               ← backend app
  [other apps]/
packages/
  ui/                ← shared component library
  utils/             ← shared utilities
  types/             ← shared TypeScript types
  config/            ← shared tooling config (eslint, ts, etc.)
```

### Tests

Mirror the `src/` structure inside `tests/`:
```
tests/
  unit/
    features/
      auth/
        auth.service.test.ts
  integration/
    features/
      auth/
        auth.routes.test.ts
  e2e/
    flows/
      login.spec.ts
```

---

## Step 4: Present the Plan

Show the user:

1. **What you found** — a short summary of the current state (messy, mixed concerns, etc.)
2. **The proposed new structure** — a clean annotated folder tree (use a code block)
3. **Key moves** — a table of where specific files/folders will move, e.g.:

| Current location | New location | Reason |
|---|---|---|
| `src/components/LoginForm.tsx` | `src/features/auth/components/LoginForm.tsx` | Belongs to auth feature |
| `utils/api.js` | `src/shared/utils/api.js` | Shared utility |
| `__tests__/` | `tests/unit/` | Standardised test location |

4. **What stays put** — root-level files that don't move (`package.json`, `.env`, `README.md`, etc.)

Then ask:

> "Does this plan look right? I can apply all the moves automatically, or we can adjust anything first."

---

## Step 5: Apply the Changes (after confirmation)

Once the user confirms, execute the reorganisation:

### Using bash
```bash
# Create new directories first
mkdir -p src/features/auth/components src/shared/ui ...

# Move files (use git mv if inside a git repo — preserves history)
git mv src/components/LoginForm.tsx src/features/auth/components/LoginForm.tsx

# Or plain mv if not a git repo
mv src/components/LoginForm.tsx src/features/auth/components/LoginForm.tsx

# Remove empty directories
find . -type d -empty -not -path '*/.git/*' -delete
```

### Using Filesystem MCP
If the Filesystem MCP is connected and the user's directory is accessible, prefer `move_file` calls for each file.

---

## Step 6: Fix Import Paths

After moving files, automatically update all broken imports across the codebase.

### TypeScript / JavaScript

```bash
# Find all files with imports that reference old paths
grep -rl "from ['\"].*old/path" src/ --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx"
```

For each moved file, compute its old and new path, then do a targeted find-and-replace across the whole codebase.

**Strategy:**
1. Build a mapping of `{ oldPath → newPath }` from the moves made in Step 5
2. For each source file in the project, scan for `import` / `require` / `export from` statements
3. Resolve each import relative to the file it lives in, check if it matches an old path, and rewrite it to the new relative path

Use `sed` for simple cases:
```bash
# Replace a specific import across all TS/JS files
find src -name "*.ts" -o -name "*.tsx" | xargs sed -i "s|from '../components/LoginForm'|from '../auth/components/LoginForm'|g"
```

For complex rewrites (many files, deep nesting), use a Node.js script:
```bash
node -e "
const fs = require('fs');
const path = require('path');
const glob = require('glob'); // or use fs.readdirSync recursively

const moves = {
  'src/components/LoginForm': 'src/features/auth/components/LoginForm',
  // ... all moves
};

// For each .ts/.tsx/.js/.jsx file, rewrite imports
"
```

### Python

```bash
# Find all imports referencing old module paths
grep -rn "from old.module.path import\|import old.module.path" --include="*.py" .

# Rewrite with sed
find . -name "*.py" | xargs sed -i "s/from old\.module\.path/from new.module.path/g"
```

### After rewriting imports

Run a quick sanity check to confirm no old paths remain:
```bash
# Should return nothing if all imports were updated
grep -rn "from ['\"].*components/LoginForm" src/ --include="*.ts" --include="*.tsx"
```

---

## Step 7: Create / Update Barrel Files

Barrel files (`index.ts` / `index.js`) let consumers import cleanly from a feature rather than a deep path.

### Create a barrel for each feature folder

For every `src/features/[feature]/` directory, create or update `index.ts`:

```typescript
// src/features/auth/index.ts
export { LoginForm } from './components/LoginForm';
export { useAuth } from './hooks/useAuth';
export { authApi } from './api';
export type { AuthUser, AuthState } from './types';
```

### Create a barrel for shared/

```typescript
// src/shared/ui/index.ts
export { Button } from './Button';
export { Input } from './Input';
export { Modal } from './Modal';
```

### Update existing barrel files

If the project already had barrel files, check they still point to the right locations and update any stale re-exports.

```bash
# Find all index files that might have stale exports
grep -rn "export.*from" src --include="index.ts" --include="index.js"
```

---

## Step 8: Update Build Config

Fix any hardcoded paths in build tooling.

### tsconfig.json — path aliases

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/features/*": ["src/features/*"],
      "@/shared/*":   ["src/shared/*"],
      "@/app/*":      ["src/app/*"]
    }
  }
}
```

Read the current `tsconfig.json`, identify any `paths` entries pointing to old locations, and update them. Also check `include` / `exclude` arrays.

### vite.config.ts

```typescript
export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@features': path.resolve(__dirname, './src/features'),
      '@shared': path.resolve(__dirname, './src/shared'),
    }
  }
})
```

### webpack.config.js

```javascript
resolve: {
  alias: {
    '@': path.resolve(__dirname, 'src'),
    '@features': path.resolve(__dirname, 'src/features'),
  }
}
```

### next.config.js

Next.js auto-resolves `@/` from `tsconfig.json` — no extra config needed if `paths` is set there.

### jest.config.ts / vitest.config.ts

```typescript
moduleNameMapper: {
  '^@/(.*)$': '<rootDir>/src/$1',
  '^@features/(.*)$': '<rootDir>/src/features/$1',
}
```

### Python (pyproject.toml / setup.cfg)

If using a src layout, ensure `pythonpath` or `packages` entries are updated:
```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
```

---

## Step 9: Update CI/CD

Scan all CI/CD config files and fix hardcoded paths.

### Files to check

```bash
find . -path './.git' -prune -o -name "*.yml" -print -o -name "*.yaml" -print | grep -E "(github|gitlab|circle|jenkins|azure|bitbucket)"
# Also check:
ls .github/workflows/
cat Dockerfile
cat docker-compose.yml
cat Makefile
```

### Common things to fix

**GitHub Actions**
```yaml
# Old
- run: npm test -- --testPathPattern=src/components

# New
- run: npm test -- --testPathPattern=src/features
```

Look for and update:
- `working-directory` paths
- `--testPathPattern` / `--coverage-directory` flags
- `COPY` instructions in Dockerfiles that reference `src/` subdirectories
- Volume mounts in `docker-compose.yml`
- `coverage` report paths in codecov/coveralls config

### Dockerfile

```dockerfile
# Check COPY instructions for stale paths
COPY src/server ./src/server   # ← may need updating
```

Read the full Dockerfile and update any `COPY`, `ADD`, or `WORKDIR` paths that changed.

---

## Step 10: Verify Everything Works

Run the project's own tooling to confirm nothing is broken.

### TypeScript type check (no compilation)
```bash
npx tsc --noEmit
```
Zero errors = imports and types are all resolved correctly.

### Lint
```bash
npx eslint src --ext .ts,.tsx,.js,.jsx
# or
npx biome check src/
```

### Tests
```bash
npm test          # or: npx vitest, npx jest, pytest, etc.
```

### Build
```bash
npm run build     # or: npx vite build, python -m build, etc.
```

### Start (dev server)
```bash
npm run dev       # or equivalent — confirm it starts without errors
```

### Report results to the user

After running checks, present a clear summary:

```
✅ TypeScript — 0 errors
✅ Lint       — 0 warnings
✅ Tests      — 142 passed, 0 failed
✅ Build      — completed in 4.2s
✅ Dev server — started on http://localhost:3000
```

If anything fails, diagnose and fix before reporting back. Common issues:
- **Missing import** — a file was moved but its import wasn't caught; fix the import and re-run
- **Alias not resolved** — build tool alias config wasn't updated; go back to Step 8
- **Test path pattern wrong** — CI or jest config still points to old path; fix in Step 9
- **Circular import via barrel** — a barrel file imports something that imports the barrel; remove the circular re-export

Only mark the reorganisation complete once all checks pass cleanly.

---

## Edge Cases

- **Already partially organised**: Acknowledge what's already good, only suggest changes where there's genuine improvement
- **Large monorepos**: Focus on the top 3-5 noisiest areas, don't try to move everything at once
- **Framework conventions**: Respect framework conventions (e.g. Next.js `app/` or `pages/` directory — don't fight the framework)
- **Config files at root**: Leave tooling configs (`eslint`, `prettier`, `tsconfig`, etc.) at the root — that's correct
- **No git repo**: Warn the user that moves can't be undone easily, suggest they back up or initialise git first

---

## Tone

Be direct and practical. Don't over-explain — show the tree, explain the key decisions briefly, and let the user react. If the codebase is small, the whole interaction should feel quick and light. For large projects, be more thorough but still concise. Always focus on the benefits of the new structure (easier to navigate, better separation of concerns, more scalable) rather than just the mechanics of moving files. 