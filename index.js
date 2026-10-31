// OpenCode V2 (2.0.4+) rejects bare file paths, so it loads this plugin from the
// repository directory. Re-export the real plugin.
export { default, PragmaticDevxPlugin } from "./.opencode/plugins/pragmatic-devx.js";
