# Local model preview dependency

Google model-viewer 4.1.0, Apache-2.0. Bundled module: `@google/model-viewer@4.1.0/dist/model-viewer.min.js` (979139 bytes). Package metadata and upstream license are preserved alongside it.

Upstream: https://github.com/google/model-viewer/tree/v4.1.0
Official API documentation: https://modelviewer.dev/docs/ and https://modelviewer.dev/examples/animation/
Downloaded module: https://unpkg.com/@google/model-viewer@4.1.0/dist/model-viewer.min.js

The viewer is imported locally only after clicking Load 3D. No model is sent to another service. No external CDN runtime is configured. Uncompressed GLB is the supported preview path; unsupported models display an explicit error. Models using compressed textures or Draco decoding can require additional decoder resources and are not claimed supported.
