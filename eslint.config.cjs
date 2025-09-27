const js = require('@eslint/js');
const tsParser = require('@typescript-eslint/parser');

module.exports = [
  {
    files: ['**/*.js', '**/*.jsx'],
    ...js.configs.recommended,
  },
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      parser: tsParser,
    },
    plugins: {
      '@typescript-eslint': require('typescript-eslint'),
    },
    rules: {
      // Add TypeScript rules here if needed
    },
  },
];
