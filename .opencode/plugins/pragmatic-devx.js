/**
 * Pragmatic DevX plugin for OpenCode.
 *
 * Dual-compatible with OpenCode V1 and V2, with no external dependencies.
 *
 * V1: loaded via the named export — the `config` hook registers `skills/` in
 * `config.skills.paths`, and `experimental.chat.messages.transform` injects the
 * pragmatic-howto bootstrap into the first user message.
 *
 * V2: loaded via the default export `{ id, setup }` — `setup()` registers each
 * skill with `ctx.skill.transform()` and injects the bootstrap through
 * `ctx.session.hook("context")`.
 */

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const skillsDir = path.resolve(__dirname, "../../skills");

const BOOTSTRAP_MARKER = "pragmatic-devx:pragmatic-howto bootstrap for opencode";

// Frontmatter is flat `key: value` with quoted or folded descriptions; this is
// not a YAML parser, only enough for the name/description fields used here.
const extractAndStripFrontmatter = (content) => {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!match) return { frontmatter: {}, content };

  const frontmatter = {};
  let lastKey = null;
  for (const rawLine of match[1].split("\n")) {
    const line = rawLine.replace(/\r$/, "");
    const colonIdx = line.indexOf(":");
    if (colonIdx > 0 && !/^\s/.test(line)) {
      const key = line.slice(0, colonIdx).trim();
      const value = line.slice(colonIdx + 1).trim();
      frontmatter[key] = /^(>[+-]?|\|[+-]?)$/.test(value) ? "" : value;
      lastKey = key;
    } else if (lastKey !== null && line.trim() !== "") {
      frontmatter[lastKey] = `${frontmatter[lastKey]} ${line.trim()}`.trim();
    }
  }
  for (const key of Object.keys(frontmatter)) {
    frontmatter[key] = frontmatter[key].replace(/^(["'])([\s\S]*)\1$/, "$2");
  }
  return { frontmatter, content: match[2] };
};

// The three subagents under agents/ are Claude Code definitions and are not
// registered in OpenCode, so skills must take their "no subagent" fallbacks.
const sharedMapping = `- Skill invocation → OpenCode's native \`skill\` tool
- \`AskUserQuestion\` → ask the user directly in the conversation
- Read / Write / Edit files → \`read\`, \`write\`, \`edit\`
- Search files → \`glob\`, \`grep\`
- Fetch a URL → \`webfetch\`
- Subagents: \`tdd-implementer\`, \`task-reviewer\` and \`fact-finder\` are not installed in OpenCode. Treat the \`Agent\` tool as unavailable and follow each skill's "no subagent" fallback, doing the work in this session.`;

const V1_MAPPING = `## OpenCode tool mapping

- \`TodoWrite\` → \`todowrite\`
- Run shell commands → \`bash\`
${sharedMapping}`;

const V2_MAPPING = `## OpenCode tool mapping

- \`TodoWrite\` → OpenCode v2 has no todo tool; track the plan in a markdown file or the harness's plan facility
- Run shell commands → \`shell\`
${sharedMapping}`;

const _bootstrapCache = new Map(); // mapping -> bootstrap (null = file missing)

const getBootstrapContent = (toolMapping) => {
  if (_bootstrapCache.has(toolMapping)) return _bootstrapCache.get(toolMapping);

  const skillPath = path.join(skillsDir, "pragmatic-howto", "SKILL.md");
  if (!fs.existsSync(skillPath)) {
    _bootstrapCache.set(toolMapping, null);
    return null;
  }

  const { content } = extractAndStripFrontmatter(fs.readFileSync(skillPath, "utf8"));
  _bootstrapCache.set(
    toolMapping,
    `<EXTREMELY_IMPORTANT>
${BOOTSTRAP_MARKER}

You have pragmatic-devx skills.

The pragmatic-howto skill content is included below and is already loaded for this session. Follow it now. Do not load pragmatic-howto again.

${content.trim()}

${toolMapping}
</EXTREMELY_IMPORTANT>`,
  );
  return _bootstrapCache.get(toolMapping);
};

/**
 * V1 plugin function (named export).
 */
export const PragmaticDevxPlugin = async () => ({
  config: async (config) => {
    // V2 hands over a flat array; setup() registers skills there instead.
    if (Array.isArray(config.skills)) return;

    config.skills = config.skills || {};
    config.skills.paths = config.skills.paths || [];
    if (!config.skills.paths.includes(skillsDir)) {
      config.skills.paths.push(skillsDir);
    }
  },

  // Fires on every agent step with freshly loaded messages, hence the guard.
  "experimental.chat.messages.transform": async (_input, output) => {
    const bootstrap = getBootstrapContent(V1_MAPPING);
    if (!bootstrap || !output.messages.length) return;
    const firstUser = output.messages.find((m) => m.info.role === "user");
    if (!firstUser || !firstUser.parts.length) return;
    if (firstUser.parts.some((p) => p.type === "text" && p.text.includes(BOOTSTRAP_MARKER))) return;

    firstUser.parts.unshift({ ...firstUser.parts[0], type: "text", text: bootstrap });
  },
});

/**
 * V2 setup function (default export `setup`).
 */
async function setup(ctx) {
  // V1 also calls default.setup, with a ctx lacking the skill/session domains.
  if (
    !ctx ||
    !ctx.skill ||
    typeof ctx.skill.transform !== "function" ||
    !ctx.session ||
    typeof ctx.session.hook !== "function"
  ) {
    return;
  }

  // An error escaping a plugin takes down the whole V2 generation, so every
  // step below contains its own failures.
  try {
    const skills = [];
    if (fs.existsSync(skillsDir)) {
      for (const entry of fs.readdirSync(skillsDir, { withFileTypes: true })) {
        if (!entry.isDirectory() || entry.name.startsWith(".")) continue;
        const skillPath = path.join(skillsDir, entry.name, "SKILL.md");
        if (!fs.existsSync(skillPath)) continue;
        const { frontmatter, content } = extractAndStripFrontmatter(fs.readFileSync(skillPath, "utf8"));
        skills.push({
          id: entry.name,
          name: frontmatter.name || entry.name,
          ...(frontmatter.description ? { description: frontmatter.description } : {}),
          path: skillPath,
          content,
        });
      }
    }
    await ctx.skill.transform((draft) => {
      for (const skill of skills) {
        try {
          draft.add(skill);
        } catch (err) {
          console.error(`[pragmatic-devx] skill "${skill.id}" rejected by host, skipping:`, err);
        }
      }
    });
  } catch (err) {
    console.error("[pragmatic-devx] skill registration failed:", err);
  }

  try {
    await ctx.session.hook("context", async (event) => {
      try {
        const bootstrap = getBootstrapContent(V2_MAPPING);
        if (!bootstrap || !event.messages || !event.messages.length) return;
        const firstUser = event.messages.find((m) => m.role === "user");
        if (firstUser && (!firstUser.content || !firstUser.content.length)) return;
        if (firstUser?.content.some((p) => p.type === "text" && p.text && p.text.includes(BOOTSTRAP_MARKER))) return;

        if (firstUser) {
          firstUser.content.unshift({ type: "text", text: bootstrap });
        } else {
          event.messages.push({ role: "user", content: [{ type: "text", text: bootstrap }] });
        }
      } catch (err) {
        console.error("[pragmatic-devx] context hook failed:", err);
      }
    });
  } catch (err) {
    console.error("[pragmatic-devx] session hook registration failed:", err);
  }
}

export default {
  id: "pragmatic-devx",
  server: PragmaticDevxPlugin,
  setup,
};
