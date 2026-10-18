# 3d-designs

FreeCAD designs for 3D-printed parts, one project per top-level folder.

## Layout

| Path | Contents |
|---|---|
| `<Project>/PLAN.md` | Decisions, datum (reference coordinates), openings, open inputs, print notes. Source of truth for intent |
| `<Project>/*_proto.py` | Parametric generator. Source of truth for geometry; the `.FCStd` is its output |
| `<Project>/*.stp` | Vendor reference model (read-only) |
| `<Project>/exports/` | Print-ready STLs written by the generator |
| `<Project>/*.png` | Renders of the current version |
| `README.md` | User-facing overview: what each project is, files, printing, assembly, customizing |
| `.codegraph/`, `.pi/` | Tooling indexes; ignore |

### Projects

| Folder | What |
|---|---|
| `10.1-ESP-Touchscreen-Frame/` | Desk case + magnetic cradle for the Elecrow CrowPanel Advanced 10.1" ESP32-P4 |

A new project gets its own folder with a `PLAN.md` and a generator, following the same pattern.

## Docs: repo and Outline

Project docs live in two places: the repo and Outline (Outline MCP), under the **Projects** collection → **3D Designs** page. Keep them in sync: when you change a project doc in the repo, update its Outline page in the same task, and the other way round.

| Repo file | Outline page |
|---|---|
| `README.md` | **3D Designs** (`80d1e751-8661-4777-b769-ddafd38cb907`), the overview |
| `<Project>/PLAN.md` | A child page of **3D Designs**, titled after the project. CrowPanel: **CrowPanel 10.1" Desk Case** (`261d1d51-8ea9-4885-9e20-d4137bc6b668`) |

- **Synced:** user-facing and design docs only (`README.md`, each project's `PLAN.md`, and any new project doc).
- **Not synced:** agent material such as implementation plans, task lists, scratch notes, and `CLAUDE.md` itself. Keep those in the repo or the scratchpad.
- **A new project** gets a child page under **3D Designs** and a row in the overview's project table.
- **Outline formatting:** the title is a separate field, so the body starts without an H1. Repo-relative links and images don't resolve there. Link files as `https://github.com/voidrot/3d-designs/blob/main/<path>`, and embed LFS images from `https://media.githubusercontent.com/media/voidrot/3d-designs/main/<path>`.
- Edit existing Outline pages with `update_document` in `patch` mode when the change is local. Use `replace` only for a full resync.

## Environment

- **FreeCAD 1.1.4.** `/usr/bin/freecadcmd` for headless runs, plus the GUI for prototyping.
- **FreeCAD MCP** (`.mcp.json`, `uvx freecad-mcp`) drives the running GUI.
- **Printer:** Bambu Studio, 256 × 256 mm bed. Parts up to ~252 mm print in one piece.
- **Hardware on hand:** 6 × 3 mm disc magnets and M3 screws.

## Workflow

1. Write the plan first: `PLAN.md` with the datum measured from the vendor STEP, decisions, and open inputs. Ask the user for physical measurements the STEP lacks.
2. Prototype in the GUI through MCP: `execute_code` with `exec(open("<abs path>/x_proto.py").read())`. Iterate until the user approves the look; don't jump ahead to printing tasks.
3. The generator rebuilds every `Case_*` object each run and reuses the imported STEP reference, so re-runs are fast. Save with `doc.save()`.
4. Each run ends with checks and an STL export (see below). Report check output, not assumptions.

## Generator conventions

- **Display frame:** +z up, the part's front faces −y (FreeCAD "Front" view), +x right. Rotate the vendor STEP into this frame once at import (via its parent `App::Part`).
- Parameters sit in one block at the top. Every physical tolerance has a parameter (clearance, boss height, pocket fits) so a test print can tune it.
- Build a monolithic body, cut every opening once, then split at the seam. Features that cross the seam (ribs, tubes, bosses) must fuse to their owning part **after** the split, or they end up as loose solids in the other part.
- Show tilted or posed views by placing case and reference objects in an `App::Part` assembly. Never re-transform the reference itself on each run.
- Keep ≥ 0.5 mm between bosses and walls. Gaps of 0.1 mm print as hairs or fuse.

## Checks every run

- Each part `isValid()` with exactly one solid (text inlays are the exception: one solid per letter).
- Zero common volume against every visible reference solid and between mating parts. Use `shape.copy()` with `obj.getGlobalPlacement()`: nested STEP parts report local coordinates otherwise.
- **Overhang audit** in print orientation. Flag faces within 45° of straight down, excluding the bed face. Don't trust `Face.normalAt` orientation; flip the normal if `isInside(point + n*0.05)`.
- **Exports:** closed solid, no non-manifold edges, z min = 0, every axis ≤ 256 mm. Reload STLs headless to confirm.

## Print design rules (user preferences)

- **No supports.** Overhangs ≥ 45° from horizontal, flat bridges ≤ ~10 mm (use pitched roofs and triangular grooves).
- **Magnet pockets** open upward in print orientation, so magnets glue in after printing with no print pause. Leave a 0.6 mm skin where a magnet must stay hidden.
- **Low infill** instead of hollowing solid parts.
- **Multi-color text:** a separate body inlaid flush, 0.6 mm deep, in the bed-facing face. Export it as its own STL with the same transform as its host. In Bambu Studio, import both at once and choose "one object with multiple parts". This needs an AMS.
- **STL exports:** one per part, already in print orientation, centered on x/y, at z = 0, written to `exports/`.

## Research tips

- Vendor GitHub repos often ship Eagle `.sch`/`.brd` files. They're XML, so parse them with Python to verify power paths, connector pinouts, footprints, and port holes. On the CrowPanel this showed the second mic in the STEP doesn't exist on the real board.
- Check vendor STEPs against photos. Flex cables are often modeled flat, sub-parts misplaced at the origin, and glued-on parts (speakers) missing.
- Mark anything not confirmed by a primary source as UNCONFIRMED in `PLAN.md`.

## Gotchas

- `freecadcmd script.py` silently does nothing. Use `freecadcmd -c "exec(open('script.py').read())"`.
- MCP GUI calls queue behind a mouse drag in the 3D view and time out. Check `get_rpc_status` and retry. The first import of a ~20 MB STEP takes over 2 minutes, so pass a long `timeout`.
- `Part.makeWireString` returns empty wire lists for spaces. Skip them before `Part.makeFace(..., "Part::FaceMakerBullseye")`, or you get "result shape is null". Bullseye handles letters with holes.
- **Screenshots:** `setViewDirection` without an up vector gives skewed views. Temporarily reset the assembly placement and use the standard views instead.
- The shell aliases `mv` to ask before overwriting, which hangs non-interactive commands. Use `\mv -f`.
- FreeCAD writes `*.FCBak` backups next to saved documents (gitignored).
- **Git LFS** tracks `*.FCStd`, `*.stl`, `*.stp`/`*.step`, `*.3mf`, `*.png` (see `.gitattributes`); the hooks are installed with `--local`. Add new binary types there before committing them. After `git lfs migrate`, the working tree can be left holding pointer files; `git lfs checkout` restores the content.
