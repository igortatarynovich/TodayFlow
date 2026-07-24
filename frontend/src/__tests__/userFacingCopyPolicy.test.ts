import fs from "node:fs";
import path from "node:path";

const USER_FACING_DIRS = [
  "src/app",
  "src/components",
];

const USER_FACING_FILES = [
  "src/lib/coldStart.ts",
  "src/lib/thematicReports.ts",
  "../docs/today-language/TODAY_LANGUAGE_V1.md",
];

const TEXT_FILE_EXTENSIONS = new Set([".ts", ".tsx", ".md"]);

const FORBIDDEN_PATTERNS: RegExp[] = [
  /\bAI\b/i,
  /\bLLM\b/i,
  /model-based/i,
  /искусственн(?:ый|ого)\s+интеллект/i,
  /нейросет/i,
  /генератив/i,
  /\bпродукт\w*\b/i,
  /как\s+это\s+работает/i,
  /как\s+устроен/i,
  /как\s+считается/i,
  /внутренн\w+\s+расчет/i,
  /\bформул(а|ы|у|ой|е)\b/i,
];

// Soft anti-manipulation gate: looks for pressure/fear framing.
const PRESSURE_FEAR_PATTERNS: RegExp[] = [
  /\bсрочно\b/i,
  /если\s+не\s+.+(потеря|хуже|проблем|опасн)/i,
  /\bиначе\s+будет\b/i,
  /\bиначе\s+ты\s+(потеря|упуст|останешь)/i,
  /\bдолжен\b\s+прямо\s+сейчас/i,
];

function collectFilesRecursive(absoluteDirPath: string): string[] {
  if (!fs.existsSync(absoluteDirPath)) return [];
  const entries = fs.readdirSync(absoluteDirPath, { withFileTypes: true });
  const result: string[] = [];

  for (const entry of entries) {
    if (entry.name.startsWith(".")) continue;
    const absolutePath = path.join(absoluteDirPath, entry.name);

    if (entry.isDirectory()) {
      result.push(...collectFilesRecursive(absolutePath));
      continue;
    }

    if (TEXT_FILE_EXTENSIONS.has(path.extname(entry.name))) {
      result.push(absolutePath);
    }
  }

  return result;
}

describe("user-facing copy policy", () => {
  it("does not contain prohibited AI/model framing", () => {
    const repoRoot = process.cwd();

    const scannedFiles = [
      ...USER_FACING_DIRS.flatMap((relativeDir) =>
        collectFilesRecursive(path.join(repoRoot, relativeDir)),
      ),
      ...USER_FACING_FILES.map((relativeFile) => path.join(repoRoot, relativeFile)),
    ].filter((absolutePath) => fs.existsSync(absolutePath));

    const violations: string[] = [];

    for (const absolutePath of scannedFiles) {
      const content = fs.readFileSync(absolutePath, "utf-8");
      for (const pattern of FORBIDDEN_PATTERNS) {
        const match = content.match(pattern);
        if (!match) continue;
        const relativePath = path.relative(repoRoot, absolutePath);
        violations.push(`${relativePath} -> "${match[0]}"`);
      }
    }

    expect(violations).toEqual([]);
  });

  it("does not contain pressure/fear triggers", () => {
    const repoRoot = process.cwd();

    const scannedFiles = [
      ...USER_FACING_DIRS.flatMap((relativeDir) =>
        collectFilesRecursive(path.join(repoRoot, relativeDir)),
      ),
      ...USER_FACING_FILES.map((relativeFile) => path.join(repoRoot, relativeFile)),
    ].filter((absolutePath) => fs.existsSync(absolutePath));

    const violations: string[] = [];

    for (const absolutePath of scannedFiles) {
      const content = fs.readFileSync(absolutePath, "utf-8");
      for (const pattern of PRESSURE_FEAR_PATTERNS) {
        const match = content.match(pattern);
        if (!match) continue;
        const relativePath = path.relative(repoRoot, absolutePath);
        violations.push(`${relativePath} -> "${match[0]}"`);
      }
    }

    expect(violations).toEqual([]);
  });
});
