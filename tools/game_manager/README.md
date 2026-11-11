# Source Game Manager

Python 3.10+ standard library only. Start from the repository root:

    python tools/game_manager/server.py --port 8781

Open http://127.0.0.1:8781/. The server binds only to 127.0.0.1. Catalog is derived at startup from the preserved candidate37 163-file closure and current source definitions, plus bounded assets/ and chapter1/art/ inventories. Restart to refresh source facts. No Godot or game process is launched.

Management state is separate from game data and stored atomically in local-state.json (ignored by Git). Status, priority and notes are management annotations, not gameplay quality results. Old revisions return HTTP 409 with the current revision and records. JSON requests require a trusted local Host and absent or same-origin Origin. Only catalog-listed source/art and preserved v44 book files are exposed through /files/. Paths outside the project and user saves are blocked.

Run backend checks:

    python -m unittest discover -s tools/game_manager -p "test_*.py" -v

Catalog limitations are included in warnings. A packaged file is not automatically an observed in-game asset. Actor atlas definitions and GLB skeleton/animation metadata describe source artifacts; visual quality and live gameplay are separate checks. Existing book and workbench files remain in their original locations.

Candidate38 selection: ui38/package38 is selected only after the actual packaged integration and PCK audit both report success, the integration process exits successfully, all166 source paths exist, and the executable size/SHA256 matches build.json. Otherwise candidate37 remains selected. The three UI38 source files remain inspectable while the package is pending. Selected entry/controller references determine direct vs inherited use; filenames do not. Candidate37 closure remains available under build.preserved_builds.
