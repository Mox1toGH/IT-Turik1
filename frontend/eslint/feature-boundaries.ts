/**
 * Local ESLint plugin enforcing the project's feature boundaries.
 *
 * These boundaries cannot be expressed as plain glob patterns, because ESLint
 * matches the import pattern and the importing file independently. A rule that
 * banned every "features" specifier would also block a feature importing its
 * own files. This rule instead resolves which feature the *current file* belongs
 * to and compares it with the feature being imported, so same-feature imports
 * stay legal and only genuine cross-feature imports are reported.
 */

import type { Rule } from 'eslint'

/**
 * Import specifiers that are legitimate from anywhere, because they are feature
 * entry points rather than feature internals.
 */
const ALLOWED_ANYWHERE: readonly RegExp[] = [/^@\/features\/[^/]+\/routes$/]

/**
 * Files allowed to import any feature, because they compose the application
 * shell rather than belonging to a feature.
 */
const SHELL_FILES: readonly RegExp[] = [
  /[\\/]src[\\/]router[\\/]/,
  /[\\/]src[\\/]App\.vue$/,
  /[\\/]src[\\/]main\.ts$/,
]

/** Matches a feature directory inside a real filesystem path. */
const FEATURE_IN_PATH = /\/src\/features\/([^/]+)/

/** Matches a feature in an `@/features/<name>` import specifier. */
const FEATURE_SPECIFIER = /^@\/features\/([^/]+)/

function toPosix(value: string): string {
  return value.replace(/\\/g, '/')
}

/** The feature a filesystem path belongs to, or null when it is outside one. */
function featureFromPath(filePath: string): string | null {
  return toPosix(filePath).match(FEATURE_IN_PATH)?.[1] ?? null
}

/** The feature an import specifier points at, or null when it targets none. */
function featureFromSpecifier(source: string): string | null {
  return source.match(FEATURE_SPECIFIER)?.[1] ?? null
}

const featureBoundaries: Rule.RuleModule = {
  meta: {
    type: 'problem',
    docs: {
      description:
        'Disallow imports that cross feature boundaries or invert the dependency direction.',
    },
    schema: [],
    messages: {
      crossFeature:
        "'{{source}}' is imported from the '{{from}}' feature by the '{{to}}' feature. " +
        'Move genuinely shared code to shared/, or re-export it from this feature.',
      sharedToFeature:
        "'{{source}}' imports from the '{{to}}' feature. " +
        'shared/ must not depend on features/; this reverses the dependency direction.',
      internalPath:
        "'{{source}}' reaches into the '{{to}}' feature's internals. " +
        "Import that feature's public surface (its routes) instead of its internal folders.",
    },
  },

  create(context) {
    const filename = toPosix(context.filename)
    const currentFeature = featureFromPath(filename)
    // Covers both the proposed shared/ layout and the existing
    // components/shared/ folder, both of which are shared by definition.
    const isShared = /\/src\/(components\/)?shared\//.test(filename)
    const isShell = SHELL_FILES.some((pattern) => pattern.test(filename))

    /**
     * @param source A resolved module specifier.
     * @param node The string literal the specifier was read from, reported on
     *   error so the editor can highlight the exact import.
     */
    function checkSource(source: string, node: { type: string }): void {
      if (ALLOWED_ANYWHERE.some((pattern) => pattern.test(source))) return

      const targetFeature = featureFromSpecifier(source)
      if (!targetFeature) return

      const data = { source, from: currentFeature ?? '(none)', to: targetFeature }

      if (isShared) {
        context.report({ node, messageId: 'sharedToFeature', data })
        return
      }

      // The shell composes features, and a feature may always import itself.
      if (isShell || !currentFeature || targetFeature === currentFeature) return

      context.report({
        node,
        messageId: source.endsWith('/routes') ? 'crossFeature' : 'internalPath',
        data,
      })
    }

    return {
      ImportDeclaration(node) {
        const { value } = node.source
        if (typeof value === 'string') checkSource(value, node.source)
      },
      ExportNamedDeclaration(node) {
        if (node.source && typeof node.source.value === 'string') {
          checkSource(node.source.value, node.source)
        }
      },
      ExportAllDeclaration(node) {
        if (node.source && typeof node.source.value === 'string') {
          checkSource(node.source.value, node.source)
        }
      },
    }
  },
}

export default {
  meta: { name: 'project-architecture' },
  rules: {
    'feature-boundaries': featureBoundaries,
  },
}